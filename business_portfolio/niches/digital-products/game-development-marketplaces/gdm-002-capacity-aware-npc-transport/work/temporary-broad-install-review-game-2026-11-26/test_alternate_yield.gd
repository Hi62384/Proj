extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.block_boarding = true
	game.auto_yield = true
	game.wider_area = true
	root.add_child(game)
	game.surface(Vector3(2, 1.5, 0.25), Vector3(-1.4, 0.8, 0.4), false)
	var before: float = game.passengers.second.position.z
	var avoided := false
	for i in range(2500):
		await physics_frame
		if game.passengers.second.yield_count > 0 and game.passengers.second.position.z < before - 0.5: avoided = true
		if game.stage in ["completed", "failed"]: break
	var ok: bool = avoided and game.stage == "completed" and game.departures == 2
	print("Temporary game alternate-side avoidance: ", "PASS" if ok else "FAIL", " avoided=", avoided, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
