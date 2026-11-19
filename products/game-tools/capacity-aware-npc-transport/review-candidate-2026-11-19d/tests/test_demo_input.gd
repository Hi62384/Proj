extends SceneTree
const Demo = preload("res://demo/transit_demo.gd")
var failures := 0

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)

func find_button(node: Node, title: String) -> Button:
	if node is Button and node.text == title:
		return node
	for child in node.get_children():
		var found := find_button(child, title)
		if found != null: return found
	return null

func click(button: Button) -> void:
	var at := button.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = at
	motion.global_position = at
	root.push_input(motion, true)
	var down := InputEventMouseButton.new()
	down.button_index = MOUSE_BUTTON_LEFT
	down.position = at
	down.global_position = at
	down.pressed = true
	root.push_input(down, true)
	await process_frame
	var up := InputEventMouseButton.new()
	up.button_index = MOUSE_BUTTON_LEFT
	up.position = at
	up.global_position = at
	up.pressed = false
	root.push_input(up, true)
	await process_frame

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.size = Vector2i(1152, 648)
	var demo = Demo.new()
	root.add_child(demo)
	demo.automatic = false
	for i in range(4): await process_frame
	var pause := find_button(demo, "Pause / resume")
	var disable := find_button(demo, "Disable B-fast")
	var enable := find_button(demo, "Enable B-fast")
	var save := find_button(demo, "Save")
	var load := find_button(demo, "Load")
	check(pause != null and disable != null and enable != null and save != null and load != null, "all controls exist")
	if pause == null or disable == null or enable == null or save == null or load == null:
		quit(1)
		return
	check(pause.get_global_rect().size.x > 0 and pause.get_global_rect().size.y > 0, "pause has hit area")
	await click(pause)
	check(demo.paused and demo.message.text == "Paused.", "mouse pause")
	check(pause.has_focus(), "mouse focus")
	var accept_down := InputEventAction.new()
	accept_down.action = "ui_accept"
	accept_down.pressed = true
	root.push_input(accept_down, true)
	await process_frame
	var accept_up := InputEventAction.new()
	accept_up.action = "ui_accept"
	accept_up.pressed = false
	root.push_input(accept_up, true)
	await process_frame
	check(not demo.paused and demo.message.text == "Running.", "focused keyboard resume")
	await click(disable)
	check(demo.message.text == "Disable is available between ticks.", "unavailable service control explains timing")
	# Availability changes are intentionally limited to the ready phase.
	demo.advance(demo.ARRIVAL_WINDOW)
	demo.advance(demo.BOARD_WINDOW)
	check(demo.phase == "travel", "reach service-control window")
	await click(disable)
	check(demo.message.text.begins_with("B-fast disabled"), "mouse disable service")
	await click(enable)
	check(demo.message.text == "B-fast enabled.", "mouse enable service")
	await click(save)
	check(demo.message.text == "Saved locally.", "mouse save")
	await click(pause)
	check(demo.paused, "change after save")
	await click(load)
	check(demo.message.text == "Loaded local save." and not demo.paused, "mouse load restores state")
	print("Demo viewport mouse and keyboard input: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	demo.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
