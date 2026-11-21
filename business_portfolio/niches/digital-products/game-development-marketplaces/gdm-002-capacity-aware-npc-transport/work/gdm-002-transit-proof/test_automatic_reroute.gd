extends SceneTree
const Candidate = preload("res://route_planner.gd")
const DIY = preload("res://research/diy_route_baseline.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func exercise(planner, label: String) -> Dictionary:
	var original = Fixture.new(planner)
	for t in range(3):
		original.step()
	check(original.ledgers.b.waiting.size() == 3, "three riders waiting for connection " + label)
	check(original.disable_waiting_service("b"), "disable before departure " + label)
	check(original.ledgers.b.waiting.is_empty() and original.ledgers.c.waiting.size() == 3, "automatic replan to alternate queue " + label)
	var saved = original.snapshot()
	var file = FileAccess.open("user://reroute-" + label + ".dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://reroute-" + label + ".dat", FileAccess.READ)
	var resumed = Fixture.restore(file.get_var(), planner)
	file.close()
	check(resumed != null, "restore disrupted state " + label)
	if resumed == null:
		return {}
	for t in range(150):
		original.step()
		resumed.step()
		for ledger in original.ledgers.values():
			check(ledger.reserved.size() + ledger.aboard.size() <= ledger.capacity, "capacity invariant " + label)
	check(original.snapshot() == resumed.snapshot(), "restored event trace and state match " + label)
	for p in original.passengers.values():
		check(p.state == "completed", "passenger completed after reroute " + label)
	for ledger in original.ledgers.values():
		check(ledger.waiting.is_empty() and ledger.reserved.is_empty() and ledger.aboard.is_empty(), "no ghost seats " + label)
	var broken = saved.duplicate(true)
	broken.ledgers.c.waiting.append(broken.ledgers.c.waiting[0])
	check(Fixture.restore(broken, planner) == null, "duplicate ownership rejected " + label)
	broken = saved.duplicate(true)
	broken.passengers.npc00.stop = "origin"
	check(Fixture.restore(broken, planner) == null, "wrong-stop snapshot rejected " + label)
	return original.snapshot()
func _initialize() -> void:
	var a = exercise(Candidate, "candidate")
	var b = exercise(DIY, "diy")
	check(not a.is_empty() and a == b, "same full reroute trace")
	var boarded = Fixture.new(Candidate)
	for t in range(4):
		boarded.step()
	check(not boarded.ledgers.b.aboard.is_empty(), "baseline B has riders")
	var before = boarded.snapshot()
	check(not boarded.disable_waiting_service("b") and boarded.snapshot() == before, "in-transit disable refused without mutation")
	var unreachable = Fixture.new(Candidate)
	for t in range(3):
		unreachable.step()
	check(unreachable.disable_waiting_service("b") and unreachable.disable_waiting_service("c"), "disable all connections")
	for t in range(100):
		unreachable.step()
	for p in unreachable.passengers.values():
		check(p.state == "failed", "no-route outcome")
	print("Automatic reroute fixture: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", a.get("trace", []).size(), " events)")
	quit(0 if failures == 0 else 1)
