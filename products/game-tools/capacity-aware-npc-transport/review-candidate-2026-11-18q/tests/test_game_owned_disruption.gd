extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Character = preload("res://examples/game_owned_character.gd")
var failures := 0
var requests := {}
var recovery := {}
var body: CharacterBody3D
var bridge: Node

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)

func surface(size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var node: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	node.add_child(shape)
	node.position = position
	return node

func wait_state(transit: Node, state: String, frames: int) -> bool:
	for i in range(frames):
		await physics_frame
		if transit.journey("rider").get("state") == state:
			return true
	return false

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var platform = surface(Vector3(3, 0.4, 3), Vector3.ZERO, true)
	world.add_child(platform)
	world.add_child(surface(Vector3(2.2, 0.4, 3), Vector3(-2.5, 0, 0), false))
	world.add_child(surface(Vector3(4, 0.4, 3), Vector3(5.9, 0, 0), false))
	body = Character.new()
	var collision := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	collision.shape = capsule
	body.add_child(collision)
	body.position = Vector3(-2.5, 0.75, 0)
	world.add_child(body)
	var transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"owned-disruption-v1", "tick_unit":"simulation_tick", "stops":["origin","end"], "vehicles":[{"id":"lift","capacity":1}], "services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(cfg, "owned-disruption") and bridge.configure(transit), "configure")
	bridge.movement_requested.connect(func(event):
		requests[event.id] = event
		if event.type == "boarding_requested":
			body.start_motion(Vector3(0, 0.7, 0), event.id)
		elif event.type == "recovery_requested":
			recovery.merge(event, true)
			body.start_motion(Vector3(5.0, 0.7, 0), event.id)
	)
	bridge.request_withdrawn.connect(func(_agent, id, _reason): body.stop_motion(id))
	body.motion_finished.connect(func(id):
		var event: Dictionary = requests[id]
		var expected := 0.0 if event.type == "boarding_requested" else 5.0
		var safe_stop := "" if event.type == "boarding_requested" else "end"
		check(bridge.complete_movement(event, func(_event): return body.is_on_floor() and absf(body.position.x - expected) < 0.25, safe_stop), "physical confirmation " + id)
	)
	check(transit.request_journey("rider", "origin", "end"), "request")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "boarding window")
	check(await wait_state(transit, "boarding_confirmed", 180), "walk onto platform")
	check(transit.finish_tick(), "depart")
	for i in range(120):
		await physics_frame
		platform.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x - platform.position.x) < 0.5, "ride platform")
	check(transit.set_service_enabled("out", false), "disable while onboard")
	check(transit.journey("rider").state == "stranded" and not recovery.is_empty(), "recovery requested")
	check(not bridge.complete_movement(recovery, func(_event): return false, "end"), "unverified recovery rejected")
	check(transit.journey("rider").state == "stranded", "still stranded before arrival")
	var before: Dictionary = transit.inspect_vehicle("lift")
	check(before.get("ledger", {}).get("aboard", []).size() == 1, "seat remains occupied before arrival")
	check(await wait_state(transit, "completed", 240), "physically reach station and complete")
	var after: Dictionary = transit.inspect_vehicle("lift")
	check(after.get("ledger", {}).get("aboard", []).is_empty(), "seat released after verified recovery")
	print("Game-owned physical disruption recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; one passenger)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
