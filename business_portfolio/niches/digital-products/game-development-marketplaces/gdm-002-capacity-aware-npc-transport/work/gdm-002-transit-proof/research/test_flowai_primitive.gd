extends SceneTree
var failures := 0
func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", message)
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
		node.position = Vector3(i * 6, 0, 0)
		nodes.append(node)
	var graph := controller._runtime_create_astar()
	var path = graph.get_point_path(nodes[0].get_instance_id(), nodes[2].get_instance_id())
	check(path.size() == 3 and path[2] == Vector3(12, 0, 0), "three-stop path")
	print("FlowAI pathnode primitive: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", path.size(), " points)")
	controller.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
