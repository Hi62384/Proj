extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
const Npc = preload("res://npc.gd")
var failures := 0
var world: Node3D
var transit: Node
var bridge: Node
var dispatcher: Node
var vehicles := {}
var passengers := {}
var requests := {}
var recovery_requests := {}
var recovery_started := false
var dispatched := {}
var arrived := {}
var recovered := {}
var disabled := false
var overlap_seen := false
var cfg := {"revision":"junction-restore-capacity-two-v1", "tick_unit":"simulation_tick", "stops":["west", "east", "south", "north"], "vehicles":[{"id":"east-vehicle", "capacity":2}, {"id":"north-vehicle", "capacity":1}], "services":[{"id":"eastbound", "vehicle":"east-vehicle", "from":"west", "to":"east", "period":4, "offset":0, "duration":1, "enabled":true}, {"id":"northbound", "vehicle":"north-vehicle", "from":"south", "to":"north", "period":4, "offset":0, "duration":1, "enabled":true}]}

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)

func vehicle(at: Vector3) -> AnimatableBody3D:
	var body := AnimatableBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(2, 0.4, 2)
	shape.shape = box
	body.add_child(shape)
	body.position = at
	world.add_child(body)
	return body

func static_pad(at: Vector3, size: Vector3) -> void:
	var pad := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	pad.add_child(shape)
	pad.position = at
	world.add_child(pad)

func make_passenger(id: String, vehicle_id: String, restored: bool) -> CharacterBody3D:
	var passenger: CharacterBody3D = Npc.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	var collision := CollisionShape3D.new()
	collision.shape = capsule
	passenger.add_child(collision)
	passenger.collision_layer = 2
	passenger.collision_mask = 1
	if restored:
		vehicles[vehicle_id].add_child(passenger)
		passenger.position = Vector3(0, 0.7, 0)
		passenger.set_physics_process(false)
	else:
		world.add_child(passenger)
		passenger.position = Vector3(-4, 0.7, 2.0) if id == "east-rider" else (Vector3(-4, 0.7, 3.0) if id == "east-rider-two" else Vector3(2.4, 0.7, -4))
	passenger.reached.connect(_passenger_reached.bind(id))
	return passenger

func _dismount(passenger: CharacterBody3D) -> void:
	var saved_transform: Transform3D = passenger.global_transform
	var old_parent := passenger.get_parent()
	old_parent.remove_child(passenger)
	world.add_child(passenger)
	passenger.global_transform = saved_transform
	passenger.set_physics_process(true)

func _passenger_reached(request_id: String, agent: String) -> void:
	if not requests.has(request_id):
		check(false, "physical passenger arrival has a matching coordinator request")
		return
	var event: Dictionary = requests[request_id]
	var passenger: CharacterBody3D = passengers[agent]
	var target: Vector3
	var safe_stop := ""
	if event.type == "boarding_requested":
		var platform: AnimatableBody3D = vehicles[event.details.vehicle]
		target = platform.global_position + Vector3(0, 0.7, 0.5 if agent == "east-rider-two" else 0.0)
	elif event.type == "alighting_requested":
		target = Vector3(2.4, 0.7, 4)
	else:
		target = Vector3(-6.5, 0.7, 0.8 if agent == "east-rider-two" else 0.0)
		safe_stop = "west"
	var valid := passenger.is_on_floor() and Vector2(passenger.global_position.x - target.x, passenger.global_position.z - target.z).length() < 0.35
	var accepted: bool = bridge.complete_movement(event, func(_request: Dictionary): return valid, safe_stop)
	check(accepted, "controller bridge accepts physical CharacterBody arrival " + event.type + " for " + agent)
	if accepted and event.type == "boarding_requested":
		var transform: Transform3D = passenger.global_transform
		var old_parent := passenger.get_parent()
		old_parent.remove_child(passenger)
		vehicles[event.details.vehicle].add_child(passenger)
		passenger.global_transform = transform
		passenger.set_physics_process(false)
	elif accepted and event.type == "recovery_requested":
		recovered[event.agent] = safe_stop
	requests.erase(request_id)

