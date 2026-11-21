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
	var cfg := {"revision":"adapter-restore-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var original = Transit.new()
	world.add_child(original)
	check(original.configure(cfg,"restore") and original.request_journey("rider","a","b") and original.begin_tick() and original.open_boarding(),"boarding window")
	var before: Dictionary = original.pending_request("rider")
	var saved: Dictionary = original.save_snapshot()
	check(saved.ok and before.type == "boarding_requested","save in-flight request")
	var restored = Transit.new()
	world.add_child(restored)
	check(restored.restore_snapshot(cfg,saved.snapshot),"restore coordinator")
	var request: Dictionary = restored.pending_request("rider")
	check(request == before,"reconstruct pending request")
	var body := CharacterBody3D.new()
	world.add_child(body)
	var nav := NavigationAgent3D.new()
	body.add_child(nav)
	var adapter = Adapter.new()
	world.add_child(adapter)
	adapter.set_physics_process(false)
	check(adapter.configure(restored) and adapter.register_agent("rider",body,nav),"configure restored adapter")
	check(adapter.move_for_request(request,Vector3.ZERO,func(_body,_event): return true),"restart movement")
	adapter._physics_process(0.01)
	check(restored.journey("rider").state == "boarding_confirmed","complete restored request")
	check(restored.pending_request("rider").is_empty(),"acknowledged request cleared")
	print("Adapter request restore: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
