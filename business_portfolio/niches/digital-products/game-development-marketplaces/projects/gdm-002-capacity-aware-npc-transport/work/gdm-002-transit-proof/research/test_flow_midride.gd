extends SceneTree
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func person(model, mode: String) -> Dictionary:
	return model.passengers.npc00 if mode == "ledger" else model.people.npc00
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var controller := FlowAIController.new()
	controller.show_pathnode_lines = false
	root.add_child(controller)
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
		var model = Candidate.new(1) if mode == "ledger" else DIY.new(1)
		var body := CharacterBody3D.new()
		var agent := FlowAIAgent3D.new()
		agent.path_desired_distance = 0.15
		body.add_child(agent)
		root.add_child(body)
		agent.set_goal_pathnode(nodes[2])
		var leg := 0
		var frames := 0
		var rescuing := false
		var rescued := false
		while frames < 1500:
			await physics_frame
			if leg == 0 and body.global_position.x >= 0.2:
				check(model.begin_tick(), "first departure window " + mode)
				check(model.acknowledge_board("A", "npc00", person(model, mode).token), "first boarding " + mode)
				check(model.finish_tick(), "first departure " + mode)
				leg = 1
			if leg == 1 and not rescuing and body.global_position.x >= 2.0:
				check(model.disrupt_final_leg(), "disruption during transit " + mode)
				check(person(model, mode).state == "stranded", "seat held " + mode)
				rescuing = true
			if rescuing:
				if body.global_position.x <= 0.2:
					check(model.acknowledge_rescue("npc00", person(model, mode).token), "safe point callback " + mode)
					rescued = true
					break
				body.velocity = Vector3.LEFT * 4.0
			else:
				if agent.is_path_complete():
					break
				body.velocity = body.global_position.direction_to(agent.get_next_pathnode_position()) * 4.0
			body.move_and_slide()
			frames += 1
		check(rescued and body.global_position.x <= 0.2, "safe point reached " + mode)
		check(person(model, mode).state == "failed", "failed after recovery " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "same FlowAI event trace")
		print(mode, " FlowAI controller: ", frames, " frames; ", model.trace.size(), " events")
		body.queue_free()
		await process_frame
	print("FlowAI mid-ride recovery comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	controller.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
