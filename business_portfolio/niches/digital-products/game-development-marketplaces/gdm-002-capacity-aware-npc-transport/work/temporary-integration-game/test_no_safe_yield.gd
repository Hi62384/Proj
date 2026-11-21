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
	var removable = game.surface(Vector3(2, 1.5, 0.25), Vector3(-1.4, 0.8, -1.6), false)
	for i in range(200):
		await physics_frame
		if game.stage in ["boarding_first", "failed"]: break
	for i in range(90): await physics_frame
	var safe_wait: bool = game.stage == "boarding_first" and game.passengers.second.yield_count == 0 and game.departures == 0 and game.transit.inspect_vehicle("ferry").ledger.claims.size() == 1
	removable.queue_free()
	await process_frame
	for i in range(2500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok: bool = safe_wait and game.passengers.second.yield_count > 0 and game.stage == "completed" and game.departures == 2
	print("Temporary game blocked avoidance: ", "PASS" if ok else "FAIL", " safe_wait=", safe_wait, " yield=", game.passengers.second.yield_count, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
