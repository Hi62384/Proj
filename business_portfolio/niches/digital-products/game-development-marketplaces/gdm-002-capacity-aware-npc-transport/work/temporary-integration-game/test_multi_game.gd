extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	root.add_child(game)
	var queued_on_first := false
	var held_during_return := false
	var early_second := false
	var exceeded := false
	for i in range(2500):
		await physics_frame
		var ledger: Dictionary = game.transit.inspect_vehicle("ferry").get("ledger", {})
		if ledger.is_empty(): continue
		if ledger.aboard.size() + ledger.claims.size() > 1: exceeded = true
		if game.stage == "sailing_first" and game.transit.journey("second").state == "queued": queued_on_first = true
		if game.stage == "returning" and game.transit.journey("second").state == "queued": held_during_return = true
		if game.stage in ["sailing_first", "alighting_first", "returning"] and game.transit.journey("second").state in ["boarding_confirmed", "onboard"]: early_second = true
		if game.stage in ["completed", "failed"]: break
	var ok: bool = game.stage == "completed" and game.error.is_empty() and game.departures == 2 and queued_on_first and held_during_return and not early_second and not exceeded and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game two-passenger contention: ", "PASS" if ok else "FAIL", " stage=", game.stage, " error=", game.error, " early=", early_second)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
