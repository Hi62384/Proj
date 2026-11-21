extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
var failures := 0
var transit: Node
var dispatcher: Node
var vehicles := {}
var passengers := {}
var recovery_request := {}
var dispatched := {}
var arrived := {}
var recovered := {}
var disabled := false
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

func _transit_event(event: Dictionary) -> void:
	if event.type == "boarding_requested":
		check(transit.acknowledge_boarding(event.agent, event.details.vehicle, event.details.token, event.id), "coordinator accepts boarding acknowledgment for " + event.agent)
	elif event.type == "departed":
		var id: String = event.details.vehicle
		dispatched[id] = dispatcher.dispatch(id)
	elif event.type == "recovery_requested":
		recovery_request = event.duplicate(true)
		var safe_stop := Vector3(-6.5, 0, 0) if event.details.service == "eastbound" else Vector3(0, 0, -6.5)
		check(dispatcher.interrupt_to_safe_stop(event.details.vehicle, safe_stop), "service interruption routes physical vehicle to its coordinator-approved safe stop")
	elif event.type == "recovered":
		recovered[event.agent] = event.details.stop
	elif event.type == "alighting_requested":
		check(transit.acknowledge_alighting(event.agent, event.details.vehicle, event.details.token, event.id), "coordinator accepts alighting after physical arrival")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	vehicles["east-vehicle"] = vehicle(world, Vector3(-4, 0, 0))
	vehicles["north-vehicle"] = vehicle(world, Vector3(0, 0, -4))
	for id in ["east-rider", "north-rider"]:
		var marker := Marker3D.new()
		var vehicle_id := "east-vehicle" if id == "east-rider" else "north-vehicle"
		vehicles[vehicle_id].add_child(marker)
		passengers[id] = marker
	transit = Transit.new()
	dispatcher = Dispatcher.new()
	world.add_child(transit)
	world.add_child(dispatcher)
	var configured_junctions: Array[Vector3] = [Vector3.ZERO]
	dispatcher.junctions = configured_junctions
	dispatcher.vehicle_arrived.connect(func(id: String): arrived[id] = true)
	dispatcher.vehicle_recovered.connect(func(id: String, safe_stop: Vector3):
		var event: Dictionary = recovery_request
		var agent: String = event.agent
		check(safe_stop == Vector3(-6.5, 0, 0), "physical recovery reaches the configured safe stop")
		recovered[agent] = transit.acknowledge_recovery(agent, event.details.vehicle, event.details.token, event.id, "west")
	)
	transit.transit_event.connect(_transit_event)
	var cfg := {"revision":"coordinator-junction-dispatch-v1", "tick_unit":"simulation_tick", "stops":["west", "east", "south", "north"], "vehicles":[{"id":"east-vehicle", "capacity":1}, {"id":"north-vehicle", "capacity":1}], "services":[{"id":"eastbound", "vehicle":"east-vehicle", "from":"west", "to":"east", "period":4, "offset":0, "duration":1, "enabled":true}, {"id":"northbound", "vehicle":"north-vehicle", "from":"south", "to":"north", "period":4, "offset":0, "duration":1, "enabled":true}]}
	var configured: bool = transit.configure(cfg, "coordinator-junction-dispatch")
	var east_route: Array[Vector3] = [Vector3(-4, 0, 0), Vector3(4, 0, 0)]
	var north_route: Array[Vector3] = [Vector3(0, 0, -4), Vector3(0, 0, 4)]
	configured = configured and dispatcher.register_vehicle("east-vehicle", vehicles["east-vehicle"], east_route, 2.0, 1)
	configured = configured and dispatcher.register_vehicle("north-vehicle", vehicles["north-vehicle"], north_route, 2.0, 2)
	check(configured, "configure coordinator and mapped physical routes")
	check(transit.request_journey("east-rider", "west", "east") and transit.request_journey("north-rider", "south", "north"), "request both crossing services")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(), "coordinator boards and departs both vehicles")
	check(dispatched.get("east-vehicle", false) and dispatched.get("north-vehicle", false), "departed events dispatch both physical routes")
	for _frame in range(900):
		await physics_frame
		var east: AnimatableBody3D = vehicles["east-vehicle"]
		var north: AnimatableBody3D = vehicles["north-vehicle"]
		var dx := absf(east.position.x - north.position.x)
		var dz := absf(east.position.z - north.position.z)
		if dx < 2.0 and dz < 2.0:
			overlap_seen = true
		if not disabled and east.position.distance_to(Vector3.ZERO) < 0.6:
			disabled = transit.set_service_enabled("eastbound", false)
			check(disabled and not recovery_request.is_empty(), "coordinator disruption requests recovery while a vehicle holds the junction")
		if arrived.has("north-vehicle") and recovered.get("east-rider", false):
			break
	check(not overlap_seen, "crossing physical bounds remain disjoint through coordinator dispatch and recovery")
	check(dispatcher.waiting_frames("north-vehicle") > 0, "second departed service waits for the reserved junction")
	check(recovered.get("east-rider", false) and transit.journey("east-rider").state == "failed", "coordinator releases the recovered seat and fails the route with no alternative")
	check(arrived.has("north-vehicle") and transit.begin_tick(), "uninterrupted physical service reaches its mapped stop and coordinator arrival tick opens")
	check(transit.journey("north-rider").state == "completed", "uninterrupted rider completes after physical alighting")
	check(transit.inspect_vehicle("east-vehicle").ledger.aboard.is_empty() and transit.inspect_vehicle("north-vehicle").ledger.aboard.is_empty(), "coordinator seats are clear after interruption recovery and alighting")
	check(passengers["east-rider"].global_position.distance_to(Vector3(-6.5, 0, 0)) < 0.03 and passengers["north-rider"].global_position.distance_to(Vector3(0, 0, 4)) < 0.03, "passenger markers follow their physical platforms")
	print("Temporary game coordinator-driven junction dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; departure, interruption, safe recovery and waiting route)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
