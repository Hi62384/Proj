extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	for width in [1152, 800]:
		root.size = Vector2i(width, 648)
		await process_frame
		await process_frame
		var rect: Rect2 = demo.status.get_global_rect()
		check(rect.position.x >= 0 and rect.end.x <= width, "status stays within viewport width %d: %s" % [width, rect])
		check(demo.status.autowrap_mode != TextServer.AUTOWRAP_OFF, "status wraps at width %d" % width)
		if width == 800:
			check(demo.status.get_line_count() > 3, "status wraps onto additional lines at 800")
	demo.queue_free()
	await process_frame
	print("Demo layout: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
