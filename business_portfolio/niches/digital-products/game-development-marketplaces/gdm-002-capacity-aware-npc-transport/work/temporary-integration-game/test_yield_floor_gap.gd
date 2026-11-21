extends SceneTree
const Npc = preload("res://npc.gd")
func floor_piece(world: Node, size: Vector3, position: Vector3) -> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	body.position = position
	world.add_child(body)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	floor_piece(world, Vector3(2.2, 0.4, 2), Vector3(-0.8, 0, 0))
	floor_piece(world, Vector3(2.2, 0.4, 2), Vector3(2, 0, 0))
	var npc = Npc.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1
	shape.shape = capsule
	npc.add_child(shape)
	npc.position = Vector3(0, 0.75, 0)
	world.add_child(npc)
	for i in range(30): await physics_frame
	var endpoint: Vector3 = npc.global_position + Vector3(1.2, 0.2, 0)
	var query := PhysicsRayQueryParameters3D.create(endpoint, endpoint + Vector3(0, -1.5, 0), 1)
	var endpoint_supported := not world.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
	var rejects_gap: bool = not npc._can_yield(Vector3(1.2, 0, 0))
	var ok: bool = endpoint_supported and rejects_gap and npc.is_on_floor()
	print("Temporary game sampled-floor gap: ", "PASS" if ok else "FAIL", " endpoint=", endpoint_supported, " rejected=", rejects_gap)
	world.queue_free()
	await process_frame
	quit(0 if ok else 1)
