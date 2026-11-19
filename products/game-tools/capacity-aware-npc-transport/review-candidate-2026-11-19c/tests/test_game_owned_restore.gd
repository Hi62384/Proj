extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Character = preload("res://examples/game_owned_character.gd")
var failures := 0
var world: Node3D
var body
var transit
var bridge
var requests := {}
var targets := {}
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
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
func bind_bridge() -> void:
	bridge.movement_requested.connect(_on_request)
	bridge.request_withdrawn.connect(_on_withdrawn)
func _on_request(event: Dictionary) -> void:
	var x := 0.0
	if event.type == "boarding_requested": x = 0.0 if event.details.vehicle == "v1" else 7.5
	else: x = 5.0 if event.details.stop == "hub" else 12.5
	requests[event.id] = event
	targets[event.id] = x
	body.start_motion(Vector3(x,0.7,0),event.id)
func _on_withdrawn(_agent: String, id: String, _reason: String) -> void:
	if is_instance_valid(body): body.stop_motion(id)
func _on_finished(id: String) -> void:
	var target: float = targets[id]
	check(bridge.complete_movement(requests[id],func(_event): return is_instance_valid(body) and body.is_on_floor() and absf(body.position.x-target)<0.25),"verified physical completion")
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
	var first = surface(Vector3(3,0.4,3),Vector3.ZERO,true)
	var second = surface(Vector3(3,0.4,3),Vector3(7.5,0,0),true)
	world.add_child(first)
	world.add_child(second)
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(-2.5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(12.5,0,0),false))
	create_body(Vector3(-2.5,0.75,0),Vector3.ZERO)
	transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"owned-restore-v1","tick_unit":"simulation_tick","stops":["a","hub","end"],"vehicles":[{"id":"v1","capacity":1},{"id":"v2","capacity":1}],"services":[{"id":"first","vehicle":"v1","from":"a","to":"hub","period":10,"offset":0,"duration":2,"enabled":true},{"id":"second","vehicle":"v2","from":"hub","to":"end","period":10,"offset":2,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"owned-restore") and bridge.configure(transit),"configure")
	bind_bridge()
	check(transit.request_journey("rider","a","end"),"request")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(),"boarding window")
	for i in range(15): await physics_frame
	check(transit.journey("rider").state == "boarding" and body.position.x < -1.5,"save mid-walk")
	var pending: Dictionary = transit.pending_request("rider")
	var saved: Dictionary = transit.save_snapshot()
	check(saved.ok,"snapshot")
	var file := FileAccess.open("user://owned-controller-save.dat",FileAccess.WRITE)
	file.store_var({"core":saved.snapshot,"position":body.position,"velocity":body.velocity})
	file.close()
	bridge.detach()
	bridge.queue_free()
	transit.queue_free()
	body.queue_free()
	await process_frame
	file = FileAccess.open("user://owned-controller-save.dat",FileAccess.READ)
	var disk: Dictionary = file.get_var(false)
	file.close()
	create_body(disk.position,disk.velocity)
	transit = Transit.new()
	bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	check(transit.restore_snapshot(cfg,disk.core) and bridge.configure(transit),"restore new coordinator and bridge")
	bind_bridge()
	check(transit.pending_request("rider").id == pending.id and bridge.refresh_request("rider"),"restart same pending request")
	check(await wait_state("boarding_confirmed",180),"restored character boards")
	check(transit.finish_tick(),"first depart")
	for i in range(120):
		await physics_frame
		first.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x-first.position.x)<0.5,"first ride")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"first arrival")
	check(await wait_state("queued",180),"first exit")
	check(transit.open_boarding(),"second window")
	check(await wait_state("boarding_confirmed",180),"second boarding")
	check(transit.finish_tick(),"second depart")
	for i in range(120):
		await physics_frame
		second.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x-second.position.x)<0.5,"second ride")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"second arrival")
	check(await wait_state("completed",180),"complete restored journey")
	check(transit.inspect_vehicle("v1").ledger.aboard.is_empty() and transit.inspect_vehicle("v2").ledger.aboard.is_empty(),"no occupied seats remain")
	print("Game-owned controller recreated restore: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
