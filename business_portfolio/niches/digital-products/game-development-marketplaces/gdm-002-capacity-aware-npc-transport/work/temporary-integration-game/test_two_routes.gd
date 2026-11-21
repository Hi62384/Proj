extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.two_destinations = true
	root.add_child(game)
	var destinations := {}
	game.transit.transit_event.connect(func(event):
		if event.type == "alighting_requested": destinations[event.agent] = event.details.stop
	)
	for i in range(2500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok: bool = game.stage == "completed" and game.departures == 2 and destinations.get("first") == "station" and destinations.get("second") == "south" and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game two-route dispatch: ", "PASS" if ok else "FAIL", " destinations=", destinations, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
