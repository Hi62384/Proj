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
	var controller := FlowAIController.new()
	controller.show_pathnode_lines = false
	world.add_child(controller)
	var area := FlowAIAreaNode.new()
	area.a_data = FlowAIAreaData.new()
	area.a_data.a_id = 1
	area.a_flow_controller = controller
	controller.add_child(area)
	var nodes: Array = []
	for i in range(3):
		var node := FlowAIPathNode.new()
		node.p_data = FlowAIPathNodeData.new()
		node.p_data.p_id = "p%d" % i
		node.p_data.p_area_id = 1
		if i < 2:
			node.p_data.p_links = ["p%d" % (i+1)]
		node.p_flow_controller = controller
		area.add_child(node)
		node.position = Vector3(i*6,0,0)
		nodes.append(node)
	var first_trace: Array = []
	for mode in ["ledger", "diy"]:
		var model = Candidate.new(Planner) if mode == "ledger" else DIY.new(DIYPlanner)
		var bodies := {}
		var agents := {}
		var moving := {}
		for id in state_for(model, mode):
			var body := CharacterBody3D.new()
			var agent := FlowAIAgent3D.new()
			agent.path_desired_distance = 0.15
			body.add_child(agent)
			world.add_child(body)
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
					agents[id].set_goal_pathnode(nodes[1])
					moving[id] = true
				# The schedule is frozen while the external controller navigates to its safe stop.
				for f in range(30):
					await physics_frame
					for id in riders:
						var target: Vector3 = agents[id].get_next_pathnode_position()
						if not agents[id].is_path_complete():
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
					agents[id].set_goal_pathnode(nodes[1] if p.service == "a" else nodes[2])
					moving[id] = true
			for f in range(12):
				await physics_frame
				for id in moving:
					if not moving[id]:
						continue
					var target: Vector3 = agents[id].get_next_pathnode_position()
					if agents[id].is_path_complete():
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
	world.queue_free()
	await process_frame
	print("20-agent FlowAI reroute comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
