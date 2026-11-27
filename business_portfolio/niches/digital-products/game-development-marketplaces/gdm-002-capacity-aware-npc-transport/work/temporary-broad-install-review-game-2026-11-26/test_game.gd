extends SceneTree
var game
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	game = load("res://game.tscn").instantiate()
	root.add_child(game)
	for i in range(1500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok = game.stage == "completed" and game.error.is_empty() and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game integration: ", "PASS" if ok else "FAIL", " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
