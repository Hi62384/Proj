extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var a = Fixture.new(Planner, 20, true)
	for t in range(4):
		a.step()
	check(a.passengers.npc02.state == "waiting" and a.passengers.npc02.service == "c", "missed B replans to C")
	check(not a.ledgers.b.waiting.has("npc02") and a.ledgers.c.waiting.has("npc02"), "seat queue transferred once")
	var file = FileAccess.open("user://capacity-replan.dat", FileAccess.WRITE)
	file.store_var(a.snapshot())
	file.close()
	file = FileAccess.open("user://capacity-replan.dat", FileAccess.READ)
	var b = Fixture.restore(file.get_var(), Planner)
	file.close()
	check(b != null and b.capacity_replan, "restore replan mode")
	if b == null:
		quit(1)
		return
	for t in range(150):
		a.step()
		b.step()
		for ledger in a.ledgers.values():
			check(ledger.aboard.size() + ledger.reserved.size() <= ledger.capacity, "capacity invariant")
	check(a.snapshot() == b.snapshot(), "same restored state and events")
	var arrival := -1
	for event in a.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == "npc02":
			arrival = event[0]
	check(arrival == 7, "passenger arrives at tick 7")
	for p in a.passengers.values():
		check(p.state == "completed", "all passengers completed")
	for ledger in a.ledgers.values():
		check(ledger.waiting.is_empty() and ledger.reserved.is_empty() and ledger.aboard.is_empty(), "no ghost seats")
	print("Capacity replan experiment: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; npc02 arrival ", arrival, ")")
	quit(0 if failures == 0 else 1)
