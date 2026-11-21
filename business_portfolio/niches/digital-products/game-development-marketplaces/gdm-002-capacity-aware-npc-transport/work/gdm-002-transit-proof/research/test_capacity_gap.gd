extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func run_case(model, planner, label: String) -> void:
	for t in range(4):
		model.step()
	var queue: Array = model.ledgers.b.waiting if label == "ledger" else model.waiting.b
	check(queue.size() == 1, "one passenger missed a full B departure " + label)
	if queue.size() != 1:
		return
	var id: String = queue[0]
	var next_route = planner.plan(model.stops, model.services, "hub", "end", model.tick)
	check(next_route.ok and next_route.legs[0].service == "c" and next_route.arrival == 7, "alternative C arrives at tick 7 " + label)
	check(model.passengers[id].state == "waiting" and model.passengers[id].service == "b", "passenger remains queued for B " + label)
	while model.tick <= 10:
		model.step()
	var arrived := -1
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == id:
			arrived = event[0]
	check(arrived == 10, "passenger reaches destination at tick 10 " + label)
	print(label, " missed-capacity case: alternate=7 actual=", arrived, " passenger=", id)
func _initialize() -> void:
	run_case(Candidate.new(Planner), Planner, "ledger")
	run_case(DIY.new(DIYPlanner), DIYPlanner, "diy")
	print("Capacity-reroute gap reproduction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
