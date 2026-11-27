extends SceneTree
func _initialize() -> void:
	call_deferred("capture")
func capture() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640,480)
	root.content_scale_factor = 1.5
	root.size = Vector2i(960,720)
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	for i in range(30): await process_frame
	for i in range(3):
		RenderingServer.force_draw(false,0.0)
		await process_frame
	var image = root.get_texture().get_image()
	if image == null or image.is_empty() or image.save_png("res://scaled-demo-review.png") != OK:
		printerr("Scaled demo capture FAIL")
		quit(1)
		return
	var bar = demo.status.get_parent().get_child(0)
	var details: Button = null
	for child in bar.get_children():
		if child is Button and child.text == "Hide details": details = child
	if details == null:
		printerr("Details toggle missing")
		quit(1)
		return
	details.pressed.emit()
	for i in range(5): await process_frame
	for i in range(3):
		RenderingServer.force_draw(false,0.0)
		await process_frame
	var compact = root.get_texture().get_image()
	if compact == null or compact.is_empty() or compact.save_png("res://scaled-demo-compact.png") != OK:
		printerr("Compact capture FAIL")
		quit(1)
		return
	print("Scaled demo capture PASS")
	quit(0)
