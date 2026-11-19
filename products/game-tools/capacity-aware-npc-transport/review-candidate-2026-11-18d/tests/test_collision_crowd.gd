extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
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
	for i in range(4):
		var body := CharacterBody3D.new()
		var body_shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		body_shape.shape = capsule
		body.add_child(body_shape)
		body.position = Vector3(0,0.75,float(i)*0.8-1.2)
		world.add_child(body)
		bodies["npc%d" % i] = body
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var cfg := {"revision":"crowd-v1","tick_unit":"simulation_tick","stops":["origin","end"],"vehicles":[{"id":"lift","capacity":4}],"services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"crowd"),"configure")
	for id in bodies:
		check(transit.request_journey(id,"origin","end"),"request " + id)
	for i in range(30):
		await physics_frame
		for body in bodies.values():
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
	check(transit.begin_tick() and transit.open_boarding(),"open boarding")
	var boarded := 0
	for event in events.duplicate():
		if event.type == "boarding_requested":
			check(bodies[event.agent].is_on_floor(),"physical contact " + event.agent)
			if transit.acknowledge_boarding(event.agent,"lift",event.details.token,event.id): boarded += 1
	check(boarded == 4,"four passengers boarded")
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
	check(alighted == 4,"four passengers alighted")
	for id in bodies:
		check(transit.journey(id).state == "completed","completed " + id)
	print("Collision platform, four passengers: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
