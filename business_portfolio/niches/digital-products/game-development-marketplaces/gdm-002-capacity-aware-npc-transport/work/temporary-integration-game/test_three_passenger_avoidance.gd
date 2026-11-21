extends SceneTree
const Npc = preload("res://npc.gd")
func npc_at(world: Node, position: Vector3):
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
	npc.position = position
	world.add_child(npc)
	return npc
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(10, 0.4, 6)
	floor_shape.shape = box
	floor_body.add_child(floor_shape)
	world.add_child(floor_body)
	var walker = npc_at(world, Vector3(-3, 0.75, 0))
	var first = npc_at(world, Vector3(-0.7, 0.75, 0))
	var second = npc_at(world, Vector3(0.8, 0.75, 0))
	var reached := []
	walker.reached.connect(func(id): reached.append(id))
	for i in range(30): await physics_frame
	walker.walk_to(Vector3(3, 0.7, 0), "across")
	for i in range(350):
		await physics_frame
		if not reached.is_empty(): break
	var ok: bool = reached == ["across"] and first.yield_count > 0 and second.yield_count > 0 and walker.is_on_floor() and first.is_on_floor() and second.is_on_floor()
	print("Temporary game three-passenger avoidance: ", "PASS" if ok else "FAIL", " reached=", reached, " yields=", first.yield_count, ",", second.yield_count)
	world.queue_free()
	await process_frame
	quit(0 if ok else 1)
