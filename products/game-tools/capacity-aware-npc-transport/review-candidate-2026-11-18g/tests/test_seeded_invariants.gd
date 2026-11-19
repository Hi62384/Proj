extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		if failures <= 20: printerr("FAIL: ",label)
func respond(core, events: Array, rng: RandomNumberGenerator) -> void:
	for event in events:
		if event.type == "boarding_requested" and rng.randi_range(0,4) != 0:
			check(core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id),"board")
		elif event.type == "alighting_requested" and rng.randi_range(0,4) != 0:
			check(core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id),"alight")
		elif event.type == "recovery_requested" and not event.details.safe_stops.is_empty():
			check(core.acknowledge_recovery(event.agent,event.details.vehicle,event.details.token,event.id,event.details.safe_stops[0]),"recover")
func inspect(core, cfg: Dictionary, sample: int, tick: int) -> void:
	var snapshot: Dictionary = core.snapshot()
	var owners := {}
	for vehicle in snapshot.ledgers:
		var ledger: Dictionary = snapshot.ledgers[vehicle]
		check(ledger.claims.size()+ledger.aboard.size() <= ledger.capacity,"capacity")
		for id in ledger.waiting:
			check(not owners.has(id),"unique waiting ownership")
			owners[id] = true
		for group in ["claims","aboard"]:
			for entry in ledger[group]:
				check(not owners.has(entry.agent),"unique seat ownership")
				owners[entry.agent] = true
	var restored = Core.restore(cfg,snapshot)
	check(restored.ok,"restore sample %d tick %d" % [sample,tick])
	if restored.ok:
		check(restored.coordinator.snapshot() == snapshot,"exact restored state")
func _initialize() -> void:
	var cfg := {"revision":"random-v1","tick_unit":"simulation_tick","stops":["a","b","c"],"vehicles":[{"id":"v1","capacity":3},{"id":"v2","capacity":2}],"services":[{"id":"s1","vehicle":"v1","from":"a","to":"b","period":4,"offset":0,"duration":2,"enabled":true},{"id":"s2","vehicle":"v2","from":"b","to":"c","period":5,"offset":3,"duration":2,"enabled":true}]}
	for sample in range(25):
		var rng := RandomNumberGenerator.new()
		rng.seed = 2000+sample
		var core = Core.create(cfg,"random%d" % sample).coordinator
		for i in range(20): check(core.request_journey("npc%d" % i,"a","c").ok,"request")
		core.drain_events()
		var enabled := true
		for tick in range(50):
			if rng.randi_range(0,9) == 0:
				enabled = not enabled
				check(core.set_service_enabled("s2",enabled),"toggle")
				respond(core,core.drain_events(),rng)
				core.drain_events()
			check(core.begin_tick(),"begin")
			respond(core,core.drain_events(),rng)
			core.drain_events()
			check(core.open_boarding(),"open")
			respond(core,core.drain_events(),rng)
			core.drain_events()
			check(core.finish_tick(),"finish")
			core.drain_events()
			inspect(core,cfg,sample,tick)
	print("Seeded disruption invariants: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; 25 x 50 ticks)")
	quit(0 if failures == 0 else 1)
