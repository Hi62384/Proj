extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var sampling := true
var timings: Array[float] = []
var start_usec := 0
func sample_physics() -> void:
	while sampling:
		await physics_frame
		timings.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0)

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		if failures <= 20: printerr("FAIL: ",label)
func surface(size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var node: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	node.add_child(shape)
	node.position = position
	return node
func walk(group: Dictionary, speed: float, frames: int) -> void:
	for i in range(frames):
		await physics_frame
		for body in group.values():
			body.velocity.x = speed
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
func ride(platform: Node3D, group: Dictionary, frames: int) -> void:
	for i in range(frames):
		await physics_frame
		platform.position.x += 0.02
		for body in group.values():
			body.velocity.x = 0.0
			body.velocity.y -= 9.8/60.0
			body.move_and_slide()
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	start_usec = Time.get_ticks_usec()
	sample_physics()
	var world := Node3D.new()
	root.add_child(world)
	var first = surface(Vector3(3,0.4,20),Vector3.ZERO,true)
	var second = surface(Vector3(3,0.4,20),Vector3(7.5,0,0),true)
	world.add_child(first)
	world.add_child(second)
	world.add_child(surface(Vector3(2.2,0.4,20),Vector3(-2.5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,20),Vector3(5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,20),Vector3(12.5,0,0),false))
	var groups := [{},{},{},{},{},{},{}]
	for i in range(20):
		var body := CharacterBody3D.new()
		body.collision_layer = 2
		body.collision_mask = 1
		var shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		shape.shape = capsule
		body.add_child(shape)
		body.position = Vector3(0 if i < 3 else -2.5,0.75,float(i)*0.8-7.6)
		world.add_child(body)
		groups[int(i / 3)]["npc%d" % i] = body
	var transit = Transit.new()
	world.add_child(transit)
	var cfg := {"revision":"staggered-v1","tick_unit":"simulation_tick","stops":["a","hub","end"],"vehicles":[{"id":"v1","capacity":3},{"id":"v2","capacity":3}],"services":[{"id":"first","vehicle":"v1","from":"a","to":"hub","period":10,"offset":0,"duration":2,"enabled":true},{"id":"second","vehicle":"v2","from":"hub","to":"end","period":10,"offset":2,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"staggered"),"configure")
	for group in groups:
		for id in group: check(transit.request_journey(id,"a","end"),"request " + id)
	for group in groups:
		await walk(group,0.0,30)
	for batch in range(7):
		var group: Dictionary = groups[batch]
		check(transit.begin_tick() and transit.open_boarding(),"first boarding window")
		if batch == 0:
			for later in range(1,7):
				for id in groups[later]: check(transit.journey(id).state == "queued","later cohort waits " + id)
		else:
			await walk(group,2.0,75)
		for id in group:
			var e: Dictionary = transit.pending_request(id)
			check(group[id].is_on_floor() and absf(group[id].position.x-first.position.x)<0.5,"first platform contact " + id)
			check(e.get("type") == "boarding_requested" and transit.acknowledge_boarding(id,"v1",e.details.token,e.id),"first boarding " + id)
		check(transit.finish_tick(),"first departure")
		await ride(first,group,120)
		for id in group: check(group[id].is_on_floor() and absf(group[id].position.x-first.position.x)<0.5,"first ride " + id)
		check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"first arrival")
		await walk(group,2.0,75)
		for id in group:
			var e: Dictionary = transit.pending_request(id)
			check(group[id].is_on_floor() and group[id].position.x > 4.3 and group[id].position.x < 5.8,"shared station " + id)
			check(e.get("type") == "alighting_requested" and transit.acknowledge_alighting(id,"v1",e.details.token,e.id),"first exit " + id)
		check(transit.open_boarding(),"second boarding window")
		await walk(group,2.0,78)
		for id in group:
			var e: Dictionary = transit.pending_request(id)
			check(group[id].is_on_floor() and absf(group[id].position.x-second.position.x)<0.5,"second platform contact " + id)
			check(e.get("type") == "boarding_requested" and transit.acknowledge_boarding(id,"v2",e.details.token,e.id),"second boarding " + id)
		check(transit.finish_tick(),"second departure")
		await ride(second,group,120)
		for id in group: check(group[id].is_on_floor() and absf(group[id].position.x-second.position.x)<0.5,"second ride " + id)
		check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"second arrival")
		await walk(group,2.0,90)
		for id in group:
			var e: Dictionary = transit.pending_request(id)
			check(group[id].is_on_floor() and group[id].position.x > 11.5,"end station " + id)
			check(e.get("type") == "alighting_requested" and transit.acknowledge_alighting(id,"v2",e.details.token,e.id),"final exit " + id)
			check(transit.journey(id).state == "completed","completed " + id)
		if batch < 6:
			for i in range(120):
				await physics_frame
				first.position.x -= 0.02
				second.position.x -= 0.02
			check(absf(first.position.x)<0.1 and absf(second.position.x-7.5)<0.1,"empty returns complete")
			check(transit.open_boarding() and transit.finish_tick(),"finish arrival tick")
			for i in range(5):
				check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"wait for next departure")
	sampling = false
	timings.sort()
	var total := 0.0
	for value in timings: total += value
	var size := timings.size()
	var result := {"fixture":"20-passenger staggered scripted two-platform transfer", "physics_process_ms_mean": total / size if size else -1.0, "physics_process_ms_p95": timings[mini(size - 1, int(size * 0.95))] if size else -1.0, "physics_process_ms_max": timings[size - 1] if size else -1.0, "samples":size, "elapsed_seconds":float(Time.get_ticks_usec() - start_usec) / 1000000.0, "failures":failures}
	print("MEASUREMENT_JSON ",JSON.stringify(result))
	print("20-agent staggered physical transfer: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; 20 agents; capacity 3; no agent collisions)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
