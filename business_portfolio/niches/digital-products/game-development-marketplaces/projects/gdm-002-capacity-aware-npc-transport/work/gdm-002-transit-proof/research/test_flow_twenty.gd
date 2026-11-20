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
		var start_us := Time.get_ticks_usec()
		var ticks := 0
		for t in range(100):
			# Arriving riders must physically reach the stop before the model releases them.
			for id in state_for(model, mode):
				var p: Dictionary = state_for(model, mode)[id]
				if p.state == "onboard":
					var destination := Vector3(6,0,0) if p.leg == "A" else Vector3(12,0,0)
					check(bodies[id].global_position.distance_to(destination) < 0.35, "body reached stop before model arrival " + id + " " + mode)
			check(model.begin_tick(), "begin tick " + mode)
			for vehicle in ["A", "B"]:
				var waiting: Array = model.ledgers[vehicle].reserved.duplicate() if mode == "ledger" else model.claims[vehicle].duplicate()
				for id in waiting:
					check(model.acknowledge_board(vehicle, id, state_for(model, mode)[id].token), "boarding " + id + " " + mode)
					agents[id].set_goal_pathnode(nodes[1] if vehicle == "A" else nodes[2])
					moving[id] = true
			check(model.finish_tick(), "finish tick " + mode)
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
					bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(100.0, distance * 60.0)
					bodies[id].move_and_slide()
			ticks += 1
			var completed := 0
			for p in state_for(model, mode).values():
				if p.state == "completed":
					completed += 1
			if completed == 20:
				break
		var final_count := 0
		for p in state_for(model, mode).values():
			if p.state == "completed":
				final_count += 1
		check(final_count == 20, "20 completed " + mode)
		check(model.trace.size() == 80, "80 events " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "identical 20-agent trace")
		print(mode, " 20-agent FlowAI: ", ticks, " ticks, ", model.trace.size(), " events, ", (Time.get_ticks_usec()-start_us)/1000000.0, " seconds elapsed")
		for body in bodies.values():
			body.queue_free()
		await process_frame
	world.queue_free()
	await process_frame
	print("20-agent FlowAI comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
