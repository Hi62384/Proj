extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://game.tscn").instantiate()
	game.scenario = "disruption"
	root.add_child(game)
	var saw_recovery := false
	var retained := false
	var rejected := false
	for i in range(1500):
		await physics_frame
		if game.stage == "recovering" and not saw_recovery:
			saw_recovery = true
			var pending: Dictionary = game.transit.pending_request("visitor")
			retained = pending.get("type") == "recovery_requested" and game.transit.inspect_vehicle("ferry").ledger.aboard.size() == 1
			rejected = not game.bridge.complete_movement(pending, func(_event): return false, "station") and game.transit.inspect_vehicle("ferry").ledger.aboard.size() == 1
		if game.stage in ["completed", "failed"]: break
	var ok = saw_recovery and retained and rejected and game.stage == "completed" and game.error.is_empty() and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game disruption: ", "PASS" if ok else "FAIL", " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
