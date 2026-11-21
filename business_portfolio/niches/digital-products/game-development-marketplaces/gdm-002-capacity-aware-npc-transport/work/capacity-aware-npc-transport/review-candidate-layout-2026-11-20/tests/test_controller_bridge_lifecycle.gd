extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node.new()
	root.add_child(world)
	var cfg := {"revision":"bridge-lifecycle-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":3,"offset":0,"duration":1,"enabled":true}]}
	var old = Transit.new()
	var bridge = Bridge.new()
	world.add_child(old)
	world.add_child(bridge)
	check(old.configure(cfg,"same") and bridge.configure(old),"configure")
	var requests := []
	var withdrawals := []
	bridge.movement_requested.connect(func(e): requests.append(e))
	bridge.request_withdrawn.connect(func(agent,id,reason): withdrawals.append([agent,id,reason]))
	check(old.request_journey("rider","a","b") and old.begin_tick() and old.open_boarding(),"boarding")
	var first: Dictionary = requests.back()
	var saved: Dictionary = old.save_snapshot()
	var replacement = Transit.new()
	world.add_child(replacement)
	check(replacement.restore_snapshot(cfg,saved.snapshot),"restore same identifiers")
	check(not bridge.complete_movement(first,func(_event):
		bridge.detach()
		check(bridge.configure(replacement) and bridge.refresh_request("rider"),"rebind within callback")
		return true
	),"old completion cannot affect new coordinator")
	check(replacement.journey("rider").state == "boarding","new coordinator not acknowledged")
	check(withdrawals.size() == 1 and withdrawals[0][2] == "detached","detach withdraws movement")
	check(bridge.complete_movement(requests.back(),func(_event): return true),"current coordinator can acknowledge")
	check(replacement.finish_tick() and replacement.set_service_enabled("s",false),"disable onboard service")
	var recovery: Dictionary = requests.back()
	var refresh_on_withdraw = func(agent,_id,reason):
		if reason == "superseded": bridge.refresh_request(agent)
	bridge.request_withdrawn.connect(refresh_on_withdraw)
	var count := requests.size()
	check(replacement.set_service_enabled("s",true),"refresh recovery")
	check(requests.size() == count+1 and requests.back().id != recovery.id,"reentrant refresh emits once")
	var pending_id: String = requests.back().id
	replacement.queue_free()
	await process_frame
	check(withdrawals.back() == ["rider",pending_id,"detached"],"coordinator removal withdraws request")
	var next = Transit.new()
	world.add_child(next)
	check(next.configure(cfg,"next") and bridge.configure(next),"reconfigure after removal")
	check(next.request_journey("last","a","b") and next.begin_tick() and next.open_boarding(),"request before bridge removal")
	var bridge_exit_id: String = requests.back().id
	var exit_rebind := []
	bridge.request_withdrawn.connect(func(agent,_id,_reason):
		if agent == "last": exit_rebind.append(bridge.configure(next))
	)
	bridge.queue_free()
	await process_frame
	check(withdrawals.back() == ["last",bridge_exit_id,"detached"],"bridge removal withdraws movement")
	check(exit_rebind == [false],"bridge cannot rebind while exiting")
	check(next.journey("last").state == "boarding","bridge removal does not acknowledge or release claim")
	check(next.finish_tick() and next.journey("last").state == "queued","claim expires normally after bridge removal")
	var another = Bridge.new()
	var fresh = Transit.new()
	world.add_child(another)
	world.add_child(fresh)
	check(fresh.configure(cfg,"fresh") and another.configure(fresh), "configure explicit detach")
	check(fresh.request_journey("detach-rider","a","b") and fresh.begin_tick() and fresh.open_boarding(), "pending request for detach")
	var rebind_attempts := []
	another.request_withdrawn.connect(func(_agent,_id,_reason):
		rebind_attempts.append(another.configure(fresh))
		another.detach()
	)
	another.detach()
	check(rebind_attempts == [false], "callback cannot reconnect during detach")
	check(another.configure(fresh), "reconnect succeeds after detach")
	print("Controller bridge lifecycle: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
