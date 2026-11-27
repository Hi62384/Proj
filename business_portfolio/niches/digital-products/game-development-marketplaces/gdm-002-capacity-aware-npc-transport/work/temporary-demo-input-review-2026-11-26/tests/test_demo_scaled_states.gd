extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func button_named(node: Node, title: String) -> Button:
	if node is Button and node.text == title:
		return node
	for child in node.get_children():
		var found := button_named(child, title)
		if found != null:
			return found
	return null
func click(button: Button) -> void:
	var position := button.get_global_rect().get_center()
	for down in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		event.position = position
		event.global_position = position
		root.push_input(event, true)
		await process_frame
func run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 480)
	root.content_scale_factor = 1.5
	root.size = Vector2i(960, 720)
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	await process_frame
	await process_frame
	check(root.size == Vector2i(960, 720) and is_equal_approx(root.content_scale_factor, 1.5),"requested scaled viewport")
	for label in [demo.status, demo.message]:
		var label_rect: Rect2 = label.get_global_rect()
		check(label_rect.position.x >= 0.0 and label_rect.position.y >= 0.0 and label_rect.end.x <= root.get_visible_rect().size.x and label_rect.end.y <= root.get_visible_rect().size.y,"label within scaled viewport")
	var details := button_named(demo, "Hide details")
	check(details != null, "details toggle exists")
	if details != null:
		await click(details)
		check(not demo.status.visible and not demo.message.visible and details.text == "Show details", "details hide")
		await click(details)
		check(demo.status.visible and demo.message.visible and details.text == "Hide details", "details restore")
	var pause := button_named(demo, "Pause / resume")
	var save := button_named(demo, "Save")
	var load_button := button_named(demo, "Load")
	check(pause != null and save != null and load_button != null, "demo controls exist")
	if pause != null and save != null and load_button != null:
		for button in [pause, save, load_button]:
			var rect: Rect2 = button.get_global_rect()
			check(rect.position.x >= 0.0 and rect.position.y >= 0.0 and rect.end.x <= root.get_visible_rect().size.x and rect.end.y <= root.get_visible_rect().size.y,"control within viewport: " + button.text)
		await click(pause)
		check(demo.paused, "mouse click pauses")
		pause.grab_focus()
		var press := InputEventAction.new()
		press.action = "ui_accept"
		press.pressed = true
		root.push_input(press, true)
		var release := InputEventAction.new()
		release.action = "ui_accept"
		release.pressed = false
		root.push_input(release, true)
		await process_frame
		check(not demo.paused, "focused keyboard action resumes")
		await click(save)
		check(demo.message.text == "Saved locally.", "mouse click saves")
		save.grab_focus()
		var next := InputEventAction.new()
		next.action = "ui_focus_next"
		next.pressed = true
		root.push_input(next, true)
		await process_frame
		check(root.gui_get_focus_owner() == load_button, "keyboard focus advances from Save to Load")
		var next_release := InputEventAction.new()
		next_release.action = "ui_focus_next"
		next_release.pressed = false
		root.push_input(next_release, true)
		var activate := InputEventAction.new()
		activate.action = "ui_accept"
		activate.pressed = true
		root.push_input(activate, true)
		var activate_release := InputEventAction.new()
		activate_release.action = "ui_accept"
		activate_release.pressed = false
		root.push_input(activate_release, true)
		await process_frame
		check(demo.message.text == "Loaded local save.", "focused keyboard action loads")
		await click(load_button)
		check(demo.message.text == "Loaded local save.", "mouse click loads")
	for i in range(140): demo.advance(0.1)
	await process_frame
	await process_frame
	for label in [demo.status, demo.message]:
		var label_rect: Rect2 = label.get_global_rect()
		check(label_rect.position.x >= 0.0 and label_rect.position.y >= 0.0 and label_rect.end.x <= root.get_visible_rect().size.x and label_rect.end.y <= root.get_visible_rect().size.y,"progressed label within scaled viewport")
	demo.disable_service()
	await process_frame
	await process_frame
	var message_rect: Rect2 = demo.message.get_global_rect()
	check(message_rect.end.y <= root.get_visible_rect().size.y,"service message within scaled viewport")
	demo.queue_free()
	await process_frame
	print("Demo scaled state changes: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
