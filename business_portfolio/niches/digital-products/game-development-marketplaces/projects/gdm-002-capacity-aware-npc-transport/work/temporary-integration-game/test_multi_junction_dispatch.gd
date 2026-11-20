extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var arrivals := {}
var overlap_seen := false
var fleet := {}
var goals := {
	"horizontal": Vector3(7, 0, 0),
	"left-vertical": Vector3(-3, 0, 5),
	"right-vertical": Vector3(3, 0, -5)
}
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
	fleet["horizontal"] = vehicle(world, Vector3(-7, 0, 0))
	fleet["left-vertical"] = vehicle(world, Vector3(-3, 0, -5))
	fleet["right-vertical"] = vehicle(world, Vector3(3, 0, 5))
	var dispatcher: Node = Dispatcher.new()
	var intersections: Array[Vector3] = [Vector3(-3, 0, 0), Vector3(3, 0, 0)]
	dispatcher.junctions = intersections
	world.add_child(dispatcher)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	var horizontal: Array[Vector3] = [Vector3(-7, 0, 0), goals.horizontal]
	var left_route: Array[Vector3] = [Vector3(-3, 0, -5), goals["left-vertical"]]
	var right_route: Array[Vector3] = [Vector3(3, 0, 5), goals["right-vertical"]]
	check(dispatcher.register_vehicle("horizontal", fleet.horizontal, horizontal, 2.0, 1), "register two-junction horizontal route")
	check(dispatcher.register_vehicle("left-vertical", fleet["left-vertical"], left_route, 2.0, 2), "register left crossing route")
	check(dispatcher.register_vehicle("right-vertical", fleet["right-vertical"], right_route, 2.0, 3), "register right crossing route")
	for id in ["horizontal", "left-vertical", "right-vertical"]:
		check(dispatcher.dispatch(id), "dispatch " + id)
	for _frame in range(1000):
		await physics_frame
		var ids := ["horizontal", "left-vertical", "right-vertical"]
		for i in range(ids.size()):
			for j in range(i + 1, ids.size()):
				var a: AnimatableBody3D = fleet[ids[i]]
				var b: AnimatableBody3D = fleet[ids[j]]
				if absf(a.position.x - b.position.x) < 2.0 and absf(a.position.z - b.position.z) < 2.0:
					overlap_seen = true
		if arrivals.size() == 3:
			break
	check(not overlap_seen, "platform collision bounds stay separated at both junctions")
	check(arrivals.size() == 3, "all vehicles complete the two-junction dispatch")
	for id in goals:
		check(arrivals.has(id), id + " emits arrival")
		check(fleet[id].position.distance_to(goals[id]) < 0.03, id + " reaches its mapped endpoint")
	check(dispatcher.waiting_frames("left-vertical") > 0 or dispatcher.waiting_frames("right-vertical") > 0, "crossing routes wait for reservations")
	print("Temporary game multi-junction dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; three vehicles, two junctions)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
