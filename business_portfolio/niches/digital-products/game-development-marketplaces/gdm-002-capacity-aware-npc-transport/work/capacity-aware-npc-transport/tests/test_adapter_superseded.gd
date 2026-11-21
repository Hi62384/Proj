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
	var cfg := {"revision":"supersede-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var failed := []
	adapter.movement_failed.connect(func(_agent,id,reason): failed.append([id,reason]))
	check(transit.configure(cfg,"supersede") and adapter.configure(transit) and adapter.register_agent("rider",body,navigation),"configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(),"first boarding")
	var first: Dictionary = transit.pending_request("rider")
	check(adapter.move_for_request(first,Vector3(1,0,0),func(_body,_event): return false),"start first movement")
	body.velocity.x = 2.0
	check(transit.finish_tick(),"expire first request")
	check(failed == [[first.id,"superseded"]] and body.velocity.x == 0.0,"expired movement stopped")
	check(not adapter.move_for_request(first,Vector3.ZERO,func(_body,_event): return true),"reject expired request before motion")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"advance to next departure")
	check(transit.begin_tick() and transit.open_boarding(),"second boarding")
	var second: Dictionary = transit.pending_request("rider")
	check(transit.acknowledge_boarding("rider","v",second.details.token,second.id) and transit.finish_tick(),"board and depart")
	check(transit.set_service_enabled("s",false),"interrupt")
	var recovery: Dictionary = transit.pending_request("rider")
	check(adapter.move_for_request(recovery,Vector3(1,0,0),func(_body,_event): return false,"a"),"start recovery")
	check(transit.set_service_enabled("s",true),"refresh recovery")
	var replacement: Dictionary = transit.pending_request("rider")
	check(replacement.id != recovery.id and failed.back() == [recovery.id,"superseded"],"changed request stopped")
	check(not adapter.move_for_request(recovery,Vector3.ZERO,func(_body,_event): return true,"a"),"reject old recovery")
	check(adapter.move_for_request(replacement,Vector3.ZERO,func(_body,_event): return true,"a"),"accept current recovery")
	adapter._physics_process(0.01)
	check(transit.journey("rider").state == "queued","current recovery completed")
	print("Superseded movement handling: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
