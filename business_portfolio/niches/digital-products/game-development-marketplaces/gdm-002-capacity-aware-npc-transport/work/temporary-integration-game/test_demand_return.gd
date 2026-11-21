extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.defer_second = true
	game.demand_dispatch = true
	root.add_child(game)
	for i in range(1500):
		await physics_frame
		if game.stage in ["waiting_demand", "failed"]: break
	var waiting: bool = game.stage == "waiting_demand" and game.departures == 1
	var parked_x: float = game.platform.position.x
	for i in range(90): await physics_frame
	var remained: bool = game.stage == "waiting_demand" and is_equal_approx(game.platform.position.x, parked_x)
	var accepted: bool = game.transit.request_journey("second", "dock", "station")
	var returned := false
	var premature := false
	for i in range(2500):
		await physics_frame
		if game.stage == "returning":
			returned = true
			if game.transit.journey("second").state != "queued": premature = true
		if game.stage in ["completed", "failed"]: break
	var ok: bool = waiting and remained and accepted and returned and not premature and game.stage == "completed" and game.departures == 2 and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game demand-triggered return: ", "PASS" if ok else "FAIL", " parked=", remained, " accepted=", accepted, " returned=", returned, " early=", premature, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
