extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Npc = preload("res://npc.gd")
var failures := 0
var passengers := {}
var requests := {}
var bridge: Node
var platforms := {}
var started := {}
var returning := {}
var recovery_events := {}
var recovered := {}
var targets := {"east-service": Vector3(2.4, 0, -2), "east-alt": Vector3(2.4, 0, -2), "north-service": Vector3(0, 0, 4.4)}
var homes := {"east-service": Vector3(0, 0, -2), "east-alt": Vector3(0, 0, -2), "north-service": Vector3(0, 0, 2)}
var exit_points := {"east-rider": Vector3(5, 0.7, -2), "north-rider": Vector3(0, 0.7, 5.8)}
var speeds := {"east-service": 2.4, "east-alt": 2.0, "north-service": 1.5}
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func surface(world: Node, size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var body: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	body.position = position
	world.add_child(body)
	return body
func route_for_vehicle(vehicle: String) -> String:
	return "east-service" if vehicle == "e" else "north-service"
func _transit_event(event: Dictionary) -> void:
	if event.type == "departed":
		started[event.details.service] = true
	elif event.type == "recovery_requested":
		var service: String = event.details.service
		recovery_events[event.agent] = event.duplicate(true)
		started[service] = false
		returning[service] = true
	elif event.type == "recovered":
		recovered[event.agent] = event.details.stop
func _requested(event: Dictionary) -> void:
	requests[event.id] = event
	if event.type == "boarding_requested":
		passengers[event.agent].walk_to(Vector3(0, 0.7, -2 if event.agent == "east-rider" else 2), event.id)
	elif event.type == "alighting_requested":
		passengers[event.agent].walk_to(exit_points[event.agent], event.id)
	else:
		requests[event.id] = event
func _reached(id: String, agent: String) -> void:
	var event: Dictionary = requests[id]
	var npc: CharacterBody3D = passengers[agent]
	var valid := npc.is_on_floor()
	if event.type == "boarding_requested":
		valid = valid and absf(npc.position.x) < 0.25 and absf(npc.position.z - (-2 if agent == "east-rider" else 2)) < 0.25
	elif event.type == "alighting_requested":
		valid = valid and npc.global_position.distance_to(exit_points[agent]) < 0.35
	else:
		valid = valid and npc.global_position.distance_to(homes[event.details.service] + Vector3(0, 0.5, 0)) < 0.35
	var safe_stop := "dock" if event.type == "recovery_requested" else ""
	check(bridge.complete_movement(event, func(_event): return valid, safe_stop), "verified physical movement " + agent)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	surface(world, Vector3(3, 0.4, 7), Vector3(-2.5, 0, 0), false)
	surface(world, Vector3(4, 0.4, 3), Vector3(4.4, 0, -2), false)
	surface(world, Vector3(3, 0.4, 4), Vector3(0, 0, 5.4), false)
	platforms["e"] = surface(world, Vector3(3, 0.4, 2.5), Vector3(0, 0, -2), true)
	platforms["w"] = surface(world, Vector3(3, 0.4, 2.5), Vector3(0, 0, 2), true)
	for id in ["east-rider", "north-rider"]:
		var npc: CharacterBody3D = Npc.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		var shape := CollisionShape3D.new()
		shape.shape = capsule
		npc.add_child(shape)
		npc.collision_layer = 2
		npc.collision_mask = 1
		npc.position = Vector3(-2.5, 0.75, -2 if id == "east-rider" else 2)
		world.add_child(npc)
		passengers[id] = npc
		npc.reached.connect(_reached.bind(id))
	var transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	transit.transit_event.connect(_transit_event)
	bridge.movement_requested.connect(_requested)
	var cfg := {"revision":"mapped-physical-v1", "tick_unit":"simulation_tick", "stops":["dock", "east", "north"], "vehicles":[{"id":"e", "capacity":1}, {"id":"w", "capacity":1}], "services":[{"id":"east-service", "vehicle":"e", "from":"dock", "to":"east", "period":4, "offset":0, "duration":1, "enabled":true}, {"id":"east-alt", "vehicle":"e", "from":"dock", "to":"east", "period":4, "offset":1, "duration":1, "enabled":true}, {"id":"north-service", "vehicle":"w", "from":"dock", "to":"north", "period":4, "offset":0, "duration":1, "enabled":true}]}
	check(transit.configure(cfg, "mapped-physical") and bridge.configure(transit), "configure mapped services")
	check(transit.request_journey("east-rider", "dock", "east") and transit.request_journey("north-rider", "dock", "north"), "independent destination requests")
	for _frame in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "open dispatch")
	for _frame in range(240):
		await physics_frame
		if transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed": break
	check(transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed", "both physically board their assigned vehicles")
	check(transit.finish_tick(), "depart confirmed journeys")
	var disabled := false
	for frame in range(300):
		await physics_frame
		for service in ["east-service", "east-alt", "north-service"]:
			var vehicle := "w" if service == "north-service" else "e"
			var platform: AnimatableBody3D = platforms[vehicle]
			var step: float = float(speeds[service]) / float(Engine.physics_ticks_per_second)
			if returning.get(service, false):
				var home_offset: Vector3 = homes[service] - platform.position
				platform.position += home_offset.normalized() * minf(home_offset.length(), step)
				if platform.position.distance_to(homes[service]) < 0.02:
					returning[service] = false
					started[service + "_recovered_home"] = true
					var event: Dictionary = recovery_events["east-rider" if vehicle == "e" else "north-rider"]
					passengers[event.agent].walk_to(passengers[event.agent].global_position, event.id)
			elif started.get(service, false):
				var offset: Vector3 = targets[service] - platform.position
				platform.position += offset.normalized() * minf(offset.length(), step)
				if platform.position.distance_to(targets[service]) < 0.02:
					started[service] = false
					started[service + "_arrived"] = true
		if frame == 30 and not disabled:
			disabled = transit.set_service_enabled("east-service", false)
			check(disabled, "disable east service during physical travel")
		if started.get("east-service_recovered_home", false) and not recovery_events.is_empty() and recovered.has("east-rider") and started.get("north-service_arrived", false): break
	check(started.get("north-service_arrived", false), "unaffected northbound vehicle reaches its mapped destination")
	check(started.get("east-service_recovered_home", false) and recovered.get("east-rider") == "dock", "interrupted eastbound vehicle physically returns passenger to safe dock")
	check(transit.journey("east-rider").state == "queued" and transit.journey("east-rider").service == "east-alt", "recovery reroutes passenger to the available alternate service")
	check(passengers["north-rider"].is_on_floor() and passengers["north-rider"].global_position.distance_to(targets["north-service"] + Vector3(0, 0.5, 0)) < 0.55, "north passenger rides assigned moving platform")
	check(transit.begin_tick(), "arrival tick issues alighting")
	for _frame in range(300):
		await physics_frame
		if transit.journey("north-rider").state == "completed": break
	check(transit.journey("north-rider").state == "completed", "unaffected passenger reaches mapped stop")
	check(transit.open_boarding(), "alighting phase closes after physical acknowledgments")
	for _frame in range(240):
		await physics_frame
		if transit.journey("east-rider").state == "boarding_confirmed": break
	check(transit.journey("east-rider").state == "boarding_confirmed", "recovered passenger boards alternate departure")
	check(transit.finish_tick(), "alternate service departs")
	for _frame in range(300):
		await physics_frame
		var platform: AnimatableBody3D = platforms["e"]
		if started.get("east-alt", false):
			var offset: Vector3 = targets["east-alt"] - platform.position
			var step: float = float(speeds["east-alt"]) / float(Engine.physics_ticks_per_second)
			platform.position += offset.normalized() * minf(offset.length(), step)
			if platform.position.distance_to(targets["east-alt"]) < 0.02:
				started["east-alt"] = false
				started["east-alt_arrived"] = true
		if started.get("east-alt_arrived", false): break
	check(started.get("east-alt_arrived", false), "alternate service physically carries passenger to east stop")
	check(passengers["east-rider"].is_on_floor() and passengers["east-rider"].global_position.distance_to(targets["east-alt"] + Vector3(0, 0.5, 0)) < 0.55, "passenger rides the recovered vehicle on its alternate dispatch")
	check(transit.begin_tick(), "alternate arrival")
	for _frame in range(300):
		await physics_frame
		if transit.journey("east-rider").state == "completed": break
	check(transit.journey("east-rider").state == "completed", "alternate-service passenger exits at destination")
	check(transit.open_boarding(), "alternate alighting phase closes")
	check(transit.inspect_vehicle("e").ledger.aboard.is_empty() and transit.inspect_vehicle("w").ledger.aboard.is_empty(), "both vehicle seats released after recovery and exits")
	print("Temporary game mapped physical dispatch recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; safe return and alternate service)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
