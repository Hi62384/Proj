extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	root.size = Vector2i(1152, 648)
	var game = load("res://game.tscn").instantiate()
	root.add_child(game)
	for i in range(500):
		await physics_frame
		if game.stage == "sailing" or game.stage == "failed": break
	await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	var ok = game.stage == "sailing" and not picture.is_empty() and picture.save_png("user://temporary-game-sailing.png") == OK
	print("Temporary game rendered capture: ", "PASS" if ok else "FAIL", " stage=", game.stage)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
