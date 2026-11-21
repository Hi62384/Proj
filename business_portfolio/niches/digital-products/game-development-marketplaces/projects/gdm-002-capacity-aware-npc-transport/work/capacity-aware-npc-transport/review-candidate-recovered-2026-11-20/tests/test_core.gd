extends SceneTree
const Graph = preload("res://addons/transit_coordinator/core/transit_graph.gd")
const Ledger = preload("res://addons/transit_coordinator/core/seat_ledger.gd")
var failures := 0
func check(condition: bool, label: String) -> void:
	if not condition:
		failures += 1
		printerr("FAIL: ", label)
func example() -> Dictionary:
	return {"revision":"demo-v1", "tick_unit":"simulation_tick", "stops":["origin", "hub", "end"],
		"vehicles":[{"id":"lift", "capacity":2}, {"id":"boat", "capacity":2}, {"id":"direct", "capacity":1}],
		"services":[
			{"id":"a", "vehicle":"lift", "from":"origin", "to":"hub", "period":4, "offset":0, "duration":2, "enabled":true},
			{"id":"b", "vehicle":"boat", "from":"hub", "to":"end", "period":5, "offset":3, "duration":2, "enabled":true},
			{"id":"c", "vehicle":"direct", "from":"origin", "to":"end", "period":10, "offset":0, "duration":9, "enabled":true}]}
func brute_overlap(a: Dictionary, b: Dictionary) -> bool:
	# The small periods tested below repeat within this window.
	for x in range(a.offset, 300, a.period):
		for y in range(b.offset, 300, b.period):
			if x < y + b.duration and y < x + a.duration:
				return true
	return false
func _initialize() -> void:
	var cfg := example()
	var created = Graph.create(cfg)
	check(created.ok, "valid graph")
	if not created.ok:
		quit(1)
		return
	var graph = created.graph
	var route = graph.plan("origin", "end", 0)
	check(route.ok and route.arrival == 5 and route.legs.size() == 2, "earliest connection")
	cfg.services[1].enabled = false
	check(graph.plan("origin", "end", 0).arrival == 5, "input copy isolates graph")
	var changed = graph.export_config()
	changed.services[1].enabled = false
	var altered = Graph.create(changed).graph
	check(altered.plan("origin", "end", 0).arrival == 9, "disabled connection uses direct route")
	changed.services[2].enabled = false
	check(Graph.create(changed).graph.plan("origin", "end", 0).error == "no_route", "no route explicit")
	check(graph.plan("origin", "origin", 2).arrival == 2, "same stop")
	var bad := example()
	bad.services.append(bad.services[0].duplicate(true))
	check(Graph.validate(bad) == "duplicate_service", "duplicate service rejected")
	bad = example()
	bad.services[0].duration = 0
	check(Graph.validate(bad) == "invalid_schedule", "zero duration rejected")
	bad = example()
	bad.services[0].vehicle = "missing"
	check(Graph.validate(bad) == "unknown_vehicle", "unknown vehicle rejected")
	bad = example()
	bad.services[2].vehicle = "lift"
	check(Graph.validate(bad) == "vehicle_schedule_overlap", "vehicle conflicts rejected")
	var rng := RandomNumberGenerator.new()
	rng.seed = 1771
	for i in range(1000):
		var p := rng.randi_range(1, 8)
		var q := rng.randi_range(1, 8)
		var a = {"period":p, "offset":rng.randi_range(0,p-1), "duration":rng.randi_range(1,p)}
		var b = {"period":q, "offset":rng.randi_range(0,q-1), "duration":rng.randi_range(1,q)}
		check(Graph._services_overlap(a,b) == brute_overlap(a,b), "periodic overlap fixture %d" % i)
	var ledger = Ledger.create(1)
	check(ledger.request("first") and ledger.request("second"), "requests accepted")
	var first: Dictionary = ledger.allocate()[0]
	check(first.agent == "first", "FIFO seat")
	check(ledger.cancel("first") and not ledger.board("first",first.token), "cancel rejects stale board")
	var second: Dictionary = ledger.allocate()[0]
	check(second.agent == "second" and ledger.board("second",second.token) and not ledger.board("second",second.token), "one boarding")
	var saved = ledger.snapshot()
	var restored = Ledger.restore(saved)
	check(restored != null and restored.snapshot() == saved, "ledger snapshot round trip")
	check(restored.release("second",second.token) and not restored.release("second",second.token), "release exactly once")
	check(restored.request("first"), "agent may requeue")
	var renewed: Dictionary = restored.allocate()[0]
	check(renewed.token > second.token and not restored.board("first",first.token), "old token stays invalid")
	var corrupt = saved.duplicate(true)
	corrupt.claims.append({"agent":"other", "token":second.token})
	check(Ledger.restore(corrupt) == null, "overcapacity rejected")
	corrupt = saved.duplicate(true)
	corrupt.waiting.append("second")
	check(Ledger.restore(corrupt) == null, "duplicate ownership rejected")
	print("Transit core contracts: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 1000 schedule cases)")
	quit(0 if failures == 0 else 1)
