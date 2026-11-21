extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	root.add_child(game)
	for i in range(500):
		await physics_frame
		if game.stage in ["sailing_first", "failed"]: break
	var queued: bool = game.stage == "sailing_first" and game.transit.journey("second").state == "queued"
	var cancelled: bool = game.transit.cancel_journey("second") and game.transit.journey("second").state == "cancelled"
	var absent: bool = not game.transit.inspect_vehicle("ferry").ledger.waiting.has("second")
	var requeued: bool = game.transit.request_journey("second", "dock", "station") and game.transit.journey("second").state == "queued"
	for i in range(2500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok: bool = queued and cancelled and absent and requeued and game.stage == "completed" and game.departures == 2 and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game dispatch requeue: ", "PASS" if ok else "FAIL", " queued=", queued, " cancelled=", cancelled, " requeued=", requeued, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
