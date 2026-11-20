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
	var ground := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(12, 0.4, 5)
	shape.shape = box
	ground.add_child(shape)
	ground.position.y = -0.2
	world.add_child(ground)
	var walkers := {}
	for id in ["yielding", "continuing"]:
		var npc: CharacterBody3D = Npc.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.28
		capsule.height = 1.0
		var collision := CollisionShape3D.new()
		collision.shape = capsule
		npc.add_child(collision)
		npc.position = Vector3(-2, 0.5, 0) if id == "yielding" else Vector3(2, 0.5, 0)
		npc.collision_layer = 2
		npc.collision_mask = 3
		npc.cooperative_avoidance = true
		npc.extended_avoidance = true
		npc.avoidance_priority = 1 if id == "yielding" else 2
		npc.reached.connect(func(request_id: String): arrived[request_id] = true)
		world.add_child(npc)
		walkers[id] = npc
	walkers.yielding.walk_to(Vector3(2, 0.5, 0), "cancel-me")
	walkers.continuing.walk_to(Vector3(-2, 0.5, 0), "continue-me")
	for _frame in range(180):
		await physics_frame
		if walkers.yielding.yielding: break
	check(walkers.yielding.yield_count > 0 and walkers.yielding.yielding, "first walker begins its crowd sidestep")
	walkers.yielding.cancel_walk("cancel-me")
	for _frame in range(900):
		await physics_frame
		if arrived.has("continue-me"): break
	check(not arrived.has("cancel-me"), "canceled sidestep does not emit original arrival")
	check(not walkers.yielding.walking and not walkers.yielding.yielding, "canceled walker stays stopped")
	check(arrived.has("continue-me") and walkers.continuing.global_position.distance_to(Vector3(-2, 0.5, 0)) < 0.3, "other walker completes its unaffected route")
	check(walkers.yielding.is_on_floor() and walkers.continuing.is_on_floor(), "both walkers remain grounded")
	print("Temporary game crowd sidestep cancellation: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
