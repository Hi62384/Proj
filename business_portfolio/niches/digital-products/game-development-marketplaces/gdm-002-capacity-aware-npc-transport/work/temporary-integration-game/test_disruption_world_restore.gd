extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://game.tscn").instantiate()
	game.scenario = "disruption"
	root.add_child(game)
	for i in range(1500):
		await physics_frame
		if game.stage in ["recovering", "failed"]: break
	if game.stage != "recovering":
		printerr("FAIL: did not reach recovery: ", game.error)
		quit(1)
		return
	var pending_id: String = game.transit.pending_request("visitor").id
	for i in range(12): await physics_frame
	var saved: Dictionary = game.recovery_checkpoint()
	if saved.is_empty():
		printerr("FAIL: checkpoint missing")
		quit(1)
		return
	var file := FileAccess.open("user://temporary-game-recovery.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	game.queue_free()
	await process_frame
	file = FileAccess.open("user://temporary-game-recovery.dat", FileAccess.READ)
	var disk: Dictionary = file.get_var(false)
	file.close()
	game = load("res://game.tscn").instantiate()
	game.scenario = "disruption"
	game.restore_data = disk
	root.add_child(game)
	var retained: bool = game.stage == "recovering" and game.transit.pending_request("visitor").get("id") == pending_id and game.transit.inspect_vehicle("ferry").ledger.aboard.size() == 1
	for i in range(500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok: bool = retained and game.stage == "completed" and game.error.is_empty() and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game full scene recovery restore: ", "PASS" if ok else "FAIL", " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
