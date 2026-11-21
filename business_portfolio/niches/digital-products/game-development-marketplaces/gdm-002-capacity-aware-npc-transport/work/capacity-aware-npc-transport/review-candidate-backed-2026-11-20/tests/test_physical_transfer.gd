extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func make_surface(size: Vector3, position: Vector3, moving: bool) -> Node3D:
	var surface: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	surface.add_child(shape)
	surface.position = position
	return surface
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var first = make_surface(Vector3(3,0.4,3),Vector3.ZERO,true)
	var second = make_surface(Vector3(3,0.4,3),Vector3(7.5,0,0),true)
	world.add_child(first)
	world.add_child(second)
	world.add_child(make_surface(Vector3(2.2,0.4,3),Vector3(5.0,0,0),false))
	world.add_child(make_surface(Vector3(2.2,0.4,3),Vector3(12.5,0,0),false))
	var body := CharacterBody3D.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	body.add_child(shape)
	body.position = Vector3(0,0.75,0)
	world.add_child(body)
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var cfg := {"revision":"physical-transfer-v1","tick_unit":"simulation_tick","stops":["a","hub","end"],"vehicles":[{"id":"v1","capacity":1},{"id":"v2","capacity":1}],"services":[{"id":"first","vehicle":"v1","from":"a","to":"hub","period":10,"offset":0,"duration":2,"enabled":true},{"id":"second","vehicle":"v2","from":"hub","to":"end","period":10,"offset":2,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"transfer") and transit.request_journey("rider","a","end"),"configure journey")
	for i in range(30):
		await physics_frame
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor(),"initial platform contact")
	check(transit.begin_tick() and transit.open_boarding(),"first boarding")
	var board: Dictionary = transit.pending_request("rider")
	check(board.get("type") == "boarding_requested" and transit.acknowledge_boarding("rider","v1",board.details.token,board.id),"board first")
	check(transit.finish_tick(),"depart first")
	for i in range(120):
		await physics_frame
		first.position.x += 0.02
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor() and absf(body.position.x-first.position.x) < 0.5,"ride first platform")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"first arrival")
	var alight: Dictionary = transit.pending_request("rider")
	check(alight.get("type") == "alighting_requested","request transfer exit")
	for i in range(75):
		await physics_frame
		body.velocity.x = 2.0
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	body.velocity.x = 0
	check(body.is_on_floor() and body.position.x > 4.3 and body.position.x < 5.8,"reach shared station")
	check(transit.acknowledge_alighting("rider","v1",alight.details.token,alight.id),"confirm first exit")
	check(transit.open_boarding(),"second boarding")
	board = transit.pending_request("rider")
	check(board.get("type") == "boarding_requested" and board.details.vehicle == "v2","second request")
	for i in range(78):
		await physics_frame
		body.velocity.x = 2.0
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	body.velocity.x = 0
	check(body.is_on_floor() and absf(body.position.x-second.position.x) < 0.5,"reach second platform")
	check(transit.acknowledge_boarding("rider","v2",board.details.token,board.id) and transit.finish_tick(),"depart second")
	for i in range(120):
		await physics_frame
		second.position.x += 0.02
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor() and absf(body.position.x-second.position.x) < 0.5,"ride second platform")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"second arrival")
	alight = transit.pending_request("rider")
	for i in range(90):
		await physics_frame
		body.velocity.x = 2.0
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor() and body.position.x > 11.5,"reach end station")
	check(transit.acknowledge_alighting("rider","v2",alight.details.token,alight.id),"confirm final exit")
	check(transit.journey("rider").state == "completed","transfer completed")
	print("Two-platform collision transfer: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; one passenger)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
