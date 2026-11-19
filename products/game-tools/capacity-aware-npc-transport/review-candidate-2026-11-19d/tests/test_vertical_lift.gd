extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var station := StaticBody3D.new()
	var station_shape := CollisionShape3D.new()
	var station_box := BoxShape3D.new()
	station_box.size = Vector3(4,0.4,3)
	station_shape.shape = station_box
	station.add_child(station_shape)
	station.position = Vector3(3.4,3,0)
	world.add_child(station)
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var cfg := {"revision":"collision-v1","tick_unit":"simulation_tick","stops":["origin","end"],"vehicles":[{"id":"lift","capacity":1}],"services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"collision"),"configure coordinator")
	check(transit.request_journey("rider","origin","end"),"request")
	var platform := AnimatableBody3D.new()
	var platform_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(3,0.4,3)
	platform_shape.shape = box
	platform.add_child(platform_shape)
	world.add_child(platform)
	var body := CharacterBody3D.new()
	var body_shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	body_shape.shape = capsule
	body.add_child(body_shape)
	body.position = Vector3(0,0.75,0)
	world.add_child(body)
	for i in range(30):
		await physics_frame
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor(),"passenger rests on platform")
	check(transit.begin_tick() and transit.open_boarding(),"open boarding")
	var board: Dictionary = {}
	for event in events:
		if event.type == "boarding_requested": board = event
	check(not board.is_empty(),"boarding requested")
	if not board.is_empty():
		check(transit.acknowledge_boarding("rider","lift",board.details.token,board.id),"acknowledge boarding after physical contact")
	check(transit.finish_tick(),"depart")
	for i in range(120):
		await physics_frame
		platform.position.y += 0.025
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor(),"passenger remains on platform")
	check(absf(body.position.y - platform.position.y - 0.7) < 0.2,"passenger follows translating platform")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"advance travel tick")
	check(transit.begin_tick(),"begin arrival")
	var alight: Dictionary = {}
	for event in events:
		if event.type == "alighting_requested": alight = event
	check(not alight.is_empty(),"alighting requested")
	for i in range(90):
		await physics_frame
		body.velocity.x = 2.0
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.position.x > 2.0 and body.position.y > 3.5 and body.is_on_floor(),"passenger reached destination station")
	if not alight.is_empty():
		check(transit.acknowledge_alighting("rider","lift",alight.details.token,alight.id),"acknowledge physical alighting")
	check(transit.journey("rider").state == "completed","journey completed")
	print("Vertical lift: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; platform x=",platform.position.x,", body x=",body.position.x,")")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
