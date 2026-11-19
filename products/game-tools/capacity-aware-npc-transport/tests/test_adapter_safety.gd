extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var body := CharacterBody3D.new()
	world.add_child(body)
	var navigation := NavigationAgent3D.new()
	body.add_child(navigation)
	var transit = Transit.new()
	world.add_child(transit)
	var adapter = Adapter.new()
	world.add_child(adapter)
	adapter.set_physics_process(false)
	var cfg := {"revision":"adapter-safety-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var events := []
	var failures_seen := []
	transit.transit_event.connect(func(e): events.append(e))
	adapter.movement_failed.connect(func(_agent,_id,reason): failures_seen.append(reason))
	check(transit.configure(cfg,"adapter") and adapter.configure(transit) and adapter.register_agent("rider",body,navigation),"configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(),"boarding window")
	var event: Dictionary = {}
	for item in events:
		if item.type == "boarding_requested": event = item
	check(not event.is_empty(),"request received")
	check(adapter.move_for_request(event,Vector3.ZERO,func(_body,_event): return false,"",2.0,0.4,0.1),"start unverified move")
	adapter._physics_process(0.2)
	check(failures_seen == ["timeout"],"timeout reported")
	check(transit.journey("rider").state == "boarding","unverified arrival did not acknowledge")
	check(not adapter.move_for_request(event,Vector3(NAN,0,0),func(_body,_event): return true),"nonfinite target rejected")
	check(adapter.move_for_request(event,Vector3.ZERO,func(_body,_event):
		adapter.cancel_movement("rider")
		return true
	),"start reentrant cancellation")
	adapter._physics_process(0.01)
	check(transit.journey("rider").state == "boarding","cancelled callback did not acknowledge")
	check(transit.finish_tick(),"close boarding")
	check(transit.journey("rider").state == "queued","claim expired")
	check(not adapter.move_for_request(event,Vector3.ZERO,func(_body,_event): return true),"stale request rejected before movement")
	check(failures_seen == ["timeout"],"no movement started for stale request")
	check(transit.journey("rider").state == "queued","stale request leaves journey queued")
	print("Navigation adapter safety: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
