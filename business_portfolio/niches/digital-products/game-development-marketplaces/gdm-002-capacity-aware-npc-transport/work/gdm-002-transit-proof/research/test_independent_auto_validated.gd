extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var c = Candidate.new(Planner)
	var d = DIY.new(DIYPlanner)
	for t in range(4):
		c.step()
		d.step()
	check(c.ledgers.b.aboard.size() == 2 and d.aboard.b.size() == 2, "two riders in transit")
	check(c.disrupt_service("b") and d.disrupt_service("b"), "service disrupted")
	check(c.trace == d.trace and c.passengers == d.passengers, "matching disruption state")
	var file = FileAccess.open("user://independent-auto-comparison.dat", FileAccess.WRITE)
	file.store_var({"candidate": c.snapshot(), "diy": d.snapshot()})
	file.close()
	file = FileAccess.open("user://independent-auto-comparison.dat", FileAccess.READ)
	var data: Dictionary = file.get_var()
	file.close()
	var cr = Candidate.restore(data.candidate, Planner)
	var dr = DIY.restore(data.diy, DIYPlanner)
	check(cr != null and dr != null, "stranded state restored")
	if cr == null or dr == null:
		quit(1)
		return
	cr.step()
	dr.step()
	for id in ["npc00", "npc01"]:
		var token: int = cr.passengers[id].rescue_token
		check(not cr.acknowledge_rescue(id, token-1, "hub") and not dr.acknowledge_rescue(id, token-1, "hub"), "stale rescue rejected")
		check(cr.acknowledge_rescue(id, token, "hub") and dr.acknowledge_rescue(id, token, "hub"), "rescue and reroute")
	for t in range(150):
		cr.step()
		dr.step()
	check(cr.trace == dr.trace and cr.passengers == dr.passengers, "same independent full trace and outcomes")
	for id in cr.passengers:
		check(cr.passengers[id].state == "completed", "completed " + id)
	for service in cr.services:
		check(cr.ledgers[service.id].waiting.is_empty() and cr.ledgers[service.id].aboard.is_empty() and dr.waiting[service.id].is_empty() and dr.aboard[service.id].is_empty(), "no ghost claims")
	var corrupt_c = data.candidate.duplicate(true)
	corrupt_c.ledgers.b.aboard.append(corrupt_c.ledgers.b.aboard[0])
	var corrupt_d = data.diy.duplicate(true)
	corrupt_d.aboard.b.append(corrupt_d.aboard.b[0])
	check(Candidate.restore(corrupt_c, Planner) == null and DIY.restore(corrupt_d, DIYPlanner) == null, "duplicate ownership rejected")
	corrupt_c = data.candidate.duplicate(true)
	corrupt_d = data.diy.duplicate(true)
	corrupt_c.passengers.npc00.stop = "origin"
	corrupt_d.passengers.npc00.stop = "origin"
	check(Candidate.restore(corrupt_c, Planner) == null, "candidate rejects wrong stop")
	check(DIY.restore(corrupt_d, DIYPlanner) == null, "validated DIY rejects wrong-stop state")
	print("Validated automatic reroute comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", cr.trace.size(), " events)")
	quit(0 if failures == 0 else 1)
