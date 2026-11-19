extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
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
	var nav_map := NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(nav_map,true)
	var nav_mesh := NavigationMesh.new()
	nav_mesh.vertices = PackedVector3Array([Vector3(-6,0,-3),Vector3(-6,0,3),Vector3(2,0,3),Vector3(2,0,-3)])
	nav_mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var region := NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(region,nav_mesh)
	NavigationServer3D.region_set_map(region,nav_map)
	var origin := StaticBody3D.new()
	var origin_shape := CollisionShape3D.new()
	var origin_box := BoxShape3D.new()
	origin_box.size = Vector3(6,0.4,3)
	origin_shape.shape = origin_box
	origin.add_child(origin_shape)
	origin.position = Vector3(-4.5,0,0)
	world.add_child(origin)
	var station := StaticBody3D.new()
	var station_shape := CollisionShape3D.new()
	var station_box := BoxShape3D.new()
	station_box.size = Vector3(4,0.4,3)
	station_shape.shape = station_box
	station.add_child(station_shape)
	station.position = Vector3(5.9,0,0)
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
	body.position = Vector3(-4,0.75,0)
	world.add_child(body)
	var navigation := NavigationAgent3D.new()
	body.add_child(navigation)
	navigation.set_navigation_map(nav_map)
	navigation.path_desired_distance = 0.8
	navigation.target_desired_distance = 0.8
	for i in range(60):
		await physics_frame
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(transit.begin_tick() and transit.open_boarding(),"open boarding")
	var board: Dictionary = {}
	for event in events:
		if event.type == "boarding_requested": board = event
	check(not board.is_empty(),"boarding requested")
	var adapter = Adapter.new()
	world.add_child(adapter)
	check(adapter.configure(transit) and adapter.register_agent("rider",body,navigation),"configure adapter")
	check(adapter.move_for_request(board,Vector3(0,0.7,0),func(candidate, _event): return candidate.is_on_floor() and absf(candidate.position.x) < 0.4),"start adapter movement")
	for i in range(60):
		await physics_frame
	check(transit.journey("rider").state == "boarding" and body.position.x < -0.4,"save while moving")
	var saved: Dictionary = transit.save_snapshot()
	check(saved.ok,"save moving request")
	adapter.cancel_movement("rider")
	adapter.queue_free()
	var restored = Transit.new()
	world.add_child(restored)
	restored.transit_event.connect(func(e): events.append(e))
	check(restored.restore_snapshot(cfg,saved.snapshot),"restore moving request")
	transit.queue_free()
	transit = restored
	var replacement = Adapter.new()
	world.add_child(replacement)
	check(replacement.configure(transit) and replacement.register_agent("rider",body,navigation),"reconnect adapter")
	var pending: Dictionary = transit.pending_request("rider")
	check(replacement.move_for_request(pending,Vector3(0,0.7,0),func(candidate, _event): return candidate.is_on_floor() and absf(candidate.position.x) < 0.4),"resume movement")
	for i in range(240):
		await physics_frame
	check(body.is_on_floor() and absf(body.position.x) < 0.4,"adapter navigation reached platform")
	check(transit.journey("rider").state == "boarding_confirmed","adapter acknowledged verified boarding")
	check(transit.finish_tick(),"depart")
	for i in range(120):
		await physics_frame
		platform.position.x += 0.02
		body.velocity.y -= 9.8/60.0
		body.move_and_slide()
	check(body.is_on_floor(),"passenger remains on platform")
	check(absf(body.position.x - platform.position.x) < 0.5,"passenger follows translating platform")
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
	check(body.position.x > 4.2 and body.is_on_floor(),"passenger reached destination station")
	if not alight.is_empty():
		check(transit.acknowledge_alighting("rider","lift",alight.details.token,alight.id),"acknowledge physical alighting")
	check(transit.journey("rider").state == "completed","journey completed")
	print("Restore moving navigation adapter: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; platform x=",platform.position.x,", body x=",body.position.x,")")
	NavigationServer3D.free_rid(region)
	NavigationServer3D.free_rid(nav_map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
