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
	for t in range(2):
		c.begin_tick()
		d.begin_tick()
		for v in ["A", "B"]:
			for id in c.ledgers[v].reserved.duplicate():
				check(c.acknowledge_board(v, id, c.passengers[id].token), "candidate board")
				check(d.acknowledge_board(v, id, d.people[id].token), "DIY board")
		c.finish_tick()
		d.finish_tick()
	c.begin_tick()
	d.begin_tick()
	for id in c.ledgers.B.reserved.duplicate():
		check(c.acknowledge_board("B", id, c.passengers[id].token), "candidate B board")
		check(d.acknowledge_board("B", id, d.people[id].token), "DIY B board")
	check(c.ledgers.B.aboard.size() == 2 and d.riders.B.size() == 2, "two riders in disrupted vehicle")
	check(c.disrupt_final_leg() and d.disrupt_final_leg(), "disruption accepted")
	check(not c.disrupt_final_leg() and not d.disrupt_final_leg(), "duplicate disruption ignored")
	check(not c.acknowledge_board("B", "npc00", 2) and not d.acknowledge_board("B", "npc00", 2), "late callback rejected")
	check(c.ledgers.B.aboard.size() == 2 and d.riders.B.size() == 2, "stranded seats held")
	for id in ["npc00", "npc01"]:
		check(c.acknowledge_rescue(id, c.passengers[id].token), "candidate rescue")
		check(d.acknowledge_rescue(id, d.people[id].token), "DIY rescue")
	check(c.trace == d.trace, "matching disruption events")
	for id in c.passengers:
		if c.passengers[id] != d.people[id] or c.passengers[id].state != "failed":
			printerr("Mismatch ", id, " candidate=", c.passengers[id], " DIY=", d.people[id])
		check(c.passengers[id] == d.people[id] and c.passengers[id].state == "failed", "explicit identical failure")
	for v in ["A", "B"]:
		check(c.ledgers[v].waiting.is_empty() and c.ledgers[v].reserved.is_empty() and c.ledgers[v].aboard.is_empty(), "no remaining claims")
		check(d.queues[v].is_empty() and d.claims[v].is_empty() and d.riders[v].is_empty(), "DIY no remaining claims")
	check(Candidate.restore(c.snapshot()) != null and DIY.restore(d.snapshot()) != null, "restore disrupted state")
	print("Fixed-route disruption comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
