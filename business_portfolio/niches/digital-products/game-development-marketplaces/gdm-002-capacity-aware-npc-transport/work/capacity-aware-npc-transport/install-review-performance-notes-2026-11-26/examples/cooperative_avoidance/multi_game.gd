extends Node3D
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Npc = preload("res://examples/cooperative_avoidance/npc.gd")
var transit: Node
var bridge: Node
var platform: AnimatableBody3D
var passengers := {}
var requests := {}
var stage := "settling"
var error := ""
var frames := 0
var departures := 0
var block_boarding := false
var auto_yield := false
var defer_second := false
var demand_dispatch := false
var wider_area := false
var two_destinations := false

func surface(size: Vector3, at: Vector3, moving: bool) -> Node3D:
	var body: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	body.position = at
	add_child(body)
	return body

func _ready() -> void:
	surface(Vector3(2.2, 0.4, 5 if wider_area else 3), Vector3(-2.5, 0, 0), false)
	surface(Vector3(4, 0.4, 3), Vector3(5.9, 0, 0), false)
	if two_destinations: surface(Vector3(3, 0.4, 4), Vector3(0, 0, 5.9), false)
	platform = surface(Vector3(3, 0.4, 5 if wider_area else 3), Vector3.ZERO, true)
	for id in ["first", "second"]:
		var npc = Npc.new()
		npc.cooperative_avoidance = auto_yield
		var shape := CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.25
		capsule.height = 1.0
		shape.shape = capsule
		npc.add_child(shape)
		npc.collision_layer = 2
		npc.collision_mask = 3 if block_boarding else 1
		npc.position = Vector3(-1.4, 0.75, lane("first")) if block_boarding and id == "second" else Vector3(-2.5, 0.75, lane(id))
		add_child(npc)
		passengers[id] = npc
		npc.reached.connect(_reached.bind(id))
	transit = Transit.new()
	bridge = Bridge.new()
	add_child(transit)
	add_child(bridge)
	var cfg := {"revision":"temporary-multi-v1", "tick_unit":"simulation_tick", "stops":["dock", "station"], "vehicles":[{"id":"ferry", "capacity":1}], "services":[{"id":"route", "vehicle":"ferry", "from":"dock", "to":"station", "period":3, "offset":0, "duration":2, "enabled":true}]}
	if two_destinations:
		cfg = {"revision":"temporary-two-routes-v1", "tick_unit":"simulation_tick", "stops":["dock", "station", "south"], "vehicles":[{"id":"ferry", "capacity":1}], "services":[{"id":"north", "vehicle":"ferry", "from":"dock", "to":"station", "period":6, "offset":0, "duration":2, "enabled":true}, {"id":"southbound", "vehicle":"ferry", "from":"dock", "to":"south", "period":6, "offset":3, "duration":2, "enabled":true}]}
	if not transit.configure(cfg, "temporary-multi") or not bridge.configure(transit):
		fail("configure: " + transit.last_error)
		return
	bridge.movement_requested.connect(_requested)
	bridge.request_withdrawn.connect(func(id, request_id, _reason): passengers[id].cancel_walk(request_id))
	if not transit.request_journey("first", "dock", "station"):
		fail("request")
	elif not defer_second and not transit.request_journey("second", "dock", "south" if two_destinations else "station"):
		fail("second request")

func lane(id: String) -> float:
	return -0.6 if id == "first" else 0.6

func fail(reason: String) -> void:
	error = reason
	stage = "failed"

func _requested(event: Dictionary) -> void:
	requests[event.id] = event
	passengers[event.agent].walk_to(target(event), event.id)

func target(event: Dictionary) -> Vector3:
	if event.type == "boarding_requested": return Vector3(0, 0.7, lane(event.agent))
	if two_destinations and event.details.stop == "south": return Vector3(0, 0.7, 5.0)
	return Vector3(5, 0.7, lane(event.agent))

func _reached(request_id: String, agent: String) -> void:
	var event: Dictionary = requests[request_id]
	var npc: CharacterBody3D = passengers[agent]
	var destination := target(event)
	if not bridge.complete_movement(event, func(_event): return npc.is_on_floor() and Vector2(npc.position.x - destination.x, npc.position.z - destination.z).length() < 0.25):
		fail("acknowledge " + agent)

func _physics_process(delta: float) -> void:
	if stage in ["completed", "failed"]: return
	frames += 1
	if frames > 2500:
		fail("timeout")
		return
	if stage == "settling" and frames >= 30:
		if not transit.begin_tick() or not transit.open_boarding(): fail("first boarding")
		else: stage = "boarding_first"
	elif stage in ["boarding_first", "boarding_second"]:
		var agent := "first" if stage == "boarding_first" else "second"
		if transit.journey(agent).state == "boarding_confirmed":
			if not transit.finish_tick(): fail("depart")
			else:
				departures += 1
				stage = "sailing_first" if agent == "first" else "sailing_second"
	elif stage in ["sailing_first", "sailing_second"]:
		var first_trip := stage == "sailing_first"
		var npc: CharacterBody3D = passengers["first" if first_trip else "second"]
		if two_destinations and not first_trip: platform.position.z = minf(platform.position.z + 1.2 * delta, 2.4)
		else: platform.position.x = minf(platform.position.x + 1.2 * delta, 2.4)
		var arrived := platform.position.z >= 2.4 if two_destinations and not first_trip else platform.position.x >= 2.4
		if arrived:
			if not npc.is_on_floor() or Vector2(npc.position.x - platform.position.x, npc.position.z - platform.position.z).length() > 1.0:
				fail("passenger not aboard")
			elif not transit.begin_tick() or not transit.open_boarding() or not transit.finish_tick() or not transit.begin_tick():
				fail("arrive")
			else: stage = "alighting_first" if first_trip else "alighting_second"
	elif stage == "alighting_first" and transit.journey("first").state == "completed":
		if demand_dispatch:
			if not transit.open_boarding() or not transit.finish_tick(): fail("close arrival tick")
			else: stage = "waiting_demand"
		else: stage = "returning"
	elif stage == "waiting_demand":
		if transit.journey("second").get("state") == "queued": stage = "returning"
	elif stage == "returning":
		platform.position.x = maxf(platform.position.x - 1.2 * delta, 0.0)
		if platform.position.x <= 0.0:
			if demand_dispatch:
				if not transit.begin_tick() or not transit.open_boarding(): fail("second boarding after demand")
				else: stage = "boarding_second"
			else:
				if not transit.open_boarding() or not transit.finish_tick() or not transit.begin_tick() or not transit.open_boarding(): fail("second boarding")
				else: stage = "boarding_second"
	elif stage == "alighting_second" and transit.journey("second").state == "completed":
		stage = "completed"
