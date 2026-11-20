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

func run() -> void:
	var cases := [
		{"center":Vector3(0, 0, 0), "angle":0.0},
		{"center":Vector3(12, 0, -7), "angle":PI / 6.0},
		{"center":Vector3(-9, 0, 14), "angle":PI / 4.0},
		{"center":Vector3(21, 0, 11), "angle":PI / 3.0},
		{"center":Vector3(-18, 0, -13), "angle":PI / 2.0},
		{"center":Vector3(6, 0, 23), "angle":-PI / 4.0}
	]
	for index in cases.size():
		var layout: Dictionary = cases[index]
		var center: Vector3 = layout.center
		var angle: float = layout.angle
		var direction := Vector3(cos(angle), 0, sin(angle))
		var crossing := Vector3(-sin(angle), 0, cos(angle))
		var world := Node3D.new()
		root.add_child(world)
		var first := vehicle(world, center - direction * 4.0)
		var second := vehicle(world, center - crossing * 4.0)
		var dispatcher: Node = Dispatcher.new()
		world.add_child(dispatcher)
		var junctions: Array[Vector3] = [center]
		dispatcher.junctions = junctions
		var first_id := "first-" + str(index)
		var second_id := "second-" + str(index)
		var first_priority := 1 if index % 2 == 0 else 2
		var second_priority := 2 if index % 2 == 0 else 1
		var arrivals := {}
		dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
		var first_route: Array[Vector3] = [first.position, center + direction * 4.0]
		var second_route: Array[Vector3] = [second.position, center + crossing * 4.0]
		check(dispatcher.register_vehicle(first_id, first, first_route, 3.0, first_priority), "register first route for layout " + str(index))
		check(dispatcher.register_vehicle(second_id, second, second_route, 3.0, second_priority), "register crossing route for layout " + str(index))
		check(dispatcher.dispatch(first_id) and dispatcher.dispatch(second_id), "dispatch generated layout " + str(index))
		var overlap := false
		for _frame in range(480):
			await physics_frame
			if absf(first.position.x - second.position.x) < 2.0 and absf(first.position.z - second.position.z) < 2.0:
				overlap = true
			if arrivals.size() == 2:
				break
		check(not overlap, "physical bounds stay separate for layout " + str(index))
		check(arrivals.has(first_id) and arrivals.has(second_id), "both crossing routes finish for layout " + str(index))
		check(first.position.distance_to(first_route[1]) < 0.03 and second.position.distance_to(second_route[1]) < 0.03, "platforms stop at assigned endpoints for layout " + str(index))
		world.queue_free()
		await process_frame
	print("Temporary game generated junction layouts: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; six translated and rotated crossings)")
	quit(0 if failures == 0 else 1)
