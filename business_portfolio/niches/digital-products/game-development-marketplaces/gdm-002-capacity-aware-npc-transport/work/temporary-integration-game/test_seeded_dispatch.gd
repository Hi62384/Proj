extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run_case(seed_value: int) -> void:
	var world := Node.new()
	root.add_child(world)
	var transit = Transit.new()
	var bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"seeded-game-dispatch-v1", "tick_unit":"simulation_tick", "stops":["dock", "east", "west"], "vehicles":[{"id":"e", "capacity":2}, {"id":"w", "capacity":2}], "services":[{"id":"east-service", "vehicle":"e", "from":"dock", "to":"east", "period":3, "offset":0, "duration":1, "enabled":true}, {"id":"west-service", "vehicle":"w", "from":"dock", "to":"west", "period":3, "offset":1, "duration":1, "enabled":true}]}
	check(transit.configure(cfg, "seed-" + str(seed_value)) and bridge.configure(transit), "configure")
	var destinations := {}
	var arrivals := {}
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	for i in range(12):
		var id := "p%02d" % i
		destinations[id] = "east" if rng.randi_range(0, 1) == 0 else "west"
		arrivals[id] = rng.randi_range(0, 7)
	var seen := {}
	bridge.movement_requested.connect(func(event):
		if event.type == "alighting_requested":
			check(event.details.stop == destinations[event.agent], "correct destination " + event.agent)
			seen[event.agent] = event.details.stop
		check(bridge.complete_movement(event, func(_event): return true), "simulated movement acknowledgment")
	)
	for tick in range(30):
		for id in arrivals:
			if arrivals[id] == tick: check(transit.request_journey(id, "dock", destinations[id]), "new demand " + id)
		check(transit.begin_tick() and transit.open_boarding(), "tick start")
		for vehicle in ["e", "w"]:
			var ledger: Dictionary = transit.inspect_vehicle(vehicle).ledger
			check(ledger.aboard.size() + ledger.claims.size() <= ledger.capacity, "capacity")
		check(transit.finish_tick(), "tick finish")
	for id in destinations:
		check(transit.journey(id).get("state") == "completed" and seen.get(id) == destinations[id], "completed " + id)
	for vehicle in ["e", "w"]:
		check(transit.inspect_vehicle(vehicle).ledger.aboard.is_empty(), "seat released")
	world.queue_free()
	await process_frame
func run() -> void:
	for seed_value in [41, 73, 109]: await run_case(seed_value)
	print("Temporary game seeded multi-vehicle dispatch: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; simulated movement)")
	quit(0 if failures == 0 else 1)
