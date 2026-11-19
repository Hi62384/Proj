extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
var failures := 0
var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var nav_map := NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(nav_map,true)
	var nav_mesh := NavigationMesh.new()
	nav_mesh.vertices = PackedVector3Array([Vector3(-7,0,-10),Vector3(-7,0,10),Vector3(2,0,10),Vector3(2,0,-10)])
	nav_mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var region := NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(region,nav_mesh)
	NavigationServer3D.region_set_map(region,nav_map)
	var origin := StaticBody3D.new()
	var origin_shape := CollisionShape3D.new()
	var origin_box := BoxShape3D.new()
	origin_box.size = Vector3(6,0.4,20)
	origin_shape.shape = origin_box
	origin.add_child(origin_shape)
	origin.position = Vector3(-4.5,0,0)
	world.add_child(origin)
	var station := StaticBody3D.new()
	var station_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4,0.4,20)
	station_shape.shape = box
	station.add_child(station_shape)
	station.position = Vector3(5.9,0,0)
	world.add_child(station)
	var platform := AnimatableBody3D.new()
	var shape := CollisionShape3D.new()
	var platform_box := BoxShape3D.new()
	platform_box.size = Vector3(3,0.4,20)
	shape.shape = platform_box
	platform.add_child(shape)
	world.add_child(platform)
	var bodies := {}
	var navigations := {}
	for i in range(20):
		var body := CharacterBody3D.new()
		body.collision_layer = 2
		body.collision_mask = 1
		var body_shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		body_shape.shape = capsule
		body.add_child(body_shape)
		body.position = Vector3(-4,0.75,float(i)*0.8-7.6)
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
	var cfg := {"revision":"crowd-v1","tick_unit":"simulation_tick","stops":["origin","end"],"vehicles":[{"id":"lift","capacity":20}],"services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
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
			var target := Vector3(0,0.7,float(index)*0.8-7.6)
			var valid = func(candidate, _event): return candidate.is_on_floor() and absf(candidate.position.x) < 0.4
			if adapter.move_for_request(event,target,valid): requested += 1
	check(requested == 20,"twenty adapter requests")
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
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"travel tick")
	check(transit.begin_tick(),"arrival")
	for i in range(90):
		await physics_frame
		for body in bodies.values():
			body.velocity.x = 2.0
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
	var alighted := 0
	for event in events.duplicate():
		if event.type == "alighting_requested":
			check(bodies[event.agent].is_on_floor() and bodies[event.agent].position.x > 4.2,"passenger reached station " + event.agent)
			if transit.acknowledge_alighting(event.agent,"lift",event.details.token,event.id): alighted += 1
	check(alighted == 20,"twenty passengers alighted")
	for id in bodies:
		check(transit.journey(id).state == "completed","completed " + id)
	print("Navigation adapter, 20 collision-platform passengers: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	NavigationServer3D.free_rid(region)
	NavigationServer3D.free_rid(nav_map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
