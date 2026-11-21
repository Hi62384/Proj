extends SceneTree
const Schedule = preload("res://callback_schedule.gd")
const Original = preload("res://scheduled_fixture.gd")
var failures := 0
func check(ok: bool, text: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", text)
func finish_boarding(s) -> void:
	for vehicle in ["A", "B"]:
		for id in s.ledgers[vehicle].reserved.duplicate():
			if s.tick % Schedule.CONFIG[vehicle].period == Schedule.CONFIG[vehicle].offset:
				check(s.acknowledge_board(vehicle, id, s.passengers[id].token), "boarding callback")
	check(s.finish_tick(), "finish tick")
func _initialize() -> void:
	var a = Schedule.new()
	check(a.begin_tick(), "begin")
	check(a.acknowledge_board("A", "npc00", a.passengers.npc00.token), "one callback before save")
	var saved = a.snapshot()
	var file = FileAccess.open("user://callback-schedule.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://callback-schedule.dat", FileAccess.READ)
	var b = Schedule.restore(file.get_var())
	file.close()
	check(b != null, "restore mid-boarding")
	if b == null:
		quit(1)
		return
	check(not b.acknowledge_board("A", "npc00", b.passengers.npc00.token), "duplicate callback after restore")
	finish_boarding(a)
	finish_boarding(b)
	for i in range(102):
		check(a.begin_tick() and b.begin_tick(), "begin tick")
		finish_boarding(a)
		finish_boarding(b)
	check(a.snapshot() == b.snapshot(), "disk restore replay matches")
	for p in a.passengers.values():
		check(p.state == "completed", "journey completed")
	check(a.trace.size() == 80, "two legs per passenger")
	var original = Original.new()
	for i in range(103):
		original.step()
	check(a.trace == original.journal, "same trace as original schedule")
	var delayed = Schedule.new(1)
	delayed.begin_tick()
	delayed.finish_tick()
	check(delayed.passengers.npc00.state == "waiting" and delayed.ledgers.A.waiting == ["npc00"], "missed boarding returns to queue")
	delayed.begin_tick()
	check(not delayed.acknowledge_board("A", "npc00", delayed.passengers.npc00.token), "late callback outside departure rejected")
	delayed.finish_tick()
	for i in range(2):
		delayed.begin_tick()
		delayed.finish_tick()
	check(delayed.passengers.npc00.state == "waiting" and delayed.ledgers.A.waiting == ["npc00"], "missed boarding returns to queue")
	delayed.begin_tick()
	check(not delayed.acknowledge_board("A", "npc00", 1), "prior departure token rejected")
	check(delayed.acknowledge_board("A", "npc00", 2), "current departure token accepted")
	delayed.finish_tick()
	var fairness = Schedule.new(4)
	fairness.begin_tick()
	check(fairness.acknowledge_board("A", "npc00", fairness.passengers.npc00.token), "one passenger boards")
	fairness.finish_tick()
	check(fairness.ledgers.A.waiting == ["npc01", "npc02", "npc03"], "missed passengers retain FIFO priority")
	var cancellation = Schedule.new(4)
	cancellation.begin_tick()
	var old_token: int = cancellation.passengers.npc00.token
	check(cancellation.cancel("npc00"), "cancel reservation")
	check(not cancellation.acknowledge_board("A", "npc00", old_token), "cancelled callback rejected")
	check(not cancellation.cancel("npc00"), "duplicate cancellation rejected")
	check(Schedule.restore(cancellation.snapshot()) != null, "cancelled state restores")
	cancellation.finish_tick()
	check(cancellation.ledgers.A.waiting == ["npc01", "npc02", "npc03"], "remaining queue preserved")
	var invalid = saved.duplicate(true)
	invalid.ledgers.B.waiting.append("npc00")
	check(Schedule.restore(invalid) == null, "cross-vehicle ownership rejected")
	print("Callback schedule: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", a.trace.size(), " events)")
	quit(0 if failures == 0 else 1)
