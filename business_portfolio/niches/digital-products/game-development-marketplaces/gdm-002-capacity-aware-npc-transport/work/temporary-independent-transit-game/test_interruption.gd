extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Character = preload("res://passenger_controller.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func surface(size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var node: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var collision := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	collision.shape = box
	node.add_child(collision)
	node.position = position
	return node
func wait_state(transit: Node, state: String, frames: int) -> bool:
	for i in range(frames):
		await physics_frame
		if transit.journey("rider").get("state") == state: return true
	return false
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var platform = surface(Vector3(3,0.4,3),Vector3.ZERO,true)
	world.add_child(platform)
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(-2.5,0,0),false))
	var body = Character.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	body.add_child(shape)
	body.position = Vector3(-2.5,0.75,0)
	world.add_child(body)
	var transit = Transit.new()
	var bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"independent-interruption-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"service","vehicle":"v","from":"a","to":"b","period":10,"offset":0,"duration":2,"enabled":true}]}
	var requests := {}
	bridge.movement_requested.connect(func(event):
		requests[event.type] = event
		if event.type == "boarding_requested": body.start_motion(Vector3(0,0.7,0),event.id)
	)
	bridge.request_withdrawn.connect(func(_agent,id,_reason): body.stop_motion(id))
	body.motion_finished.connect(func(id):
		if requests.has("boarding_requested") and id == requests.boarding_requested.id:
			check(bridge.complete_movement(requests.boarding_requested,func(_event): return body.is_on_floor() and absf(body.position.x-platform.position.x)<0.4), "physically boarded")
		elif requests.has("recovery_requested") and id == requests.recovery_requested.id:
			check(bridge.complete_movement(requests.recovery_requested,func(_event): return body.is_on_floor() and absf(body.position.x+2.5)<0.25,"a"), "physically recovered")
	)
	check(transit.configure(cfg,"interruption") and bridge.configure(transit), "configure")
	check(transit.request_journey("rider","a","b"), "request")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "boarding window")
	check(await wait_state(transit,"boarding_confirmed",180), "board before departure")
	check(transit.finish_tick(), "depart")
	for i in range(60):
		await physics_frame
		platform.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x-platform.position.x)<0.5, "passenger rides platform")
	check(transit.set_service_enabled("service",false), "interrupt service")
	check(requests.has("recovery_requested") and transit.inspect_vehicle("v").ledger.aboard.size() == 1, "seat held until recovery")
	for i in range(60):
		await physics_frame
		platform.position.x -= 0.02
	if requests.has("recovery_requested"):
		body.start_motion(Vector3(-2.5,0.7,0),requests.recovery_requested.id)
	for i in range(180):
		await physics_frame
		if transit.inspect_vehicle("v").ledger.aboard.is_empty(): break
	check(transit.inspect_vehicle("v").ledger.aboard.is_empty(), "seat released after safe exit")
	print("Independent temporary game interruption: ", "PASS" if failures == 0 else "FAIL", " (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
