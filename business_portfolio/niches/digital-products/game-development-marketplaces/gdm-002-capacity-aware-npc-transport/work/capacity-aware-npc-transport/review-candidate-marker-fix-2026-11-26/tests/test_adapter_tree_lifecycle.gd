extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
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
	var adapter = Adapter.new()
	world.add_child(transit)
	world.add_child(adapter)
	adapter.set_physics_process(false)
	var cfg := {"revision":"tree-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var reasons := []
	var attempts := []
	adapter.movement_failed.connect(func(_id,_request,reason):
		reasons.append(reason)
		attempts.append(adapter.configure(transit))
	)
	check(transit.configure(cfg,"tree") and adapter.configure(transit) and adapter.register_agent("rider",body,navigation), "configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(), "boarding")
	var request: Dictionary = transit.pending_request("rider")
	check(adapter.move_for_request(request,Vector3(1,0,0),func(_body,_event): return false), "start movement")
	body.velocity.x = 2.0
	world.remove_child(transit)
	check(body.velocity.x == 0.0 and reasons == ["agent_or_coordinator_missing"], "removing coordinator stops movement")
	check(attempts == [false] and not adapter.configure(transit), "cannot rebind during detach or to off-tree coordinator")
	world.add_child(transit)
	check(adapter.configure(transit) and adapter.move_for_request(request,Vector3(1,0,0),func(_body,_event): return false), "rebind after coordinator returns")
	body.velocity.z = 2.0
	world.remove_child(adapter)
	check(body.velocity.z == 0.0 and reasons.size() == 2 and attempts == [false,false], "removing adapter stops movement and rejects rebind")
	check(transit.journey("rider").state == "boarding", "removal does not acknowledge journey")
	adapter.free()
	world.queue_free()
	await process_frame
	print("Navigation adapter tree lifecycle: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
