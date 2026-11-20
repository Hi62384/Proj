extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0

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

func collision_seen(bodies: Array[AnimatableBody3D]) -> bool:
	for i in range(bodies.size()):
		for j in range(i + 1, bodies.size()):
			if absf(bodies[i].position.x - bodies[j].position.x) < 2.0 and absf(bodies[i].position.z - bodies[j].position.z) < 2.0:
				return true
	return false

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var dispatcher: Node = Dispatcher.new()
	dispatcher.reservation_radius = 4.0
	world.add_child(dispatcher)
	var ids: Array[String] = ["restore-a", "restore-b", "restore-c"]
	var routes: Array[Array] = []
	var bodies: Array[AnimatableBody3D] = []
	var arrivals := {}
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	for index in range(3):
		var angle := float(index) * 2.0 * PI / 3.0
		var direction := Vector3(cos(angle), 0, sin(angle))
		var body := vehicle(world, -direction * 7.0)
		var route: Array[Vector3] = [body.position, direction * 7.0]
		check(dispatcher.register_vehicle(ids[index], body, route, 3.0, index + 1), "register reconstruction fleet " + str(index))
		routes.append(route)
		bodies.append(body)
	for id in ids:
		check(dispatcher.dispatch(id), "dispatch reconstruction fleet " + id)
	var snapshot := {}
	var positions := {}
	var waits := {}
	var pre_restore_collision := false
	for _frame in range(480):
		await physics_frame
		pre_restore_collision = pre_restore_collision or collision_seen(bodies)
		if bodies[0].position.length() < 0.12 and dispatcher.waiting_frames(ids[1]) > 0 and dispatcher.waiting_frames(ids[2]) > 0:
			snapshot = dispatcher.save_snapshot()
			for index in range(3):
				positions[ids[index]] = bodies[index].position
				waits[ids[index]] = dispatcher.waiting_frames(ids[index])
			break
	check(not pre_restore_collision, "platform bounds stay separated before saving")
	check(snapshot.get("version") == 1, "save dispatcher while one vehicle crosses and two wait")
	check(waits.get(ids[1], 0) > 0 and waits.get(ids[2], 0) > 0, "snapshot includes both waiting vehicles")
	world.queue_free()
	await process_frame
	arrivals.clear()
	world = Node3D.new()
	root.add_child(world)
	dispatcher = Dispatcher.new()
	dispatcher.reservation_radius = 4.0
	world.add_child(dispatcher)
	bodies.clear()
	for index in range(3):
		var angle := float(index) * 2.0 * PI / 3.0
		var direction := Vector3(cos(angle), 0, sin(angle))
		var body := vehicle(world, positions.get(ids[index], -direction * 7.0))
		var changed_route: Array[Vector3] = [body.position, routes[index][1] + Vector3(0, 0, 2)]
		check(dispatcher.register_vehicle(ids[index], body, changed_route, 6.0, 10 - index), "register changed restored fleet " + str(index))
		bodies.append(body)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	check(dispatcher.restore_snapshot(snapshot), "restore crossing fleet snapshot into fresh scene")
	var restored_state: Dictionary = dispatcher.save_snapshot()
	for id in ids:
		check(restored_state.vehicles[id].route == snapshot.vehicles[id].route, "restore saved route for " + id)
		check(restored_state.vehicles[id].speed == snapshot.vehicles[id].speed, "restore saved speed for " + id)
		check(restored_state.vehicles[id].priority == snapshot.vehicles[id].priority, "restore saved priority for " + id)
	var changed_junction: Dictionary = snapshot.duplicate(true)
	changed_junction.junctions[0] = Vector3(0.25, 0, 0)
	check(not dispatcher.restore_snapshot(changed_junction), "reject snapshot from changed junction geometry")
	check(dispatcher.save_snapshot() == restored_state, "changed junction rejection leaves restored fleet untouched")
	var changed_fleet: Dictionary = snapshot.duplicate(true)
	changed_fleet.vehicles.erase(ids[2])
	check(not dispatcher.restore_snapshot(changed_fleet), "reject snapshot with changed vehicle membership")
	check(dispatcher.save_snapshot() == restored_state, "changed fleet rejection leaves restored state untouched")
	var invalid_speed: Dictionary = snapshot.duplicate(true)
	invalid_speed.vehicles[ids[0]].speed = 0.0
	check(not dispatcher.restore_snapshot(invalid_speed), "reject snapshot with non-positive vehicle speed")
	check(dispatcher.save_snapshot() == restored_state, "invalid speed rejection leaves restored state untouched")
	var invalid_priority: Dictionary = snapshot.duplicate(true)
	invalid_priority.vehicles[ids[1]].priority = "urgent"
	check(not dispatcher.restore_snapshot(invalid_priority), "reject snapshot with malformed priority")
	check(dispatcher.save_snapshot() == restored_state, "invalid priority rejection leaves restored state untouched")
	for id in ids:
		check(dispatcher.waiting_frames(id) == waits.get(id, -1), "restore wait count for " + id)
	var post_restore_collision := false
	for _frame in range(1200):
		await physics_frame
		post_restore_collision = post_restore_collision or collision_seen(bodies)
		if arrivals.size() == ids.size():
			break
	check(not post_restore_collision, "platform bounds stay separated after reconstruction")
	check(arrivals.size() == ids.size(), "all restored vehicles eventually arrive")
	for index in range(3):
		check(arrivals.has(ids[index]), "restored arrival signal for " + ids[index])
		check(bodies[index].position.distance_to(routes[index][1]) < 0.03, "restored endpoint for " + ids[index])
	print("Temporary game fleet dispatch reconstruction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; three vehicles, one crossing snapshot and restore)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