func _transit_event(event: Dictionary) -> void:
	if event.type == "departed":
		var id: String = event.details.vehicle
		dispatched[id] = dispatcher.dispatch(id)
	elif event.type == "recovery_requested":
		if not recovery_started:
			recovery_started = dispatcher.interrupt_to_safe_stop(event.details.vehicle, Vector3(-6.5, 0, 0))
			check(recovery_started, "first rider recovery request diverts the reconstructed physical vehicle")
	elif event.type == "recovered":
		recovered[event.agent] = event.details.stop

func _movement_requested(event: Dictionary) -> void:
	requests[event.id] = event.duplicate(true)
	var passenger: CharacterBody3D = passengers[event.agent]
	if event.type == "boarding_requested":
		var platform: AnimatableBody3D = vehicles[event.details.vehicle]
		passenger.set_physics_process(true)
		passenger.walk_to(platform.global_position + Vector3(0, 0.7, 0.5 if event.agent == "east-rider-two" else 0.0), event.id)
	elif event.type == "alighting_requested":
		_dismount(passenger)
		passenger.walk_to(Vector3(2.4, 0.7, 4), event.id)
	elif event.type == "recovery_requested":
		recovery_requests[event.agent] = event.duplicate(true)

func build_world(positions: Dictionary, snapshot: Dictionary, fleet_snapshot: Dictionary) -> bool:
	world = Node3D.new()
	root.add_child(world)
	var ground: StaticBody3D = StaticBody3D.new()
	var ground_shape := CollisionShape3D.new()
	var ground_box := BoxShape3D.new()
	ground_box.size = Vector3(40, 0.4, 40)
	ground_shape.shape = ground_box
	ground.add_child(ground_shape)
	ground.position = Vector3(0, -0.4, 0)
	world.add_child(ground)
	static_pad(Vector3(-4, 0, 2.5), Vector3(3, 0.4, 3.8))
	static_pad(Vector3(2.3, 0, -4), Vector3(2.8, 0.4, 3))
	vehicles["east-vehicle"] = vehicle(positions.get("east-vehicle", Vector3(-4, 0, 0)))
	vehicles["north-vehicle"] = vehicle(positions.get("north-vehicle", Vector3(0, 0, -4)))
	passengers["east-rider"] = make_passenger("east-rider", "east-vehicle", not snapshot.is_empty())
	passengers["east-rider-two"] = make_passenger("east-rider-two", "east-vehicle", not snapshot.is_empty())
	passengers["north-rider"] = make_passenger("north-rider", "north-vehicle", not snapshot.is_empty())
	transit = Transit.new()
	world.add_child(transit)
	var configured: bool
	if snapshot.is_empty():
		configured = transit.configure(cfg, "junction-restore")
	else:
		configured = transit.restore_snapshot(cfg, snapshot)
	if not configured:
		return false
	bridge = Bridge.new()
	world.add_child(bridge)
	if not bridge.configure(transit):
		return false
	dispatcher = Dispatcher.new()
	world.add_child(dispatcher)
	var junctions: Array[Vector3] = [Vector3.ZERO]
	dispatcher.junctions = junctions
	dispatcher.vehicle_arrived.connect(func(id: String): arrived[id] = true)
	dispatcher.vehicle_recovered.connect(func(id: String, safe_stop: Vector3):
		check(safe_stop == Vector3(-6.5, 0, 0), "reconstructed vehicle reaches the same safe stop")
		for agent in ["east-rider", "east-rider-two"]:
			var passenger: CharacterBody3D = passengers[agent]
			_dismount(passenger)
			passenger.walk_to(Vector3(-6.5, 0.7, 0.8 if agent == "east-rider-two" else 0.0), recovery_requests[agent].id)
	)
	var east_route: Array[Vector3] = [vehicles["east-vehicle"].position, Vector3(4, 0, 0)]
	var north_route: Array[Vector3] = [vehicles["north-vehicle"].position, Vector3(0, 0, 4)]
	var ok: bool = dispatcher.register_vehicle("east-vehicle", vehicles["east-vehicle"], east_route, 2.0, 1)
	ok = ok and dispatcher.register_vehicle("north-vehicle", vehicles["north-vehicle"], north_route, 2.0, 2)
	if not ok:
		return false
	if not fleet_snapshot.is_empty():
		recovery_started = bool(fleet_snapshot.get("vehicles", {}).get("east-vehicle", {}).get("recovering", false))
		var before: Dictionary = dispatcher.save_snapshot()
		var invalid_snapshots: Array[Dictionary] = []
		var unknown_version: Dictionary = fleet_snapshot.duplicate(true)
		unknown_version.version = 99
		invalid_snapshots.append(unknown_version)
		var unknown_junction: Dictionary = fleet_snapshot.duplicate(true)
		unknown_junction.junctions[0] = Vector3(8, 0, 0)
		invalid_snapshots.append(unknown_junction)
		var short_route: Dictionary = fleet_snapshot.duplicate(true)
		short_route.vehicles["east-vehicle"].route = [Vector3.ZERO]
		invalid_snapshots.append(short_route)
		var negative_wait: Dictionary = fleet_snapshot.duplicate(true)
		negative_wait.vehicles["north-vehicle"].wait_count = -1
		invalid_snapshots.append(negative_wait)
		for invalid in invalid_snapshots:
			check(not dispatcher.restore_snapshot(invalid), "dispatcher rejects malformed fleet, junction or route state")
			check(dispatcher.save_snapshot() == before, "invalid dispatcher snapshot leaves registered routes unchanged")
		ok = dispatcher.restore_snapshot(fleet_snapshot)
	if snapshot.is_empty():
		bridge.movement_requested.connect(_movement_requested)
		transit.transit_event.connect(_transit_event)
		ok = transit.request_journey("east-rider", "west", "east") and transit.request_journey("east-rider-two", "west", "east") and transit.request_journey("north-rider", "south", "north")
		ok = ok and transit.begin_tick() and transit.open_boarding()
	else:
		bridge.movement_requested.connect(_movement_requested)
		transit.transit_event.connect(_transit_event)
		var east_state: String = transit.journey("east-rider").state
		var east_two_state: String = transit.journey("east-rider-two").state
		ok = east_state in ["onboard", "stranded"] and east_two_state in ["onboard", "stranded"] and transit.journey("north-rider").state == "onboard"
		if ok and east_state == "stranded":
			ok = bridge.refresh_request("east-rider") and bridge.refresh_request("east-rider-two")
	return ok

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	check(build_world({}, {}, {}), "initial scene configures and opens physical boarding")
	for _frame in range(360):
		await physics_frame
		if transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("east-rider-two").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed":
			break
	check(transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("east-rider-two").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed", "three CharacterBody passengers physically board, with two sharing capacity two")
	check(transit.finish_tick(), "coordinator departs physically boarded passengers")
	var saved := false
	var snapshot := {}
	var fleet_snapshot := {}
	var positions := {}
	for _frame in range(300):
		await physics_frame
		if dispatcher.waiting_frames("north-vehicle") > 0 and vehicles["east-vehicle"].position.distance_to(Vector3.ZERO) < 0.15:
			var result: Dictionary = transit.save_snapshot()
			saved = result.get("ok", false)
			if saved:
				snapshot = result.snapshot
				fleet_snapshot = dispatcher.save_snapshot()
				positions = {"east-vehicle":vehicles["east-vehicle"].position, "north-vehicle":vehicles["north-vehicle"].position}
			break
	check(saved and fleet_snapshot.get("version") == 1, "save versioned dispatcher, coordinator and vehicle positions during reserved crossing")
	if not saved:
		world.queue_free()
		await process_frame
		quit(1)
		return
	world.queue_free()
	await process_frame
	vehicles.clear()
	passengers.clear()
	recovery_requests.clear()
	dispatched.clear()
	arrived.clear()
	recovered.clear()
	check(build_world(positions, snapshot, fleet_snapshot), "rebuild coordinator and physical fleet from trusted crossing state")
	var recovery_snapshot := {}
	var recovery_fleet_snapshot := {}
	var recovery_positions := {}
	for _frame in range(360):
		await physics_frame
		var east: AnimatableBody3D = vehicles["east-vehicle"]
		var north: AnimatableBody3D = vehicles["north-vehicle"]
		if absf(east.position.x - north.position.x) < 2.0 and absf(east.position.z - north.position.z) < 2.0:
			overlap_seen = true
		if not disabled and dispatcher.waiting_frames("north-vehicle") > 0 and east.position.distance_to(Vector3.ZERO) < 0.6:
			disabled = transit.set_service_enabled("eastbound", false)
			check(disabled and recovery_requests.size() == 2, "service interruption requests recovery for both shared-vehicle riders")
		if disabled and east.position.x < -1.25 and east.position.x > -5.5:
			var coordinator_state: Dictionary = transit.save_snapshot()
			if coordinator_state.get("ok", false):
				recovery_snapshot = coordinator_state.snapshot
				recovery_fleet_snapshot = dispatcher.save_snapshot()
				recovery_positions = {"east-vehicle":east.position, "north-vehicle":north.position}
			break
	check(not recovery_snapshot.is_empty() and recovery_fleet_snapshot.get("vehicles", {}).get("east-vehicle", {}).get("recovering", false), "save coordinator and recovering vehicle state during safe-stop travel")
	if not recovery_snapshot.is_empty():
		world.queue_free()
		await process_frame
		vehicles.clear()
		passengers.clear()
		recovery_requests.clear()
		dispatched.clear()
		arrived.clear()
		recovered.clear()
		disabled = true
		check(build_world(recovery_positions, recovery_snapshot, recovery_fleet_snapshot), "restore bridge and dispatcher during active safe-stop recovery")
	var did_restore := not recovery_requests.is_empty()
	for _frame in range(600):
		await physics_frame
		var east: AnimatableBody3D = vehicles["east-vehicle"]
		var north: AnimatableBody3D = vehicles["north-vehicle"]
		if absf(east.position.x - north.position.x) < 2.0 and absf(east.position.z - north.position.z) < 2.0:
			overlap_seen = true
		if not recovery_requests.is_empty():
			did_restore = true
		if arrived.has("north-vehicle") and recovered.get("east-rider", "") == "west" and recovered.get("east-rider-two", "") == "west":
			break
	check(did_restore, "restored physical dispatch responded to service interruption")
	check(not overlap_seen, "platform bounds stay separate across save, reconstruction and recovery")
	check(arrived.has("north-vehicle") and recovered.get("east-rider", "") == "west" and recovered.get("east-rider-two", "") == "west", "both recovered riders and the crossing vehicle reach their physical endpoints")
	check(transit.journey("north-rider").state == "onboard" and transit.begin_tick(), "restored coordinator advances after northbound arrival")
	for _frame in range(300):
		await physics_frame
		if transit.journey("north-rider").state == "completed":
			break
	check(transit.journey("north-rider").state == "completed", "northbound CharacterBody walks off and alights through the restored coordinator")
	check(transit.inspect_vehicle("east-vehicle").ledger.aboard.is_empty() and transit.inspect_vehicle("north-vehicle").ledger.aboard.is_empty(), "all restored vehicle seats release")
	var east_position: Vector3 = passengers["east-rider"].global_position
	var east_two_position: Vector3 = passengers["east-rider-two"].global_position
	var north_position: Vector3 = passengers["north-rider"].global_position
	check(passengers["east-rider"].is_on_floor() and passengers["east-rider-two"].is_on_floor() and passengers["north-rider"].is_on_floor() and Vector2(east_position.x + 6.5, east_position.z).length() < 0.35 and Vector2(east_two_position.x + 6.5, east_two_position.z - 0.8).length() < 0.35 and Vector2(north_position.x - 2.4, north_position.z - 4.0).length() < 0.35, "all CharacterBody passengers reach safe stop and destination on foot")
	print("Temporary game capacity-two crossing reconstruction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; shared riders, crossing save/restore and shared recovery)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
