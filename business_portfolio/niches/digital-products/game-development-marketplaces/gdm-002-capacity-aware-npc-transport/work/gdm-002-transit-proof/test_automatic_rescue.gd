extends SceneTree
const Candidate = preload("res://route_planner.gd")
const DIY = preload("res://research/diy_route_baseline.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func run_case(planner, label: String) -> Dictionary:
	var original = Fixture.new(planner)
	for t in range(4):
		original.step()
	check(original.ledgers.b.aboard.size() == 2, "two riders in transit " + label)
	check(original.disrupt_service("b"), "disable B with riders " + label)
	check(not original.disrupt_service("b"), "duplicate disruption rejected " + label)
	var riders: Array = original.ledgers.b.aboard.duplicate()
	check(riders.size() == 2 and original.passengers[riders[0]].state == "stranded", "stranded retain seats " + label)
	var file = FileAccess.open("user://reroute-rescue-" + label + ".dat", FileAccess.WRITE)
	file.store_var(original.snapshot())
	file.close()
	file = FileAccess.open("user://reroute-rescue-" + label + ".dat", FileAccess.READ)
	var resumed = Fixture.restore(file.get_var(), planner)
	file.close()
	check(resumed != null, "restore with stranded riders " + label)
	if resumed == null:
		return {}
	original.step()
	resumed.step()
	check(original.ledgers.b.aboard.size() == 2 and resumed.ledgers.b.aboard.size() == 2, "no automatic disembark " + label)
	for id in riders:
		var token: int = original.passengers[id].rescue_token
		check(not original.acknowledge_rescue(id, token-1, "hub"), "stale rescue rejected " + label)
		check(not original.acknowledge_rescue(id, token, "end"), "unsupported recovery point rejected " + label)
		check(original.acknowledge_rescue(id, token, "hub") and resumed.acknowledge_rescue(id, token, "hub"), "rescue and replan " + label)
		check(not original.acknowledge_rescue(id, token, "hub"), "duplicate rescue rejected " + label)
	for t in range(150):
		original.step()
		resumed.step()
		for ledger in original.ledgers.values():
			check(ledger.aboard.size() + ledger.reserved.size() <= ledger.capacity, "capacity " + label)
	check(original.snapshot() == resumed.snapshot(), "same restored trace " + label)
	for p in original.passengers.values():
		check(p.state == "completed", "all completed after rescue " + label)
	for ledger in original.ledgers.values():
		check(ledger.waiting.is_empty() and ledger.reserved.is_empty() and ledger.aboard.is_empty(), "no ghost claims " + label)
	return original.snapshot()
func _initialize() -> void:
	var a = run_case(Candidate, "candidate")
	var b = run_case(DIY, "diy")
	check(not a.is_empty() and a == b, "same full rescue and replan trace")
	print("Automatic disruption recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", a.get("trace", []).size(), " events)")
	quit(0 if failures == 0 else 1)
