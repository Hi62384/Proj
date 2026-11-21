extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var recovered := []
var arrivals := []

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
	var safe_stop := Vector3(-6.5, 0, 0)
	var world := Node3D.new()
	root.add_child(world)
	var dispatcher: Node = Dispatcher.new()
	world.add_child(dispatcher)
	var body := vehicle(world, Vector3(-6, 0, 0))
	var original_route: Array[Vector3] = [Vector3(-6, 0, 0), Vector3(6, 0, 0)]
	check(dispatcher.register_vehicle("recovery", body, original_route, 2.4, 1), "register interrupted vehicle")
	dispatcher.vehicle_recovered.connect(func(id: String, stop: Vector3): recovered.append({"id":id, "stop":stop}))
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals.append(id))
	check(dispatcher.dispatch("recovery"), "dispatch vehicle before interruption")
	var interrupted := false
	for _frame in range(480):
		await physics_frame
		if dispatcher._junction_owners.get(0, "") == "recovery" and absf(body.position.x) < 0.5:
			var before_unsafe_request: Dictionary = dispatcher.save_snapshot()
			check(not dispatcher.interrupt_to_safe_stop("recovery", Vector3.ZERO), "reject unsafe stop inside reserved junction")
			check(dispatcher.save_snapshot() == before_unsafe_request, "unsafe stop rejection leaves active trip unchanged")
			interrupted = dispatcher.interrupt_to_safe_stop("recovery", safe_stop)
			break
	check(interrupted, "interrupt vehicle to safe stop from junction")
	for _frame in range(35):
		await physics_frame
	var saved_position := body.position
	var snapshot: Dictionary = dispatcher.save_snapshot()
	var entry: Dictionary = snapshot.get("vehicles", {}).get("recovery", {})
	check(entry.get("recovering", false) and entry.get("active", false), "snapshot records active recovery in progress")
	check(entry.get("route", []).size() == 2 and entry.route[1] == safe_stop, "snapshot retains safe-stop route")
	world.queue_free()
	await process_frame
	world = Node3D.new()
	root.add_child(world)
	dispatcher = Dispatcher.new()
	world.add_child(dispatcher)
	body = vehicle(world, saved_position)
	var changed_registration: Array[Vector3] = [saved_position, Vector3(8, 0, 0)]
	check(dispatcher.register_vehicle("recovery", body, changed_registration, 5.0, 9), "register changed route before recovery restore")
	dispatcher.vehicle_recovered.connect(func(id: String, stop: Vector3): recovered.append({"id":id, "stop":stop}))
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals.append(id))
	check(dispatcher.restore_snapshot(snapshot), "restore active safe-stop recovery into rebuilt dispatcher")
	var restored: Dictionary = dispatcher.save_snapshot().vehicles.recovery
	check(restored.recovering and restored.active, "restored vehicle remains in recovery state")
	check(restored.route[1] == safe_stop and restored.speed == entry.speed and restored.priority == entry.priority, "restore applies saved recovery route and motion settings")
	for _frame in range(720):
		await physics_frame
		if recovered.size() > 0:
			break
	check(recovered.size() == 1 and recovered[0].id == "recovery" and recovered[0].stop == safe_stop, "recovery signal fires once at the restored safe stop")
	check(arrivals.is_empty(), "recovery does not emit normal arrival")
	check(body.position.distance_to(safe_stop) < 0.03, "restored vehicle physically reaches safe stop")
	var finished: Dictionary = dispatcher.save_snapshot().vehicles.recovery
	check(not finished.active and not finished.recovering, "vehicle clears recovery state after arrival")
	print("Temporary game recovery dispatch reconstruction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; unsafe-stop rejection and in-flight recovery restore)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
