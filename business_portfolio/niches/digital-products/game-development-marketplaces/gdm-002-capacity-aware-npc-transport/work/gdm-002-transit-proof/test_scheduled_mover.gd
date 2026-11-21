extends SceneTree
const Schedule = preload("res://callback_schedule.gd")
const Mover = preload("res://fixture_mover.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func board_callback(id: String, token: int, s, vehicle: String) -> void:
	check(s.acknowledge_board(vehicle, id, token), "mover callback accepted")
func _initialize() -> void:
	var s = Schedule.new()
	var movers := {}
	for id in s.passengers:
		var mover = Mover.new()
		get_root().add_child(mover)
		mover.agent_id = id
		mover.speed = 2.0
		movers[id] = mover
	for t in range(103):
		check(s.begin_tick(), "begin")
		for vehicle in ["A", "B"]:
			if s.tick % Schedule.CONFIG[vehicle].period != Schedule.CONFIG[vehicle].offset:
				continue
			for id in s.ledgers[vehicle].reserved.duplicate():
				var mover = movers[id]
				# Controller is deliberately reset for each synthetic boarding movement.
				mover.position = Vector3.ZERO
				var cb = Callable(self, "board_callback").bind(s, vehicle)
				mover.reached.connect(cb, CONNECT_ONE_SHOT)
				mover.move_to(Vector3(1, 0, 0), s.passengers[id].token)
				mover.advance(0.25)
				check(s.passengers[id].state == "boarding", "not boarded before movement completes")
				mover.advance(0.25)
				check(s.passengers[id].state == "onboard", "boarded on movement completion")
		check(s.finish_tick(), "finish")
	for p in s.passengers.values():
		check(p.state == "completed", "completed both legs")
	check(s.trace.size() == 80, "complete trace")
	for mover in movers.values():
		mover.free()
	print("Scheduled mover integration: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", s.trace.size(), " events)")
	quit(0 if failures == 0 else 1)
