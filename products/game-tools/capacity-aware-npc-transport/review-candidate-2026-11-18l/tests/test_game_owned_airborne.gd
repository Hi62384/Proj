extends SceneTree
const Character = preload("res://examples/game_owned_character.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var floor := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4,0.4,4)
	floor_shape.shape = box
	floor.add_child(floor_shape)
	world.add_child(floor)
	var body = Character.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	body.add_child(shape)
	body.position = Vector3(0,2,0)
	world.add_child(body)
	var arrivals := []
	body.motion_finished.connect(func(id): arrivals.append([id,body.is_on_floor()]))
	body.start_motion(Vector3(0,0.7,0),"airborne")
	for i in range(5): await physics_frame
	check(arrivals.is_empty(),"arrival not emitted while airborne at target x/z")
	for i in range(120):
		await physics_frame
		if body.is_on_floor() and not arrivals.is_empty(): break
	check(arrivals == [["airborne",true]],"arrival emitted once after landing")
	print("Game controller airborne arrival: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
