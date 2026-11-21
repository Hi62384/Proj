extends SceneTree
const Original = preload("res://scheduled_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func initial_state() -> Dictionary:
	var queue: Array = []
	for i in range(20):
		queue.append("npc%02d" % i)
	return {"tick": 0, "queues": {"A": queue, "B": []}, "aboard": {"A": [], "B": []}, "completed": [], "trace": []}
func step(s: Dictionary) -> void:
	var t: int = s.tick
	# This intentionally independent minimal FIFO baseline models only the fixed trace.
	for v in ["A", "B"]:
		var period := 4 if v == "A" else 5
		var offset := 0 if v == "A" else 2
		if t % period == (offset + 1) % period:
			for id in s.aboard[v]:
				s.trace.append([t, "arrive", v, id])
				if v == "A":
					s.queues.B.append(id)
				else:
					s.completed.append(id)
			s.aboard[v].clear()
	for v in ["A", "B"]:
		var period := 4 if v == "A" else 5
		var offset := 0 if v == "A" else 2
		var capacity := 3 if v == "A" else 2
		if t % period == offset:
			while not s.queues[v].is_empty() and s.aboard[v].size() < capacity:
				var id = s.queues[v].pop_front()
				s.aboard[v].append(id)
				s.trace.append([t, "board", v, id])
	s.tick += 1
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
			node.p_data.p_links = ["p%d" % (i + 1)]
		node.p_flow_controller = controller
		area.add_child(node)
		node.position = Vector3(i * 6, 0, 0)
		nodes.append(node)
	var graph := controller._runtime_create_astar()
	var path = graph.get_point_path(nodes[0].get_instance_id(), nodes[2].get_instance_id())
	check(path.size() == 3 and path[2] == Vector3(12, 0, 0), "FlowAI path reaches third stop")
	var baseline = initial_state()
	for i in range(3):
		step(baseline)
	var saved = baseline.duplicate(true)
	var file = FileAccess.open("user://native-baseline.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://native-baseline.dat", FileAccess.READ)
	var restored: Dictionary = file.get_var()
	file.close()
	for i in range(100):
		step(baseline)
		step(restored)
	var original = Original.new()
	for i in range(103):
		original.step()
	check(baseline.trace == original.journal, "same 80-event trace")
	check(restored == baseline, "mid-ride disk restore continuation")
	check(baseline.completed.size() == 20, "twenty completed")
	controller.queue_free()
	await process_frame
	print("FlowAI FIFO baseline: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", baseline.trace.size(), " events)")
	quit(0 if failures == 0 else 1)
