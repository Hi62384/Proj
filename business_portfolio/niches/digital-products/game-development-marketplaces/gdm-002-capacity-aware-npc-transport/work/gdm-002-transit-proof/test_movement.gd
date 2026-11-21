extends SceneTree
const Coordinator = preload("res://callback_fixture.gd")
const Mover = preload("res://fixture_mover.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var coordinator = Coordinator.new()
	var slow = Mover.new()
	var fast = Mover.new()
	get_root().add_child(slow)
	get_root().add_child(fast)
	slow.agent_id = "slow"
	fast.agent_id = "fast"
	slow.speed = 1.0
	fast.speed = 2.0
	coordinator.request("slow")
	coordinator.request("fast")
	coordinator.open_boarding()
	for mover in [slow, fast]:
		mover.reached.connect(func(id, token): coordinator.acknowledge_board(id, token))
		var request: Dictionary = coordinator.requests[0] if mover == slow else coordinator.requests[1]
		mover.move_to(Vector3(2, 0, 0), request.token)
	slow.advance(1.0)
	fast.advance(1.0)
	check(coordinator.state.fast == "onboard" and coordinator.state.slow == "boarding", "different controller speeds and callback")
	check(slow.position == Vector3(1, 0, 0) and fast.position == Vector3(2, 0, 0), "actual 3D positions")
	check(coordinator.cancel("slow"), "cancel during movement")
	slow.advance(1.0)
	check(coordinator.state.slow == "cancelled" and coordinator.ledger.aboard == ["fast"], "late movement callback rejected")
	check(coordinator.acknowledge_exit("fast"), "free boarded seat")
	slow.free()
	fast.free()
	print("3D movement callback fixture: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
