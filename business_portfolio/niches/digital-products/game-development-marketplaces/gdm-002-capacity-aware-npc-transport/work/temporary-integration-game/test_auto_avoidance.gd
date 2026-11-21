extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.block_boarding = true
	game.auto_yield = true
	root.add_child(game)
	var held_before_yield := false
	var detected := false
	for i in range(2500):
		await physics_frame
		if game.passengers.second.yield_count > 0:
			detected = true
			if game.transit.journey("first").state == "boarding" and game.departures == 0:
				held_before_yield = true
		if game.stage in ["completed", "failed"]: break
	var ok: bool = detected and held_before_yield and game.stage == "completed" and game.departures == 2 and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game cooperative avoidance: ", "PASS" if ok else "FAIL", " yield=", detected, " held=", held_before_yield, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
