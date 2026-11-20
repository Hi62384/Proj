extends SceneTree
const Schedule = preload("res://callback_schedule.gd")
const Mover = preload("res://fixture_mover.gd")
const Adapter = preload("res://fixture_recovery_adapter.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var s = Schedule.new(1)
	var mover = Mover.new()
	get_root().add_child(mover)
	mover.agent_id = "npc00"
	mover.speed = 1.0
	var adapter = Adapter.new(mover, s, "A")
	s.begin_tick()
	adapter.begin_boarding(Vector3(1, 0, 0))
	mover.advance(0.5)
	check(mover.position == Vector3(0.5, 0, 0), "partial boarding movement")
	s.finish_tick()
	check(adapter.recover_missed(), "return command issued")
	mover.advance(0.5)
	check(mover.position == Vector3.ZERO and s.passengers.npc00.state == "waiting", "physically returned to waiting point")
	for i in range(3):
		s.begin_tick()
		s.finish_tick()
	s.begin_tick()
	adapter.begin_boarding(Vector3(1, 0, 0))
	mover.advance(1.0)
	check(s.passengers.npc00.state == "onboard", "recovered passenger boards next departure")
	s.finish_tick()
	mover.free()
	print("Missed boarding recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
