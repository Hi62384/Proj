extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	await process_frame
	var marker_scene = load("res://acceptance_marker.tscn").instantiate()
	root.add_child(marker_scene)
	var stop = marker_scene.get_node_or_null("TransitStop")
	var ok: bool = demo.transit != null and stop != null and stop.stop_id == "hub"
	print("Owner acceptance project startup: ", "PASS" if ok else "FAIL")
	demo.queue_free()
	marker_scene.queue_free()
	await process_frame
	quit(0 if ok else 1)
