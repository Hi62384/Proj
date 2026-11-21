extends SceneTree
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var c = Candidate.new()
	var d = DIY.new()
	for t in range(3):
		c.begin_tick()
		d.begin_tick()
		for v in ["A", "B"]:
			for id in c.ledgers[v].reserved.duplicate():
				check(c.acknowledge_board(v, id, c.passengers[id].token), "candidate boarding")
				check(d.acknowledge_board(v, id, d.people[id].token), "DIY boarding")
		c.finish_tick()
		d.finish_tick()
	check(c.phase == "ready" and c.tick == 3 and c.ledgers.B.aboard.size() == 2, "two riders in transit")
	check(c.disrupt_final_leg() and d.disrupt_final_leg(), "disruption in transit")
	check(not c.disrupt_final_leg() and not d.disrupt_final_leg(), "duplicate disruption ignored")
	check(c.ledgers.B.aboard.size() == 2 and d.riders.B.size() == 2, "stranded retain seats")
	check(c.passengers.npc00.state == "stranded" and d.people.npc00.state == "stranded", "explicit stranded state")
	var cs = c.snapshot()
	var ds = d.snapshot()
	var file = FileAccess.open("user://midride-saves.dat", FileAccess.WRITE)
	file.store_var({"candidate": cs, "diy": ds})
	file.close()
	file = FileAccess.open("user://midride-saves.dat", FileAccess.READ)
	var saved: Dictionary = file.get_var()
	file.close()
	var cr = Candidate.restore(saved.candidate)
	var dr = DIY.restore(saved.diy)
	check(cr != null and dr != null, "restore stranded state")
	if cr == null or dr == null:
		quit(1)
		return
	cr.begin_tick()
	dr.begin_tick()
	check(cr.ledgers.B.aboard.size() == 2 and dr.riders.B.size() == 2, "scheduled arrival does not erase stranded riders")
	for id in ["npc00", "npc01"]:
		var token: int = cr.passengers[id].token
		check(not cr.acknowledge_rescue(id, token - 1) and not dr.acknowledge_rescue(id, token - 1), "stale rescue rejected")
		check(cr.acknowledge_rescue(id, token) and dr.acknowledge_rescue(id, token), "rescue acknowledged")
		check(not cr.acknowledge_rescue(id, token) and not dr.acknowledge_rescue(id, token), "duplicate rescue rejected")
	check(cr.trace == dr.trace, "same disruption and rescue trace")
	for id in cr.passengers:
		check(cr.passengers[id] == dr.people[id] and cr.passengers[id].state == "failed", "identical explicit outcomes")
	for v in ["A", "B"]:
		check(cr.ledgers[v].waiting.is_empty() and cr.ledgers[v].reserved.is_empty() and cr.ledgers[v].aboard.is_empty(), "candidate no claims")
		check(dr.queues[v].is_empty() and dr.claims[v].is_empty() and dr.riders[v].is_empty(), "DIY no claims")
	print("Mid-ride disruption comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
