extends SceneTree
const Coordinator = preload("res://callback_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var c = Coordinator.new()
	for id in ["a", "b", "c"]:
		check(c.request(id), "request " + id)
	c.open_boarding()
	check(c.ledger.reserved == ["a", "b"] and c.ledger.waiting == ["c"], "FIFO and capacity")
	var a_token: int = c.requests[0].token
	var b_token: int = c.requests[1].token
	check(c.acknowledge_board("a", a_token), "board acknowledged")
	check(not c.acknowledge_board("a", a_token), "duplicate boarding rejected")
	check(c.cancel("b") and not c.acknowledge_board("b", b_token), "cancel rejects stale callback")
	c.open_boarding()
	check(c.requests.size() == 3 and c.requests[2].agent == "c", "released claim allocated")
	check(c.acknowledge_board("c", c.requests[2].token), "next passenger boards")
	check(c.ledger.aboard.size() == 2, "capacity maintained")
	check(c.acknowledge_exit("a") and not c.acknowledge_exit("a"), "exit exactly once")
	check(c.acknowledge_exit("c") and c.ledger.aboard.is_empty(), "all seats released")
	print("Callback fixture: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
