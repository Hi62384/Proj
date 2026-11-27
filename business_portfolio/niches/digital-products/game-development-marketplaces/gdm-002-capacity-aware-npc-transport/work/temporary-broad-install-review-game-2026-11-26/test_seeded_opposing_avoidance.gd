extends SceneTree
const Npc = preload("res://npc.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run_case(seed_value: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var angle := rng.randf_range(-PI, PI)
	var direction := Vector3(cos(angle), 0, sin(angle))
	var world := Node3D.new()
	root.add_child(world)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(12, 0.4, 12)
	floor_shape.shape = floor_box
	floor_body.add_child(floor_shape)
	floor_body.position.y = -0.2
	world.add_child(floor_body)
	var walkers: Array[CharacterBody3D] = []
	var arrived := {}
	for index in range(2):
		var npc: CharacterBody3D = Npc.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.28
		capsule.height = 1.0
		var shape := CollisionShape3D.new()
		shape.shape = capsule
		npc.add_child(shape)
		npc.position = direction * (-2.0 if index == 0 else 2.0) + Vector3(0,0.5,0)
		npc.collision_layer = 2
		npc.collision_mask = 3
		npc.cooperative_avoidance = true
		npc.extended_avoidance = true
		npc.avoidance_priority = index + 1
		npc.reached.connect(func(id: String): arrived[id] = true)
		world.add_child(npc)
		walkers.append(npc)
	walkers[0].walk_to(direction * 2.0 + Vector3(0,0.5,0), "first")
	walkers[1].walk_to(direction * -2.0 + Vector3(0,0.5,0), "second")
	var min_distance := INF
	for frame in range(900):
		await physics_frame
		var a: Vector3 = walkers[0].global_position
		var b: Vector3 = walkers[1].global_position
		min_distance = minf(min_distance, Vector2(a.x-b.x,a.z-b.z).length())
		if arrived.size() == 2: break
	check(arrived.has("first") and arrived.has("second"), "both reach original destinations seed %d" % seed_value)
	check(walkers[0].yield_count > 0, "lower priority yields seed %d" % seed_value)
	check(walkers[0].is_on_floor() and walkers[1].is_on_floor(), "both grounded seed %d" % seed_value)
	check(min_distance >= 0.50, "capsule centers stay separated seed %d, min %.3f" % [seed_value,min_distance])
	world.queue_free()
	await process_frame
func run() -> void:
	for seed_value in [19, 73, 151, 271, 419, 547, 683, 811, 947, 1091, 1223, 1361]:
		await run_case(seed_value)
	print("Seeded opposing crowd avoidance: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; twelve angles)")
	quit(0 if failures == 0 else 1)
