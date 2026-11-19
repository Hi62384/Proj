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
func configure(model, is_candidate: bool) -> void:
	for item in [[1,7,3,4,3], [2,6,1,5,2]]:
		var service: Dictionary = model.services[item[0]]
		service.period = item[1]
		service.offset = item[2]
		service.duration = item[3]
		service.capacity = item[4]
		if is_candidate:
			model.ledgers[service.id].capacity = item[4]
func completed_at(model, id: String) -> int:
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == id:
			return event[0]
	return -1
func _initialize() -> void:
	var stay = Candidate.new(Planner, 20, false)
	var reroute = Candidate.new(Planner, 20, true)
	var diy = DIY.new(DIYPlanner, 20, true)
	configure(stay, true)
	configure(reroute, true)
	configure(diy, false)
	for t in range(200):
		stay.step()
		reroute.step()
		diy.step()
	var baseline := completed_at(stay, "npc08")
	var changed := completed_at(reroute, "npc08")
	check(baseline == 14 and changed == 18, "heuristic delays npc08 from tick 14 to 18")
	check(reroute.trace == diy.trace and reroute.passengers == diy.passengers, "candidate and DIY match")
	for p in reroute.passengers.values():
		check(p.state == "completed", "all passengers eventually complete")
	print("Capacity counterexample replay: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; npc08 stay=", baseline, " replan=", changed, ")")
	quit(0 if failures == 0 else 1)
