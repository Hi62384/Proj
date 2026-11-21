extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var arrivals := {}
var recoveries := {}
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
	var retreating := vehicle(world, Vector3(-6, 0, 0))
	var continuing := vehicle(world, Vector3(0, 0, -6))
	var dispatcher: Node = Dispatcher.new()
	world.add_child(dispatcher)
	dispatcher.vehicle_arrived.connect(func(id: String): arrivals[id] = true)
	dispatcher.vehicle_recovered.connect(func(id: String, safe_stop: Vector3): recoveries[id] = safe_stop)
	var retreat_route: Array[Vector3] = [Vector3(-6, 0, 0), Vector3(6, 0, 0)]
	var continue_route: Array[Vector3] = [Vector3(0, 0, -6), Vector3(0, 0, 6)]
	check(dispatcher.register_vehicle("retreating", retreating, retreat_route, 2.0, 1), "register route to interrupt")
	check(dispatcher.register_vehicle("continuing", continuing, continue_route, 2.0, 2), "register waiting route")
	check(dispatcher.dispatch("retreating") and dispatcher.dispatch("continuing"), "start both vehicles")
	var interrupted := false
	for _frame in range(900):
		await physics_frame
		if not interrupted and dispatcher._junction_owners.get(0, "") == "retreating" and absf(retreating.position.x) < 0.5:
			check(not dispatcher.interrupt_to_safe_stop("retreating", Vector3(0, 0, 0)), "reject safe stop inside reserved junction")
			interrupted = dispatcher.interrupt_to_safe_stop("retreating", Vector3(-6.5, 0, 0))
			check(interrupted, "interrupt owner to safe stop while inside junction")
		var dx := absf(retreating.position.x - continuing.position.x)
		var dz := absf(retreating.position.z - continuing.position.z)
		if dx < 2.0 and dz < 2.0:
			overlap_seen = true
		if recoveries.has("retreating") and arrivals.has("continuing"):
			break
	check(interrupted, "vehicle interruption was triggered while owning junction")
	check(recoveries.get("retreating") == Vector3(-6.5, 0, 0), "interrupted vehicle reports its safe stop")
	check(arrivals.has("continuing") and continuing.position.distance_to(Vector3(0, 0, 6)) < 0.03, "waiting vehicle proceeds after reservation releases")
	check(dispatcher.waiting_frames("continuing") > 0, "second route waited for the junction owner")
	check(not overlap_seen, "platform collision bounds never overlap during recovery")
	print("Temporary game junction interruption recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; safe return releases a shared junction)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
