extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Character = preload("res://examples/game_owned_character.gd")
var failures := 0
var world: Node3D
var body: CharacterBody3D
var transit: Node
var bridge: Node
var requests := {}

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

func create_body(position: Vector3, velocity: Vector3) -> void:
	body = Character.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	body.add_child(shape)
	body.position = position
	body.velocity = velocity
	world.add_child(body)
	body.motion_finished.connect(_on_finished)

func _on_request(event: Dictionary) -> void:
	requests[event.id] = event
	var target := 0.0 if event.type == "boarding_requested" else 5.0
	body.start_motion(Vector3(target, 0.7, 0), event.id)

func _on_withdrawn(_agent: String, id: String, _reason: String) -> void:
	if is_instance_valid(body): body.stop_motion(id)

func _on_finished(id: String) -> void:
	var event: Dictionary = requests[id]
	var target := 0.0 if event.type == "boarding_requested" else 5.0
	var safe_stop := "" if event.type == "boarding_requested" else "end"
	check(bridge.complete_movement(event, func(_event): return is_instance_valid(body) and body.is_on_floor() and absf(body.position.x - target) < 0.25, safe_stop), "verified completion")

func connect_bridge() -> void:
	bridge.movement_requested.connect(_on_request)
	bridge.request_withdrawn.connect(_on_withdrawn)

func wait_state(state: String, frames: int) -> bool:
	for i in range(frames):
		await physics_frame
		if transit.journey("rider").get("state") == state: return true
	return false

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	world = Node3D.new()
	root.add_child(world)
	var platform = surface(Vector3(3, 0.4, 3), Vector3.ZERO, true)
	world.add_child(platform)
	world.add_child(surface(Vector3(2.2, 0.4, 3), Vector3(-2.5, 0, 0), false))
	world.add_child(surface(Vector3(4, 0.4, 3), Vector3(5.9, 0, 0), false))
	create_body(Vector3(-2.5, 0.75, 0), Vector3.ZERO)
	transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"owned-disruption-restore-v1", "tick_unit":"simulation_tick", "stops":["origin","end"], "vehicles":[{"id":"lift","capacity":1}], "services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(cfg, "owned-disruption-restore") and bridge.configure(transit), "configure")
	connect_bridge()
	check(transit.request_journey("rider", "origin", "end"), "request")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "boarding window")
	check(await wait_state("boarding_confirmed", 180), "walk onto platform")
	check(transit.finish_tick(), "depart")
	for i in range(120):
		await physics_frame
		platform.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x - platform.position.x) < 0.5, "ride platform")
	check(transit.set_service_enabled("out", false), "disable while onboard")
	var pending: Dictionary = transit.pending_request("rider")
	check(pending.get("type") == "recovery_requested", "pending recovery")
	for i in range(15): await physics_frame
	check(transit.journey("rider").state == "stranded" and body.position.x < 4.0, "save while recovering")
	var snapshot: Dictionary = transit.save_snapshot()
	check(snapshot.ok, "save snapshot")
	var file := FileAccess.open("user://owned-disruption-restore.dat", FileAccess.WRITE)
	file.store_var({"core":snapshot.snapshot, "position":body.position, "velocity":body.velocity, "platform":platform.position})
	file.close()
	bridge.detach()
	bridge.queue_free()
	transit.queue_free()
	body.queue_free()
	platform.queue_free()
	await process_frame
	file = FileAccess.open("user://owned-disruption-restore.dat", FileAccess.READ)
	var disk: Dictionary = file.get_var(false)
	file.close()
	platform = surface(Vector3(3, 0.4, 3), disk.platform, true)
	world.add_child(platform)
	create_body(disk.position, disk.velocity)
	transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	check(transit.restore_snapshot(cfg, disk.core) and bridge.configure(transit), "recreate and restore")
	connect_bridge()
	check(transit.journey("rider").state == "stranded" and transit.inspect_vehicle("lift").ledger.aboard.size() == 1, "seat remains occupied after restore")
	check(transit.pending_request("rider").id == pending.id and bridge.refresh_request("rider"), "restart same recovery")
	check(not bridge.complete_movement(requests[pending.id], func(_event): return false, "end"), "unverified recovery rejected after restore")
	check(transit.inspect_vehicle("lift").ledger.aboard.size() == 1, "seat retained until arrival")
	check(await wait_state("completed", 240), "restored controller reaches station")
	check(transit.inspect_vehicle("lift").ledger.aboard.is_empty(), "seat released on recovery")
	print("Game-owned disruption recovery restore: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; one passenger)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
