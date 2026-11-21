extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Npc = preload("res://npc.gd")
var failures := 0
var passengers := {}
var requests := {}
var destinations := {}
var bridge: Node
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
func lane(id: String) -> float:
	return -2.0 if id == "east-rider" else 2.0
func _requested(event: Dictionary) -> void:
	requests[event.id] = event
	if event.type == "alighting_requested": destinations[event.agent] = event.details.stop
	if event.type == "recovery_requested": destinations[event.agent] = "east" if "east" in event.details.safe_stops else "missing"
	var x := 0.0 if event.type == "boarding_requested" else 5.0
	passengers[event.agent].walk_to(Vector3(x, 0.7, lane(event.agent)), event.id)
func _reached(id: String, agent: String) -> void:
	var event: Dictionary = requests[id]
	var npc: CharacterBody3D = passengers[agent]
	var x := 0.0 if event.type == "boarding_requested" else 5.0
	var safe_stop := "east" if event.type == "recovery_requested" else ""
	check(bridge.complete_movement(event, func(_event): return npc.is_on_floor() and absf(npc.position.x - x) < 0.25 and absf(npc.position.z - lane(agent)) < 0.25, safe_stop), "physical acknowledgment " + agent)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	surface(world, Vector3(2.2, 0.4, 7), Vector3(-2.5, 0, 0), false)
	surface(world, Vector3(4, 0.4, 7), Vector3(5.9, 0, 0), false)
	var east = surface(world, Vector3(3, 0.4, 2.5), Vector3(0, 0, -2), true)
	var west = surface(world, Vector3(3, 0.4, 2.5), Vector3(0, 0, 2), true)
	for id in ["east-rider", "west-rider"]:
		var npc = Npc.new()
		var shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1
		shape.shape = capsule
		npc.add_child(shape)
		npc.collision_layer = 2
		npc.collision_mask = 1
		npc.position = Vector3(-2.5, 0.75, lane(id))
		world.add_child(npc)
		passengers[id] = npc
		npc.reached.connect(_reached.bind(id))
	var transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"physical-parallel-v1", "tick_unit":"simulation_tick", "stops":["dock", "east", "west"], "vehicles":[{"id":"e", "capacity":1}, {"id":"w", "capacity":1}], "services":[{"id":"east-service", "vehicle":"e", "from":"dock", "to":"east", "period":4, "offset":0, "duration":1, "enabled":true}, {"id":"west-service", "vehicle":"w", "from":"dock", "to":"west", "period":4, "offset":0, "duration":1, "enabled":true}]}
	check(transit.configure(cfg, "physical-parallel") and bridge.configure(transit), "configure")
	bridge.movement_requested.connect(_requested)
	check(transit.request_journey("east-rider", "dock", "east") and transit.request_journey("west-rider", "dock", "west"), "requests")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "boarding")
	for i in range(240):
		await physics_frame
		if transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("west-rider").state == "boarding_confirmed": break
	check(transit.journey("east-rider").state == "boarding_confirmed" and transit.journey("west-rider").state == "boarding_confirmed", "both board")
	check(transit.inspect_vehicle("e").ledger.aboard.size() == 1 and transit.inspect_vehicle("w").ledger.aboard.size() == 1, "both occupied")
	check(transit.finish_tick(), "simultaneous departure")
	for i in range(120):
		await physics_frame
		east.position.x += 0.02
		west.position.x += 0.02
	check(passengers["east-rider"].is_on_floor() and absf(passengers["east-rider"].position.x - east.position.x) < 0.5, "east ride")
	check(passengers["west-rider"].is_on_floor() and absf(passengers["west-rider"].position.x - west.position.x) < 0.5, "west ride")
	check(transit.set_service_enabled("east-service", false), "disable east while both aboard")
	check(transit.journey("east-rider").state == "stranded" and transit.inspect_vehicle("e").ledger.aboard.size() == 1, "east held for recovery")
	check(transit.journey("west-rider").state == "onboard" and transit.inspect_vehicle("w").ledger.aboard.size() == 1, "west remains aboard")
	check(transit.begin_tick(), "west arrival while east recovers")
	for i in range(240):
		await physics_frame
		if transit.journey("east-rider").state == "completed" and transit.journey("west-rider").state == "completed": break
	check(transit.journey("east-rider").state == "completed" and transit.journey("west-rider").state == "completed", "both complete")
	check(destinations.get("east-rider") == "east" and destinations.get("west-rider") == "west", "correct destination events")
	check(transit.inspect_vehicle("e").ledger.aboard.is_empty() and transit.inspect_vehicle("w").ledger.aboard.is_empty(), "both seats released")
	print("Temporary game parallel vehicle disruption: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; two passengers)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
