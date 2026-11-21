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
	for item in [[1,3,1,3,1], [2,4,2,2,1]]:
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
	var stay = Candidate.new(Planner,20,false,false,false)
	var guard = Candidate.new(Planner,20,true,false,true)
	var diy = DIY.new(DIYPlanner,20,true,true)
	configure(stay,true)
	configure(guard,true)
	configure(diy,false)
	for t in range(200):
		if t == 6:
			for model in [stay,guard,diy]:
				check(model.disrupt_service("b"), "disrupt B")
				for id in model.passengers:
					if model.passengers[id].state == "stranded" and model.passengers[id].service == "b":
						check(model.acknowledge_rescue(id,model.passengers[id].rescue_token,"hub"), "rescue B rider")
		stay.step()
		guard.step()
		diy.step()
	check(completed_at(stay,"npc01") == 8 and completed_at(guard,"npc01") == 12, "disruption makes guarded passenger later")
	check(guard.trace == diy.trace and guard.passengers == diy.passengers, "DIY reproduces guarded trace")
	for p in guard.passengers.values():
		check(p.state == "completed", "all passengers complete")
	print("Guarded disruption counterexample: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; npc01 stay=8 guard=12)")
	quit(0 if failures == 0 else 1)
