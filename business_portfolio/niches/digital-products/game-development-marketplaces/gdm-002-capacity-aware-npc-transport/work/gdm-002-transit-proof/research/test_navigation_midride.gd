extends SceneTree
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
var links_seen := 0
var model
var mode := ""
func person(id: String) -> Dictionary:
	return model.passengers[id] if mode == "ledger" else model.people[id]
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func on_link(_details: Dictionary) -> void:
	var vehicle := "A" if links_seen == 0 else "B"
	links_seen += 1
	check(model.begin_tick(), "open boarding for " + mode)
	check(model.acknowledge_board(vehicle, "npc00", person("npc00").token), "board using navigation callback for " + mode)
	check(model.finish_tick(), "depart " + mode)
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
	for i in range(60):
		await physics_frame
	var first_trace: Array = []
	for which in ["ledger", "diy"]:
		mode = which
		links_seen = 0
		model = Candidate.new(1) if mode == "ledger" else DIY.new(1)
		var body := CharacterBody3D.new()
		world.add_child(body)
		var agent := NavigationAgent3D.new()
		body.add_child(agent)
		agent.set_navigation_map(map)
		agent.path_desired_distance = 0.15
		agent.target_desired_distance = 0.2
		agent.link_reached.connect(on_link)
		agent.target_position = Vector3(12, 0, 0)
		var frames := 0
		var rescuing := false
		var rescued := false
		while frames < 1500:
			await physics_frame
			if not rescuing and links_seen == 1 and body.global_position.x >= 2.0:
				check(model.disrupt_final_leg(), "disruption while in transit " + mode)
				check(person("npc00").state == "stranded", "seat held during recovery " + mode)
				rescuing = true
			if rescuing:
				if body.global_position.x <= 0.2:
					check(model.acknowledge_rescue("npc00", person("npc00").token), "safe-point callback " + mode)
					rescued = true
					break
				body.velocity = Vector3.LEFT * 4.0
			else:
				var next := agent.get_next_path_position()
				if agent.is_navigation_finished():
					break
				body.velocity = body.global_position.direction_to(next) * 4.0
			body.move_and_slide()
			frames += 1
		check(rescued and body.global_position.x <= 0.2, "body reached designated safe point " + mode)
		check(links_seen == 1, "only first link entered " + mode)
		check(person("npc00").state == "failed", "failed with explicit recovery " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "same real-controller event trace")
		print(mode, " controller: ", frames, " frames; ", links_seen, " link callbacks; ", model.trace.size(), " events")
		body.queue_free()
		await process_frame
	print("Navigation mid-ride recovery comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	for rid in rids:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
