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
	var center := Vector3(rng.randf_range(-20.0, 20.0), 0, rng.randf_range(-20.0, 20.0))
	var angle := rng.randf_range(-PI, PI)
	var direction := Vector3(cos(angle), 0, sin(angle))
	var cross_direction := Vector3(-direction.z, 0, direction.x)
	var extent := rng.randf_range(4.0, 7.0)
	var world := Node3D.new()
	root.add_child(world)
	var first := vehicle(world, center - direction * extent)
	var second := vehicle(world, center - cross_direction * extent)
	var dispatcher: Node = Dispatcher.new()
	var junctions: Array[Vector3] = [center]
	dispatcher.junctions = junctions
	world.add_child(dispatcher)
	var arrivals := {}
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	var first_id := "seed-%d-a" % case_index
	var second_id := "seed-%d-b" % case_index
	var first_route: Array[Vector3] = [first.position, center + direction * extent]
	var second_route: Array[Vector3] = [second.position, center + cross_direction * extent]
	var first_priority := rng.randi_range(1, 5)
	var second_priority := rng.randi_range(1, 5)
	check(dispatcher.register_vehicle(first_id, first, first_route, rng.randf_range(2.0, 4.0), first_priority), "register first generated route " + str(case_index))
	check(dispatcher.register_vehicle(second_id, second, second_route, rng.randf_range(2.0, 4.0), second_priority), "register crossing generated route " + str(case_index))
	check(dispatcher.dispatch(first_id) and dispatcher.dispatch(second_id), "dispatch generated pair " + str(case_index))
	var overlap := false
	for _frame in range(1200):
		await physics_frame
		if absf(first.position.x - second.position.x) < 2.0 and absf(first.position.z - second.position.z) < 2.0:
			overlap = true
		if arrivals.size() == 2:
			break
	check(not overlap, "generated platform bounds stay separate " + str(case_index))
	check(arrivals.has(first_id) and arrivals.has(second_id), "both generated routes finish " + str(case_index))
	check(first.position.distance_to(first_route[1]) < 0.03 and second.position.distance_to(second_route[1]) < 0.03, "generated endpoints reached " + str(case_index))
	world.queue_free()
	await process_frame

func run() -> void:
	var layouts := 0
	for seed_value in [17, 43, 89, 131, 211, 307, 401, 503]:
		await run_layout(seed_value, layouts)
		layouts += 1
	print("Temporary game seeded physical dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", layouts, " seeded crossings, randomized geometry/speed/priority)")
	quit(0 if failures == 0 else 1)
