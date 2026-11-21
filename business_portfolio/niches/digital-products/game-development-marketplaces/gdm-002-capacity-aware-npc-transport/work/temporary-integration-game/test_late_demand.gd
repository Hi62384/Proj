extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.defer_second = true
	root.add_child(game)
	for i in range(500):
		await physics_frame
		if game.stage in ["sailing_first", "failed"]: break
	var first_onboard: bool = game.stage == "sailing_first" and game.transit.journey("first").state == "onboard"
	var accepted: bool = game.transit.request_journey("second", "dock", "station")
	var queued: bool = accepted and game.transit.journey("second").state == "queued"
	var early := false
	for i in range(2500):
		await physics_frame
		if game.stage in ["sailing_first", "alighting_first", "returning"] and game.transit.journey("second").state != "queued": early = true
		if game.stage in ["completed", "failed"]: break
	var ok: bool = first_onboard and accepted and queued and not early and game.stage == "completed" and game.departures == 2 and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game late-demand dispatch: ", "PASS" if ok else "FAIL", " accepted=", accepted, " queued=", queued, " early=", early, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
