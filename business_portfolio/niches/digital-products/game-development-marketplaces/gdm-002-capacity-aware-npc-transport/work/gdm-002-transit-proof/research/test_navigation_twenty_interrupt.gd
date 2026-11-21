extends SceneTree
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func state_for(model, mode: String) -> Dictionary:
	return model.passengers if mode == "ledger" else model.people
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
	for mode in ["ledger", "diy"]:
		var model = Candidate.new() if mode == "ledger" else DIY.new()
		var bodies := {}
		var agents := {}
		var moving := {}
		for id in state_for(model, mode):
			var body := CharacterBody3D.new()
			var agent := NavigationAgent3D.new()
			body.add_child(agent)
			world.add_child(body)
			agent.set_navigation_map(map)
			agent.path_desired_distance = 0.15
			agent.target_desired_distance = 0.2
			bodies[id] = body
			agents[id] = agent
			moving[id] = false
		check(model.begin_tick(), "first departure " + mode)
		var selected: Array = model.ledgers.A.reserved.duplicate() if mode == "ledger" else model.claims.A.duplicate()
		check(selected.size() == 3, "three seats claimed " + mode)
		for id in selected:
			check(model.acknowledge_board("A", id, state_for(model, mode)[id].token), "boarding " + mode)
			agents[id].target_position = Vector3(6,0,0)
			moving[id] = true
		check(model.finish_tick(), "depart " + mode)
		# Advance two physics frames, placing riders between stops.
		for frame in range(2):
			await physics_frame
			for id in selected:
				var target: Vector3 = agents[id].get_next_path_position()
				var distance: float = bodies[id].global_position.distance_to(target)
				bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(100.0, distance * 60.0)
				bodies[id].move_and_slide()
		for id in selected:
			check(bodies[id].global_position.x > 0.2 and bodies[id].global_position.x < 6.0, "rider physically between stops " + mode)
		check(model.disrupt_final_leg(), "interrupt services " + mode)
		for id in selected:
			check(state_for(model, mode)[id].state == "stranded", "rider remains stranded " + mode)
		# The recovery controller moves each body to the known starting stop; this is not pathfinding.
		for frame in range(15):
			await physics_frame
			for id in selected:
				if state_for(model, mode)[id].state != "stranded":
					continue
				var position: Vector3 = bodies[id].global_position
				if position.distance_to(Vector3.ZERO) <= 0.2:
					check(model.acknowledge_rescue(id, state_for(model, mode)[id].token), "safe-point acknowledgment " + mode)
				else:
					bodies[id].velocity = position.direction_to(Vector3.ZERO) * minf(100.0, position.length() * 60.0)
					bodies[id].move_and_slide()
		for id in state_for(model, mode):
			check(state_for(model, mode)[id].state == "failed", "explicit failed outcome " + id + " " + mode)
		for v in ["A", "B"]:
			var riders: Array = model.ledgers[v].aboard if mode == "ledger" else model.riders[v]
			check(riders.is_empty(), "no remaining riders " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "identical interruption trace")
		print(mode, " 20-agent interruption: ", selected.size(), " recovered; ", model.trace.size(), " events")
		for body in bodies.values():
			body.queue_free()
		await process_frame
	for rid in rids:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	print("20-agent interruption comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
