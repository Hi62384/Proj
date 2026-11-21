extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Character = preload("res://passenger_controller.gd")
var failures := 0
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
	var mesh := MeshInstance3D.new()
	var box_mesh := BoxMesh.new()
	box_mesh.size = size
	mesh.mesh = box_mesh
	var material := StandardMaterial3D.new()
	material.albedo_color = Color.CORNFLOWER_BLUE if moving else Color.SLATE_GRAY
	mesh.material_override = material
	node.add_child(mesh)
	node.position = position
	return node
func wait_state(transit, state: String, frames: int) -> bool:
	for i in range(frames):
		await physics_frame
		if transit.journey("rider").get("state") == state:
			return true
	return false
func capture(label: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	check(img != null and not img.is_empty() and img.save_png("user://" + label + ".png") == OK,"render " + label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.size = Vector2i(1152,648)
	root.add_child(world)
	var camera := Camera3D.new()
	world.add_child(camera)
	camera.position = Vector3(5,10,18)
	camera.fov = 36
	camera.look_at(Vector3(5,0,0))
	camera.current = true
	var light := DirectionalLight3D.new()
	world.add_child(light)
	light.rotation_degrees = Vector3(-60,-30,0)
	var first = surface(Vector3(3,0.4,3),Vector3.ZERO,true)
	var second = surface(Vector3(3,0.4,3),Vector3(7.5,0,0),true)
	world.add_child(first)
	world.add_child(second)
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(-2.5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(5,0,0),false))
	world.add_child(surface(Vector3(2.2,0.4,3),Vector3(12.5,0,0),false))
	var body = Character.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	shape.shape = capsule
	body.add_child(shape)
	var passenger_mesh := MeshInstance3D.new()
	var capsule_mesh := CapsuleMesh.new()
	capsule_mesh.radius = 0.25
	capsule_mesh.height = 1.0
	passenger_mesh.mesh = capsule_mesh
	var passenger_material := StandardMaterial3D.new()
	passenger_material.albedo_color = Color.GOLD
	passenger_mesh.material_override = passenger_material
	body.add_child(passenger_mesh)
	body.position = Vector3(-2.5,0.75,0)
	world.add_child(body)
	var transit = Transit.new()
	var bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"owned-controller-v1","tick_unit":"simulation_tick","stops":["a","hub","end"],"vehicles":[{"id":"v1","capacity":1},{"id":"v2","capacity":1}],"services":[{"id":"first","vehicle":"v1","from":"a","to":"hub","period":10,"offset":0,"duration":2,"enabled":true},{"id":"second","vehicle":"v2","from":"hub","to":"end","period":10,"offset":2,"duration":2,"enabled":true}]}
	check(transit.configure(cfg,"owned") and bridge.configure(transit),"configure")
	bridge.movement_requested.connect(func(e):
		var x := 0.0
		if e.type == "boarding_requested":
			x = 0.0 if e.details.vehicle == "v1" else 7.5
		else:
			x = 5.0 if e.details.stop == "hub" else 12.5
		requests[e.id] = e
		targets[e.id] = x
		body.start_motion(Vector3(x,0.7,0),e.id)
	)
	bridge.request_withdrawn.connect(func(_agent,id,_reason): body.stop_motion(id))
	body.motion_finished.connect(func(id):
		var expected: float = targets[id]
		check(bridge.complete_movement(requests[id],func(_event): return body.is_on_floor() and absf(body.position.x-expected) < 0.25),"verified completion " + id)
	)
	check(transit.request_journey("rider","a","end"),"request")
	for i in range(30): await physics_frame
	check(transit.begin_tick() and transit.open_boarding(),"first window")
	check(await wait_state(transit,"boarding_confirmed",180),"game controller boards first")
	await capture("boarding")
	check(transit.finish_tick(),"depart first")
	for i in range(120):
		await physics_frame
		first.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x-first.position.x)<0.5,"physical first ride")
	await capture("first_ride")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"first arrival")
	check(await wait_state(transit,"queued",180),"game controller exits first")
	check(transit.open_boarding(),"second window")
	check(await wait_state(transit,"boarding_confirmed",180),"game controller boards second")
	check(transit.finish_tick(),"depart second")
	for i in range(120):
		await physics_frame
		second.position.x += 0.02
	check(body.is_on_floor() and absf(body.position.x-second.position.x)<0.5,"physical second ride")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick() and transit.begin_tick(),"second arrival")
	check(await wait_state(transit,"completed",180),"game controller exits second")
	await capture("completed")
	print("Independent temporary game visual transfer: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; one passenger)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
