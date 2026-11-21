extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var arrivals := {}
var overlap_seen := false
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
	var world := Node3D.new()
	root.add_child(world)
	var east_west := vehicle(world, Vector3(-4, 0, 0))
	var north_south := vehicle(world, Vector3(0, 0, -4))
	var dispatcher: Node = Dispatcher.new()
	world.add_child(dispatcher)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	var horizontal: Array[Vector3] = [Vector3(-4, 0, 0), Vector3(4, 0, 0)]
	var vertical: Array[Vector3] = [Vector3(0, 0, -4), Vector3(0, 0, 4)]
	check(dispatcher.register_vehicle("east-west", east_west, horizontal, 2.0, 1), "register horizontal route")
	check(dispatcher.register_vehicle("north-south", north_south, vertical, 2.0, 2), "register vertical route")
	check(dispatcher.dispatch("east-west") and dispatcher.dispatch("north-south"), "dispatch both crossing services")
	for _frame in range(720):
		await physics_frame
		var dx := absf(east_west.position.x - north_south.position.x)
		var dz := absf(east_west.position.z - north_south.position.z)
		if dx < 2.0 and dz < 2.0:
			overlap_seen = true
		if arrivals.size() == 2:
			break
	check(not overlap_seen, "platform collision bounds never overlap in the crossing")
	check(dispatcher.waiting_frames("north-south") > 0, "lower-priority physical route waits for junction reservation")
	check(arrivals.has("east-west") and arrivals.has("north-south"), "both crossing vehicles eventually reach their destinations")
	check(east_west.position.distance_to(horizontal[1]) < 0.03 and north_south.position.distance_to(vertical[1]) < 0.03, "vehicles stop at their configured route endpoints")
	print("Temporary game crossing-vehicle dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; two intersecting routes)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
