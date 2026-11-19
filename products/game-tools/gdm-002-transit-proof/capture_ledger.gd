extends SceneTree
func _initialize() -> void:
	call_deferred("capture")
func capture() -> void:
	var scene = load("res://ledger_view.tscn").instantiate()
	root.add_child(scene)
	await create_timer(4.0).timeout
	await process_frame
	var img = root.get_texture().get_image()
	var err = img.save_png("user://ledger-view.png")
	print("Ledger capture result: ", err, " size: ", img.get_size())
	quit(0 if err == OK else 1)
