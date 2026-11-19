extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		if failures <= 20: printerr("FAIL: ",label)
func make_surface(size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var surface: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	surface.add_child(shape)
	surface.position = position
	return surface
func walk(bodies: Dictionary, speed: float, frames: int) -> void:
	for i in range(frames):
		await physics_frame
		for body in bodies.values():
			body.velocity.x = speed
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
func ride(platform: Node3D, bodies: Dictionary, frames: int) -> void:
	for i in range(frames):
		await physics_frame
		platform.position.x += 0.02
		for body in bodies.values():
			body.velocity.x = 0.0
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var first = make_surface(Vector3(3,0.4,20),Vector3.ZERO,true)
	var second = make_surface(Vector3(3,0.4,20),Vector3(7.5,0,0),true)
	world.add_child(first)
	world.add_child(second)
	world.add_child(make_surface(Vector3(2.2,0.4,20),Vector3(5,0,0),false))
	world.add_child(make_surface(Vector3(2.2,0.4,20),Vector3(12.5,0,0),false))
	var bodies := {}
	for i in range(20):
		var id := "npc%02d" % i
		var body := CharacterBody3D.new()
		body.collision_layer = 2
		body.collision_mask = 1
		var shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		shape.shape = capsule
		body.add_child(shape)
		body.position = Vector3(0,0.75,float(i)*0.8-7.6)
		world.add_child(body)
		bodies[id] = body
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var cfg := {"revision":"transfer20-v1","tick_unit":"simulation_tick","stops":["a","hub","end"],"vehicles":[{"id":"v1","capacity":20},{"id":"v2","capacity":20}],"services":[{"id":"first","vehicle":"v1","from":"a","to":"hub","period":10,"offset":0,"duration":2,"enabled":true},{"id":"second","vehicle":"v2","from":"hub","to":"end","period":10,"offset":2,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"transfer20"),"configure")
	for id in bodies: check(transit.request_journey(id,"a","end"),"request " + id)
	await walk(bodies,0.0,30)
	for id in bodies: check(bodies[id].is_on_floor(),"first contact " + id)
	check(transit.begin_tick() and transit.open_boarding(),"first boarding")
	for id in bodies:
		var e: Dictionary = transit.pending_request(id)
		check(e.get("type") == "boarding_requested" and transit.acknowledge_boarding(id,"v1",e.details.token,e.id),"board first " + id)
	check(transit.finish_tick(),"first departure")
	await ride(first,bodies,120)
	for id in bodies: check(bodies[id].is_on_floor() and absf(bodies[id].position.x-first.position.x)<0.5,"first ride " + id)
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"first arrival")
	await walk(bodies,2.0,75)
	for id in bodies:
		var e: Dictionary = transit.pending_request(id)
		check(bodies[id].is_on_floor() and bodies[id].position.x > 4.3 and bodies[id].position.x < 5.8,"shared station " + id)
		check(e.get("type") == "alighting_requested" and transit.acknowledge_alighting(id,"v1",e.details.token,e.id),"exit first " + id)
	check(transit.open_boarding(),"second boarding")
	await walk(bodies,2.0,78)
	for id in bodies:
		var e: Dictionary = transit.pending_request(id)
		check(bodies[id].is_on_floor() and absf(bodies[id].position.x-second.position.x)<0.5,"second contact " + id)
		check(e.get("type") == "boarding_requested" and transit.acknowledge_boarding(id,"v2",e.details.token,e.id),"board second " + id)
	check(transit.finish_tick(),"second departure")
	await ride(second,bodies,120)
	for id in bodies: check(bodies[id].is_on_floor() and absf(bodies[id].position.x-second.position.x)<0.5,"second ride " + id)
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"second arrival")
	await walk(bodies,2.0,90)
	for id in bodies:
		var e: Dictionary = transit.pending_request(id)
		check(bodies[id].is_on_floor() and bodies[id].position.x > 11.5,"end station " + id)
		check(e.get("type") == "alighting_requested" and transit.acknowledge_alighting(id,"v2",e.details.token,e.id),"final exit " + id)
		check(transit.journey(id).state == "completed","completed " + id)
	print("20-agent two-platform collision transfer: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; agent-to-agent collision disabled)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
