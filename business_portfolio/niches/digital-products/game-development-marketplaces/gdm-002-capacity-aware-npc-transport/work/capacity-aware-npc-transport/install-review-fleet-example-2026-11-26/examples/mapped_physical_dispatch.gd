# Two configured services with game-owned scripted movement, not general vehicle pathfinding.
extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Npc = preload("res://examples/cooperative_avoidance/npc.gd")
var failures := 0
var passengers := {}
var requests := {}
var bridge: Node
var platforms := {}
var started := {}
var targets := {"east-service": Vector3(2.4, 0, -2), "north-service": Vector3(0, 0, 4.4)}
var exit_points := {"east-rider": Vector3(5, 0.7, -2), "north-rider": Vector3(0, 0.7, 5.8)}
var speeds := {"east-service": 2.4, "north-service": 1.5}
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
		started[route_for_vehicle(event.details.vehicle)] = true
func _requested(event: Dictionary) -> void:
	requests[event.id] = event
	if event.type == "boarding_requested":
		passengers[event.agent].walk_to(Vector3(0, 0.7, -2 if event.agent == "east-rider" else 2), event.id)
	else:
		passengers[event.agent].walk_to(exit_points[event.agent], event.id)
func _reached(id: String, agent: String) -> void:
	var event: Dictionary = requests[id]
	var npc: CharacterBody3D = passengers[agent]
	var valid := npc.is_on_floor()
	if event.type == "boarding_requested":
		valid = valid and absf(npc.position.x) < 0.25 and absf(npc.position.z - (-2 if agent == "east-rider" else 2)) < 0.25
	else:
		valid = valid and npc.global_position.distance_to(exit_points[agent]) < 0.35
	check(bridge.complete_movement(event, func(_event): return valid), "verified physical movement " + agent)
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
	var cfg := {"revision":"mapped-physical-v1", "tick_unit":"simulation_tick", "stops":["dock", "east", "north"], "vehicles":[{"id":"e", "capacity":1}, {"id":"w", "capacity":1}], "services":[{"id":"east-service", "vehicle":"e", "from":"dock", "to":"east", "period":4, "offset":0, "duration":1, "enabled":true}, {"id":"north-service", "vehicle":"w", "from":"dock", "to":"north", "period":4, "offset":0, "duration":1, "enabled":true}]}
	check(transit.configure(cfg, "mapped-physical") and bridge.configure(transit), "configure mapped services")
	check(transit.request_journey("east-rider", "dock", "east") and transit.request_journey("north-rider", "dock", "north"), "independent destination requests")
	for _frame in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "open dispatch")
	for _frame in range(240):
		await physics_frame
		if transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed": break
	check(transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("north-rider").state == "boarding_confirmed", "both physically board their assigned vehicles")
	check(transit.finish_tick(), "depart confirmed journeys")
	for _frame in range(240):
		await physics_frame
		for vehicle in ["e", "w"]:
			var service := route_for_vehicle(vehicle)
			if not started.get(service, false): continue
			var platform: AnimatableBody3D = platforms[vehicle]
			var offset: Vector3 = targets[service] - platform.position
			var step: float = float(speeds[service]) / float(Engine.physics_ticks_per_second)
			platform.position += offset.normalized() * minf(offset.length(), step)
			if platform.position.distance_to(targets[service]) < 0.02:
				started[service] = false
				started[service + "_arrived"] = true
		if started.get("east-service_arrived", false) and started.get("north-service_arrived", false): break
	check(started.get("east-service_arrived", false) and started.get("north-service_arrived", false), "event-triggered vehicle-specific mapped routes arrive")
	for vehicle in ["e", "w"]:
		var service := route_for_vehicle(vehicle)
		var expected: Vector3 = targets[service]
		var agent := "east-rider" if vehicle == "e" else "north-rider"
		check(passengers[agent].is_on_floor() and passengers[agent].global_position.distance_to(expected + Vector3(0, 0.5, 0)) < 0.55, "passenger rides assigned moving platform " + vehicle)
	check(transit.begin_tick(), "arrival tick issues alighting")
	for _frame in range(300):
		await physics_frame
		if transit.journey("east-rider").state == "completed" and transit.journey("north-rider").state == "completed": break
	check(transit.journey("east-rider").state == "completed" and transit.journey("north-rider").state == "completed", "both passengers reach mapped stops")
	check(transit.open_boarding(), "alighting phase closes after physical acknowledgments")
	check(transit.inspect_vehicle("e").ledger.aboard.is_empty() and transit.inspect_vehicle("w").ledger.aboard.is_empty(), "both vehicle seats released after verified exits")
	print("Mapped physical dispatch example: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; two services with distinct paths and speeds)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
