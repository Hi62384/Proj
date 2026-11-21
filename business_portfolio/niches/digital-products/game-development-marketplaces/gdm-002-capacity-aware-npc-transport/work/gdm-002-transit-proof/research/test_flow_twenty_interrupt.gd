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
		var model = Candidate.new() if mode == "ledger" else DIY.new()
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
		check(model.begin_tick(), "first departure " + mode)
		var selected: Array = model.ledgers.A.reserved.duplicate() if mode == "ledger" else model.claims.A.duplicate()
		check(selected.size() == 3, "three seats claimed " + mode)
		for id in selected:
			check(model.acknowledge_board("A", id, state_for(model, mode)[id].token), "boarding " + mode)
			agents[id].set_goal_pathnode(nodes[1])
			moving[id] = true
		check(model.finish_tick(), "depart " + mode)
		# Advance until all selected riders have moved away from the origin.
		for frame in range(15):
			await physics_frame
			for id in selected:
				var target: Vector3 = agents[id].get_next_pathnode_position()
				var distance: float = bodies[id].global_position.distance_to(target)
				bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(100.0, distance * 60.0)
				bodies[id].move_and_slide()
			var all_moved := true
			for id in selected:
				if bodies[id].global_position.x <= 0.2:
					all_moved = false
			if all_moved:
				break
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
	world.queue_free()
	await process_frame
	print("20-agent FlowAI interruption comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
