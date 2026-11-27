extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var recoveries := {}
var arrivals := {}

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

func overlap_seen(first: AnimatableBody3D, second: AnimatableBody3D) -> bool:
	return absf(first.position.x - second.position.x) < 2.0 and absf(first.position.z - second.position.z) < 2.0

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var safe_stop := Vector3(-6.5, 0, 0)
	var crossing_end := Vector3(0, 0, 6)
	var world := Node3D.new()
	root.add_child(world)
	var dispatcher: Node = Dispatcher.new()
	world.add_child(dispatcher)
	var retreating := vehicle(world, Vector3(-6, 0, 0))
	var crossing := vehicle(world, Vector3(0, 0, -6))
	var retreat_route: Array[Vector3] = [Vector3(-6, 0, 0), Vector3(6, 0, 0)]
	var crossing_route: Array[Vector3] = [Vector3(0, 0, -6), crossing_end]
	check(dispatcher.register_vehicle("retreating", retreating, retreat_route, 2.0, 1), "register priority recovery vehicle")
	check(dispatcher.register_vehicle("crossing", crossing, crossing_route, 2.0, 2), "register waiting crossing vehicle")
	dispatcher.vehicle_recovered.connect(func(id: String, stop: Vector3): recoveries[id] = stop)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	check(dispatcher.dispatch("retreating") and dispatcher.dispatch("crossing"), "dispatch both physical vehicles")
	var interrupted := false
	var pre_restore_overlap := false
	var snapshot := {}
	var positions := {}
	var waits := {}
	for _frame in range(900):
		await physics_frame
		pre_restore_overlap = pre_restore_overlap or overlap_seen(retreating, crossing)
		if not interrupted and dispatcher._junction_owners.get(0, "") == "retreating" and absf(retreating.position.x) < 0.5:
			interrupted = dispatcher.interrupt_to_safe_stop("retreating", safe_stop)
			check(interrupted, "interrupt junction owner toward safe stop")
		if interrupted and dispatcher.waiting_frames("crossing") > 10 and absf(retreating.position.x) < 2.8:
			snapshot = dispatcher.save_snapshot()
			positions = {"retreating":retreating.position, "crossing":crossing.position}
			waits = {"retreating":dispatcher.waiting_frames("retreating"), "crossing":dispatcher.waiting_frames("crossing")}
			break
	check(not pre_restore_overlap, "vehicle bounds stay separate before parallel recovery save")
	check(interrupted and snapshot.get("version") == 2, "save mixed recovery and active crossing state")
	check(snapshot.get("vehicles", {}).get("retreating", {}).get("recovering", false), "saved first vehicle is recovering")
	check(snapshot.get("vehicles", {}).get("crossing", {}).get("active", false) and waits.get("crossing", 0) > 0, "saved second vehicle is active and waiting")
	world.queue_free()
	await process_frame
	recoveries.clear()
	arrivals.clear()
	world = Node3D.new()
	root.add_child(world)
	dispatcher = Dispatcher.new()
	world.add_child(dispatcher)
	retreating = vehicle(world, positions.get("retreating", Vector3(-1, 0, 0)))
	crossing = vehicle(world, positions.get("crossing", Vector3(0, 0, -4)))
	var altered_retreat: Array[Vector3] = [retreating.position, Vector3(8, 0, 0)]
	var altered_crossing: Array[Vector3] = [crossing.position, Vector3(0, 0, -8)]
	check(dispatcher.register_vehicle("retreating", retreating, altered_retreat, 5.0, 9), "register changed recovery route")
	check(dispatcher.register_vehicle("crossing", crossing, altered_crossing, 5.0, 8), "register changed crossing route")
	dispatcher.vehicle_recovered.connect(func(id: String, stop: Vector3): recoveries[id] = stop)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	var registered_state: Dictionary = dispatcher.save_snapshot()
	var malformed_snapshot: Dictionary = snapshot.duplicate(true)
	malformed_snapshot.vehicles.crossing.wait_count = -1
	check(not dispatcher.restore_snapshot(malformed_snapshot), "reject malformed waiting vehicle state")
	check(dispatcher.save_snapshot() == registered_state, "malformed mixed-state snapshot leaves both registrations unchanged")
	check(dispatcher.restore_snapshot(snapshot), "restore mixed recovery and crossing snapshot")
	var restored: Dictionary = dispatcher.save_snapshot().vehicles
	check(restored.retreating.recovering and restored.retreating.route[1] == safe_stop, "restore first vehicle safe-stop route")
	check(restored.crossing.active and not restored.crossing.recovering and restored.crossing.route[1] == crossing_end, "restore second vehicle crossing route")
	check(dispatcher.waiting_frames("crossing") == waits.get("crossing", -1), "restore crossing vehicle wait count")
	var post_restore_overlap := false
	for _frame in range(1200):
		await physics_frame
		post_restore_overlap = post_restore_overlap or overlap_seen(retreating, crossing)
		if recoveries.has("retreating") and arrivals.has("crossing"):
			break
	check(not post_restore_overlap, "vehicle bounds stay separate after mixed-state restore")
	check(recoveries.get("retreating") == safe_stop, "recovering vehicle reaches its safe stop")
	check(arrivals.has("crossing") and crossing.position.distance_to(crossing_end) < 0.03, "waiting vehicle proceeds and reaches crossing endpoint")
	check(dispatcher.waiting_frames("crossing") > 0, "crossing vehicle waited for recovery clearance")
	check(not arrivals.has("retreating"), "recovery vehicle does not emit normal arrival")
	print("Temporary game parallel recovery reconstruction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; recover one vehicle while another waits and crosses)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
