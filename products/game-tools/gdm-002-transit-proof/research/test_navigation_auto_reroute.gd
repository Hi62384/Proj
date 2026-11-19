extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func state_for(model, mode: String) -> Dictionary:
	return model.passengers
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
		var model = Candidate.new(Planner) if mode == "ledger" else DIY.new(DIYPlanner)
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
		var ticks := 0
		for t in range(150):
			if t == 4:
				var riders: Array = model.ledgers.b.aboard.duplicate() if mode == "ledger" else model.aboard.b.duplicate()
				check(riders.size() == 2, "two B riders before disruption " + mode)
				for id in riders:
					check(bodies[id].global_position.x > 6.1 and bodies[id].global_position.x < 11.9, "rider between stops " + mode)
				check(model.disrupt_service("b"), "service interruption " + mode)
				for id in riders:
					agents[id].target_position = Vector3(6,0,0)
					moving[id] = true
				# The schedule is frozen while the external controller navigates to its safe stop.
				for f in range(30):
					await physics_frame
					for id in riders:
						var target: Vector3 = agents[id].get_next_path_position()
						if not agents[id].is_navigation_finished():
							var dist: float = bodies[id].global_position.distance_to(target)
							bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(18.0, dist * 60.0)
							bodies[id].move_and_slide()
				for id in riders:
					check(bodies[id].global_position.distance_to(Vector3(6,0,0)) < 0.35, "reached safe stop " + mode)
					check(model.acknowledge_rescue(id, model.passengers[id].rescue_token, "hub"), "acknowledge recovery " + mode)
					moving[id] = false
			# Do not let the schedule process arrival before the controller reaches the stop.
			for id in model.passengers:
				var p: Dictionary = model.passengers[id]
				if p.state == "onboard" and p.due == model.tick:
					var destination := Vector3(6,0,0) if p.service == "a" else Vector3(12,0,0)
					check(bodies[id].global_position.distance_to(destination) < 0.35, "physical arrival before schedule " + id + " " + mode)
			var prior = model.passengers.duplicate(true)
			model.step()
			for id in model.passengers:
				var p: Dictionary = model.passengers[id]
				if p.state == "onboard" and (prior[id].state != "onboard" or prior[id].service != p.service):
					agents[id].target_position = Vector3(6,0,0) if p.service == "a" else Vector3(12,0,0)
					moving[id] = true
			for f in range(12):
				await physics_frame
				for id in moving:
					if not moving[id]:
						continue
					var target: Vector3 = agents[id].get_next_path_position()
					if agents[id].is_navigation_finished():
						moving[id] = false
						continue
					var distance: float = bodies[id].global_position.distance_to(target)
					bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(18.0, distance * 60.0)
					bodies[id].move_and_slide()
			ticks += 1
			var complete := 0
			for p in model.passengers.values():
				if p.state == "completed":
					complete += 1
			if complete == 20:
				break
		var total := 0
		for p in model.passengers.values():
			if p.state == "completed":
				total += 1
		check(total == 20 and model.trace.size() == 150, "all complete with disruption " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "same 20-body reroute trace")
		print(mode, " navigation reroute: ", ticks, " ticks; ", model.trace.size(), " events")
		for body in bodies.values():
			body.queue_free()
		await process_frame
	for rid in rids:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	print("20-agent navigation reroute comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
