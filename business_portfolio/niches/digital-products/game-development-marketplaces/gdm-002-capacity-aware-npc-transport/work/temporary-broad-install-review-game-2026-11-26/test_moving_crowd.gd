extends SceneTree
const Npc = preload("res://npc.gd")
var failures := 0
var arrived := {}
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(12, 0.4, 5)
	floor_shape.shape = floor_box
	floor_body.add_child(floor_shape)
	floor_body.position.y = -0.2
	world.add_child(floor_body)
	var walkers := {}
	for id in ["northbound", "southbound"]:
		var npc: CharacterBody3D = Npc.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.28
		capsule.height = 1.0
		var collision := CollisionShape3D.new()
		collision.shape = capsule
		npc.add_child(collision)
		npc.position = Vector3(-2.0, 0.5, 0.0) if id == "northbound" else Vector3(2.0, 0.5, 0.0)
		npc.collision_layer = 2
		npc.collision_mask = 3
		npc.cooperative_avoidance = true
		npc.extended_avoidance = true
		npc.avoidance_priority = 1 if id == "northbound" else 2
		npc.reached.connect(func(request_id: String): arrived[request_id] = true)
		world.add_child(npc)
		walkers[id] = npc
	walkers.northbound.walk_to(Vector3(2.0, 0.5, 0.0), "northbound-trip")
	walkers.southbound.walk_to(Vector3(-2.0, 0.5, 0.0), "southbound-trip")
	for _frame in range(900):
		await physics_frame
		if arrived.size() == 2:
			break
	check(arrived.has("northbound-trip") and arrived.has("southbound-trip"), "both moving walkers finish original routes")
	check(walkers.northbound.yield_count > 0, "stable low-priority walker yields to moving crowd")
	check(walkers.southbound.yield_count == 0, "higher-priority walker retains its route")
	check(walkers.northbound.is_on_floor() and walkers.southbound.is_on_floor(), "both remain grounded")
	check(walkers.northbound.global_position.distance_to(Vector3(2.0, 0.5, 0.0)) < 0.3 and walkers.southbound.global_position.distance_to(Vector3(-2.0, 0.5, 0.0)) < 0.3, "both reach intended endpoints")
	print("Temporary game moving crowd avoidance: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; two opposing walkers)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
