extends SceneTree
const Npc = preload("res://npc.gd")
func box(world: Node, size: Vector3, position: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var volume := BoxShape3D.new()
	volume.size = size
	shape.shape = volume
	body.add_child(shape)
	body.position = position
	world.add_child(body)
	return body
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	box(world, Vector3(5, 0.4, 5), Vector3.ZERO)
	var npc = Npc.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1
	shape.shape = capsule
	npc.add_child(shape)
	npc.position = Vector3(0, 0.75, 0)
	npc.cooperative_avoidance = true
	world.add_child(npc)
	var other := CharacterBody3D.new()
	other.position = Vector3(-1, 0.75, 0)
	world.add_child(other)
	for i in range(30): await physics_frame
	npc.yield_to(other)
	for i in range(5): await physics_frame
	var started: bool = npc.yielding and npc.position.z > 0.05
	box(world, Vector3(1, 1.5, 0.2), Vector3(0, 0.8, 1.0))
	for i in range(40): await physics_frame
	var ok: bool = started and not npc.yielding and npc.position.z < 0.8 and npc.is_on_floor()
	print("Temporary game yield interrupted by obstacle: ", "PASS" if ok else "FAIL", " started=", started, " position=", npc.position)
	world.queue_free()
	await process_frame
	quit(0 if ok else 1)
