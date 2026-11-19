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
	check(c.begin_tick() and d.begin_tick(), "open first window")
	var stale: int = c.passengers.npc02.token
	check(c.cancel("npc00") and d.cancel("npc00"), "cancel first reservation")
	check(not c.cancel("npc00") and not d.cancel("npc00"), "duplicate cancellation")
	check(not c.acknowledge_board("A", "npc00", 1) and not d.acknowledge_board("A", "npc00", 1), "cancelled callback")
	check(c.acknowledge_board("A", "npc01", 1) and d.acknowledge_board("A", "npc01", 1), "single successful board")
	var csave = c.snapshot()
	var dsave = d.snapshot()
	var file = FileAccess.open("user://comparison-snapshots.dat", FileAccess.WRITE)
	file.store_var({"candidate": csave, "diy": dsave})
	file.close()
	file = FileAccess.open("user://comparison-snapshots.dat", FileAccess.READ)
	var disk: Dictionary = file.get_var()
	file.close()
	var cr = Candidate.restore(disk.candidate)
	var dr = DIY.restore(disk.diy)
	var bad_c = csave.duplicate(true)
	bad_c.ledgers.B.waiting.append("npc01")
	var bad_d = dsave.duplicate(true)
	bad_d.queues.B.append("npc01")
	check(Candidate.restore(bad_c) == null, "candidate rejects duplicate ownership")
	check(DIY.restore(bad_d) == null, "DIY baseline rejects duplicate ownership")
	check(cr != null and dr != null, "restore during boarding")
	check(not cr.acknowledge_board("A", "npc01", 1) and not dr.acknowledge_board("A", "npc01", 1), "duplicate callback after restore")
	cr.finish_tick()
	dr.finish_tick()
	for i in range(1, 103):
		cr.begin_tick()
		dr.begin_tick()
		if i == 4:
			check(not cr.acknowledge_board("A", "npc02", stale) and not dr.acknowledge_board("A", "npc02", stale), "old departure token rejected")
		for v in ["A", "B"]:
			for id in cr.ledgers[v].reserved.duplicate():
				check(cr.acknowledge_board(v, id, cr.passengers[id].token), "candidate acknowledgment")
				check(dr.acknowledge_board(v, id, dr.people[id].token), "DIY acknowledgment")
		cr.finish_tick()
		dr.finish_tick()
	check(cr.trace == dr.trace, "same negative-case event trace")
	for id in cr.passengers:
		check(cr.passengers[id] == dr.people[id], "matching passenger outcome")
	check(cr.passengers.npc00.state == "cancelled", "cancelled remains cancelled")
	var completed := 0
	for p in cr.passengers.values():
		if p.state == "completed":
			completed += 1
	check(completed == 19, "other 19 arrive")
	print("Validated DIY comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", cr.trace.size(), " events; ", completed, " completed)")
	quit(0 if failures == 0 else 1)
