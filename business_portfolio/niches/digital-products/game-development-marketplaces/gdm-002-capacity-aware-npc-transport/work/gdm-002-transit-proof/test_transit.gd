extends SceneTree

const Transit = preload("res://transit.gd")
var failures := 0

func check(condition: bool, label: String) -> void:
	if not condition:
		failures += 1
		printerr("FAIL: ", label)

func _initialize() -> void:
	var first = Transit.new(1)
	check(first.request("a") and first.request("b"), "queue requests")
	first.allocate()
	check(first.reserved == ["a"] and first.waiting == ["b"], "FIFO final seat")
	check(first.cancel("a") and not first.cancel("a"), "cancel exactly once")
	check(not first.board("a"), "late callback rejected")
	first.allocate()
	var saved = first.snapshot()
	var restored = Transit.restore(saved)
	check(restored != null and restored.snapshot() == saved, "snapshot round trip")
	check(restored.board("b") and not restored.board("b"), "duplicate boarding rejected")
	var invalid = saved.duplicate(true)
	invalid.aboard.append("other")
	check(Transit.restore(invalid) == null, "overcapacity rejected")
	invalid = saved.duplicate(true)
	invalid.waiting.append("b")
	check(Transit.restore(invalid) == null, "duplicate ownership rejected")
	var vehicles = [Transit.new(5), Transit.new(5)]
	for i in range(20):
		check(vehicles[i % 2].request("npc%02d" % i), "synthetic request")
	for vehicle in vehicles:
		vehicle.allocate()
		check(vehicle.reserved.size() == 5 and vehicle.waiting.size() == 5, "two vehicle capacity")
	print("Transit proof: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
