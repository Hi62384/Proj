extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
var failures := 0
var sampling := true
var timings: Array[float] = []
var started_usec := 0
func sample_physics() -> void:
	while sampling:
		await physics_frame
		timings.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0)

var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	started_usec = Time.get_ticks_usec()
	sample_physics()
	var world := Node3D.new()
	root.add_child(world)
	var nav_map := NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(nav_map,true)
	var nav_mesh := NavigationMesh.new()
	nav_mesh.vertices = PackedVector3Array([Vector3(-7,0,-3),Vector3(-7,0,3),Vector3(8,0,3),Vector3(8,0,-3)])
	nav_mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var region := NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(region,nav_mesh)
	NavigationServer3D.region_set_map(region,nav_map)
	var origin := StaticBody3D.new()
	var origin_shape := CollisionShape3D.new()
	var origin_box := BoxShape3D.new()
	origin_box.size = Vector3(6,0.4,5)
	origin_shape.shape = origin_box
	origin.add_child(origin_shape)
	origin.position = Vector3(-4.5,0,0)
	world.add_child(origin)
	var station := StaticBody3D.new()
	var station_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4,0.4,5)
	station_shape.shape = box
	station.add_child(station_shape)
	station.position = Vector3(5.9,0,0)
	world.add_child(station)
	var platform := AnimatableBody3D.new()
	var shape := CollisionShape3D.new()
	var platform_box := BoxShape3D.new()
	platform_box.size = Vector3(3,0.4,5)
	shape.shape = platform_box
	platform.add_child(shape)
	world.add_child(platform)
	var bodies := {}
	var navigations := {}
	for i in range(4):
		var body := CharacterBody3D.new()
		var body_shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		body_shape.shape = capsule
		body.add_child(body_shape)
		body.position = Vector3(-4,0.75,float(i)*0.8-1.2)
		world.add_child(body)
		bodies["npc%d" % i] = body
		var navigation := NavigationAgent3D.new()
		body.add_child(navigation)
		navigation.set_navigation_map(nav_map)
		navigation.path_desired_distance = 0.8
		navigation.target_desired_distance = 0.8
		navigations["npc%d" % i] = navigation
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var cfg := {"revision":"crowd-v1","tick_unit":"simulation_tick","stops":["origin","end"],"vehicles":[{"id":"lift","capacity":4}],"services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"crowd"),"configure")
	var adapter = Adapter.new()
	world.add_child(adapter)
	check(adapter.configure(transit),"configure adapter")
	for id in bodies:
		check(adapter.register_agent(id,bodies[id],navigations[id]),"register " + id)
	for id in bodies:
		check(transit.request_journey(id,"origin","end"),"request " + id)
	for i in range(30):
		await physics_frame
		for body in bodies.values():
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
	check(transit.begin_tick() and transit.open_boarding(),"open boarding")
	var requested := 0
	for event in events.duplicate():
		if event.type == "boarding_requested":
			var index := int(event.agent.substr(3))
			var target := Vector3(0,0.7,float(index)*0.8-1.2)
			var valid = func(candidate, _event): return candidate.is_on_floor() and absf(candidate.position.x) < 0.4
			if adapter.move_for_request(event,target,valid): requested += 1
	check(requested == 4,"four adapter requests")
	for i in range(240):
		await physics_frame
	for id in bodies:
		check(transit.journey(id).state == "boarding_confirmed","adapter boarded " + id)
	check(transit.finish_tick(),"departure")
	for i in range(120):
		await physics_frame
		platform.position.x += 0.02
		for body in bodies.values():
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
	for id in bodies:
		check(bodies[id].is_on_floor() and absf(bodies[id].position.x-platform.position.x) < 0.5,"passenger rode " + id)
	var obstacle := StaticBody3D.new()
	var obstacle_shape := CollisionShape3D.new()
	var obstacle_box := BoxShape3D.new()
	obstacle_box.size = Vector3(0.4,2,0.6)
	obstacle_shape.shape = obstacle_box
	obstacle.add_child(obstacle_shape)
	obstacle.position = Vector3(3.5,1,1.2)
	world.add_child(obstacle)
	check(transit.set_service_enabled("out",false),"interrupt vehicle")
	var recoveries := 0
	for id in bodies:
		var request: Dictionary = transit.pending_request(id)
		check(request.get("type") == "recovery_requested","recovery request " + id)
		var index := int(id.substr(3))
		var target := Vector3(5,0.7,float(index)*0.8-1.2)
		var valid = func(candidate, _event): return candidate.is_on_floor() and candidate.position.x > 4.2
		if adapter.move_for_request(request,target,valid,"end",2.0,0.4,2.0): recoveries += 1
	check(recoveries == 4,"start four recoveries")
	for i in range(150):
		await physics_frame
	for id in ["npc0","npc1","npc2"]:
		check(transit.journey(id).state == "completed","unblocked recovered " + id)
	check(transit.journey("npc3").state == "stranded","blocked passenger remains stranded")
	check(transit.inspect_vehicle("lift").ledger.aboard.size() == 1,"blocked passenger retains seat")
	var saved: Dictionary = transit.save_snapshot()
	check(saved.ok,"save mixed completed and stranded passengers")
	adapter.cancel_movement("npc3")
	adapter.queue_free()
	var restored = Transit.new()
	world.add_child(restored)
	check(restored.restore_snapshot(cfg,saved.snapshot),"restore mixed recovery state")
	transit.queue_free()
	transit = restored
	var replacement = Adapter.new()
	world.add_child(replacement)
	adapter = replacement
	check(adapter.configure(transit) and adapter.register_agent("npc3",bodies["npc3"],navigations["npc3"]),"reconnect stranded passenger")
	for id in ["npc0","npc1","npc2"]:
		check(transit.journey(id).state == "completed","completed state survives restore " + id)
	check(transit.journey("npc3").state == "stranded" and transit.inspect_vehicle("lift").ledger.aboard.size() == 1,"stranded seat survives restore")
	obstacle.queue_free()
	await physics_frame
	var pending: Dictionary = transit.pending_request("npc3")
	check(adapter.move_for_request(pending,Vector3(5,0.7,1.2),func(candidate,_event): return candidate.is_on_floor() and candidate.position.x > 4.2,"end"),"retry blocked recovery")
	for i in range(180):
		await physics_frame
	for id in bodies:
		check(bodies[id].is_on_floor() and bodies[id].position.x > 4.2,"safe physical stop " + id)
		check(transit.journey(id).state == "completed","recovered " + id)
	sampling = false
	timings.sort()
	var total := 0.0
	for value in timings: total += value
	var count := timings.size()
	var measurement := {"fixture":"four-passenger blocked recovery with coordinator restore", "physics_process_ms_mean":total / count if count else -1.0, "physics_process_ms_p95":timings[mini(count - 1,int(count * 0.95))] if count else -1.0, "physics_process_ms_max":timings[count - 1] if count else -1.0, "samples":count, "elapsed_seconds":float(Time.get_ticks_usec() - started_usec) / 1000000.0, "failures":failures}
	print("MEASUREMENT_JSON ",JSON.stringify(measurement))
	print("Temporary game blocked crowd recovery restore: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	NavigationServer3D.free_rid(region)
	NavigationServer3D.free_rid(nav_map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
