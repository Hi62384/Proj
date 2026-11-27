extends SceneTree
const Npc = preload("res://npc.gd")
func make_box(parent: Node, size: Vector3, pos: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var volume := BoxShape3D.new()
	volume.size = size
	shape.shape = volume
	body.add_child(shape)
	body.position = pos
	parent.add_child(body)
	return body
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	make_box(world, Vector3(8, 0.4, 8), Vector3.ZERO)
	make_box(world, Vector3(1.2, 1.5, 0.2), Vector3(0, 0.8, 0.8))
	make_box(world, Vector3(1.2, 1.5, 0.2), Vector3(0, 0.8, -0.8))
	var npc = Npc.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1
	shape.shape = capsule
	npc.add_child(shape)
	npc.collision_layer = 2
	npc.collision_mask = 3
	npc.cooperative_avoidance = true
	npc.extended_avoidance = true
	npc.position = Vector3(0, 0.75, 0)
	world.add_child(npc)
	var other := CharacterBody3D.new()
	other.position = Vector3(-1, 0.75, 0)
	world.add_child(other)
	for i in range(30): await physics_frame
	npc.yield_to(other)
	for i in range(90): await physics_frame
	var ok: bool = npc.yield_count == 1 and not npc.yielding and npc.is_on_floor() and npc.position.x > 0.9 and absf(npc.position.z) < 0.15
	print("Temporary game extended avoidance: ", "PASS" if ok else "FAIL", " position=", npc.position)
	world.queue_free()
	await process_frame
	quit(0 if ok else 1)
