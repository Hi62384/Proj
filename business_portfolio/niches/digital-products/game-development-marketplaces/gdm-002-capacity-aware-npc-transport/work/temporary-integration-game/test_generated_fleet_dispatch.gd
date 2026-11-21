extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)

func vehicle(world: Node, at: Vector3) -> AnimatableBody3D:
	var body := AnimatableBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(2, 0.4, 2)
	shape.shape = box
	body.add_child(shape)
	body.position = at
	world.add_child(body)
	return body

func _initialize() -> void:
	call_deferred("run")

func run_layout(seed_value: int, case_index: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var center := Vector3(rng.randf_range(-18.0, 18.0), 0, rng.randf_range(-18.0, 18.0))
	var base_angle := rng.randf_range(-PI, PI)
	var extent := rng.randf_range(5.5, 7.0)
	var world := Node3D.new()
	root.add_child(world)
	var dispatcher: Node = Dispatcher.new()
	var junctions: Array[Vector3] = [center]
	dispatcher.junctions = junctions
	# Acute crossings with 2-unit square footprints need wider clearance than the default.
	dispatcher.reservation_radius = 4.0
	world.add_child(dispatcher)
	var ids: Array[String] = []
	var bodies: Array[AnimatableBody3D] = []
	var routes: Array[Array] = []
	var arrivals := {}
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	for vehicle_index in range(3):
		var angle := base_angle + float(vehicle_index) * PI / 3.0
		var direction := Vector3(cos(angle), 0, sin(angle))
		var body := vehicle(world, center - direction * extent)
		var id := "fleet-%d-%d" % [case_index, vehicle_index]
		var route: Array[Vector3] = [body.position, center + direction * extent]
		var priority := rng.randi_range(1, 6)
		var speed := rng.randf_range(2.2, 3.8)
		check(dispatcher.register_vehicle(id, body, route, speed, priority), "register generated fleet vehicle " + str(case_index) + ":" + str(vehicle_index))
		ids.append(id)
		bodies.append(body)
		routes.append(route)
	var launch_delays: Array[int] = [0, rng.randi_range(1, 18), rng.randi_range(1, 30)]
	var launched := [false, false, false]
	var overlap := false
	for frame in range(1800):
		for vehicle_index in range(3):
			if not launched[vehicle_index] and frame >= launch_delays[vehicle_index]:
				check(dispatcher.dispatch(ids[vehicle_index]), "dispatch generated fleet vehicle " + str(case_index) + ":" + str(vehicle_index))
				launched[vehicle_index] = true
		await physics_frame
		for i in range(3):
			for j in range(i + 1, 3):
				if absf(bodies[i].position.x - bodies[j].position.x) < 2.0 and absf(bodies[i].position.z - bodies[j].position.z) < 2.0:
					overlap = true
		if arrivals.size() == 3:
			break
	check(not overlap, "generated three-vehicle collision bounds remain separate " + str(case_index))
	for vehicle_index in range(3):
		check(arrivals.has(ids[vehicle_index]), "generated fleet arrival " + str(case_index) + ":" + str(vehicle_index))
		check(bodies[vehicle_index].position.distance_to(routes[vehicle_index][1]) < 0.03, "generated fleet endpoint " + str(case_index) + ":" + str(vehicle_index))
	world.queue_free()
	await process_frame

func run() -> void:
	var case_index := 0
	for seed_value in [29, 67, 113, 197, 263, 349, 457, 557]:
		await run_layout(seed_value, case_index)
		case_index += 1
	print("Temporary game generated fleet dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", case_index, " layouts, three vehicles per junction, staggered launch)")
	quit(0 if failures == 0 else 1)
