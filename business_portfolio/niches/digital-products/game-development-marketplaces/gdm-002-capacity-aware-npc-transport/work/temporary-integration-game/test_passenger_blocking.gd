extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://multi_game.gd").new()
	game.block_boarding = true
	root.add_child(game)
	for i in range(200):
		await physics_frame
		if game.stage == "boarding_first" or game.stage == "failed": break
	var collided := false
	for i in range(90):
		await physics_frame
		if game.passengers.first.get_slide_collision_count() > 0:
			for j in range(game.passengers.first.get_slide_collision_count()):
				if game.passengers.first.get_slide_collision(j).get_collider() == game.passengers.second: collided = true
	var blocked: bool = game.stage == "boarding_first" and game.transit.journey("first").state == "boarding" and game.departures == 0 and game.passengers.first.position.x < -1.6
	var ledger: Dictionary = game.transit.inspect_vehicle("ferry").ledger
	var held: bool = ledger.claims.size() == 1 and ledger.aboard.is_empty() and game.transit.journey("second").state == "queued"
	game.passengers.second.position.z = game.lane("second")
	for i in range(2500):
		await physics_frame
		if game.stage in ["completed", "failed"]: break
	var ok: bool = collided and blocked and held and game.stage == "completed" and game.departures == 2 and game.transit.inspect_vehicle("ferry").ledger.aboard.is_empty()
	print("Temporary game passenger blocking: ", "PASS" if ok else "FAIL", " collision=", collided, " blocked=", blocked, " held=", held, " stage=", game.stage, " error=", game.error)
	game.queue_free()
	await process_frame
	quit(0 if ok else 1)
