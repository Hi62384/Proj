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
	var nav := NavigationAgent3D.new()
	body.add_child(nav)
	var transit = Transit.new()
	world.add_child(transit)
	var adapter = Adapter.new()
	world.add_child(adapter)
	adapter.set_physics_process(false)
	var cfg := {"revision":"deleted-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var failed := []
	adapter.movement_failed.connect(func(_agent,_id,reason): failed.append(reason))
	check(transit.configure(cfg,"deleted") and adapter.configure(transit) and adapter.register_agent("rider",body,nav),"configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(),"open boarding")
	var request: Dictionary = transit.pending_request("rider")
	check(adapter.move_for_request(request,Vector3(1,0,0),func(_body,_event): return true),"start movement")
	body.queue_free()
	await process_frame
	adapter._physics_process(0.1)
	check(failed == ["agent_or_coordinator_missing"],"missing body reported")
	check(transit.journey("rider").state == "boarding","missing body not acknowledged")
	check(transit.finish_tick() and transit.journey("rider").state == "queued","unclaimed seat expires at departure")
	adapter.unregister_agent("rider")
	check(transit.cancel_journey("rider") and transit.journey("rider").state == "cancelled","game explicitly cancels remaining journey")
	transit.queue_free()
	await process_frame
	check(not adapter.move_for_request(request,Vector3.ZERO,func(_body,_event): return true),"deleted coordinator rejects movement")
	print("Deleted movement body: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
