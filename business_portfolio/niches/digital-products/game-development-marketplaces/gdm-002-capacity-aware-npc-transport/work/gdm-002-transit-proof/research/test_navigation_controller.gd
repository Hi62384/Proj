extends SceneTree
var failures := 0
var links_seen := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func on_link(_details: Dictionary) -> void:
	links_seen += 1
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-1,0,-1), Vector3(-1,0,1), Vector3(1,0,1), Vector3(1,0,-1)])
	mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var rids: Array = []
	for i in range(3):
		var region = NavigationServer3D.region_create()
		NavigationServer3D.region_set_navigation_mesh(region, mesh)
		NavigationServer3D.region_set_transform(region, Transform3D(Basis.IDENTITY, Vector3(i*6,0,0)))
		NavigationServer3D.region_set_map(region, map)
		rids.append(region)
	for i in range(2):
		var link = NavigationServer3D.link_create()
		NavigationServer3D.link_set_start_position(link, Vector3(i*6+0.8,0,0))
		NavigationServer3D.link_set_end_position(link, Vector3((i+1)*6-0.8,0,0))
		NavigationServer3D.link_set_map(link, map)
		rids.append(link)
	var body := CharacterBody3D.new()
	world.add_child(body)
	var agent := NavigationAgent3D.new()
	body.add_child(agent)
	agent.set_navigation_map(map)
	agent.path_desired_distance = 0.15
	agent.target_desired_distance = 0.2
	agent.link_reached.connect(on_link)
	for i in range(60):
		await physics_frame
	agent.target_position = Vector3(12,0,0)
	var frames := 0
	while frames < 1500:
		await physics_frame
		var next := agent.get_next_path_position()
		if agent.is_navigation_finished():
			break
		body.velocity = body.global_position.direction_to(next) * 4.0
		body.move_and_slide()
		frames += 1
	check(body.global_position.distance_to(Vector3(12,0,0)) < 0.35, "CharacterBody3D reached target using NavigationAgent3D")
	check(links_seen == 2, "both link callbacks fired")
	print("Navigation controller: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", frames, " physics frames; ", links_seen, " links)")
	for rid in rids:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
