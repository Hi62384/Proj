extends SceneTree
const Candidate = preload("res://route_planner.gd")
const DIY = preload("res://research/diy_route_baseline.gd")
const Ledger = preload("res://transit.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func exercise(planner, label: String) -> Dictionary:
	var stops = ["origin", "hub", "end"]
	var services = [
		{"id":"a", "from":"origin", "to":"hub", "period":4, "offset":0, "duration":2, "capacity":1, "enabled":true},
		{"id":"b", "from":"hub", "to":"end", "period":5, "offset":3, "duration":2, "capacity":1, "enabled":true},
		{"id":"c", "from":"hub", "to":"end", "period":7, "offset":4, "duration":3, "capacity":1, "enabled":true}
	]
	var initial = planner.plan(stops, services, "origin", "end", 0)
	check(initial.ok and initial.legs[1].service == "b" and initial.arrival == 5, "initial route " + label)
	var ledgers = {"a": Ledger.new(1), "b": Ledger.new(1), "c": Ledger.new(1)}
	check(ledgers.a.request("npc") , "first queue " + label)
	ledgers.a.allocate()
	check(ledgers.a.board("npc") and ledgers.a.disembark("npc"), "first leg " + label)
	check(ledgers.b.request("npc"), "queue connection " + label)
	ledgers.b.allocate()
	services[1].enabled = false
	check(ledgers.b.cancel("npc") and not ledgers.b.board("npc"), "released failed connection and rejected late boarding " + label)
	var replanned = planner.plan(stops, services, "hub", "end", 2)
	check(replanned.ok and replanned.legs[0].service == "c" and replanned.arrival == 7, "alternate service " + label)
	check(ledgers.c.request("npc"), "alternate queue " + label)
	ledgers.c.allocate()
	check(ledgers.c.board("npc") and ledgers.c.disembark("npc"), "alternate leg " + label)
	for ledger in ledgers.values():
		check(ledger.waiting.is_empty() and ledger.reserved.is_empty() and ledger.aboard.is_empty(), "no ghost seats " + label)
	return {"initial": initial, "replanned": replanned}
func _initialize() -> void:
	var a = exercise(Candidate, "candidate")
	var b = exercise(DIY, "DIY")
	check(a == b, "same selected itineraries")
	print("Manual reroute with seat ledger: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
