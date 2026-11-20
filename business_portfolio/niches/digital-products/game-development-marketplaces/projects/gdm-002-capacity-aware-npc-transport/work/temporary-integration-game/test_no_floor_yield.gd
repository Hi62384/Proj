extends SceneTree
const Npc = preload("res://npc.gd")
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4, 0.4, 1)
	floor_shape.shape = box
	floor_body.add_child(floor_shape)
	world.add_child(floor_body)
	var blocker = Npc.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	blocker.add_child(shape)
	blocker.collision_layer = 2
	blocker.collision_mask = 3
	blocker.cooperative_avoidance = true
	blocker.position = Vector3(0, 0.75, 0)
	world.add_child(blocker)
	var other := CharacterBody3D.new()
	other.position = Vector3(-1, 0.75, 0)
	world.add_child(other)
	for i in range(30): await physics_frame
	blocker.yield_to(other)
	for i in range(30): await physics_frame
	var ok: bool = blocker.yield_count == 0 and not blocker.yielding and blocker.is_on_floor() and absf(blocker.position.z) < 0.1
	print("Temporary game unsupported yield rejection: ", "PASS" if ok else "FAIL", " yield=", blocker.yield_count, " position=", blocker.position)
	world.queue_free()
	await process_frame
	quit(0 if ok else 1)
