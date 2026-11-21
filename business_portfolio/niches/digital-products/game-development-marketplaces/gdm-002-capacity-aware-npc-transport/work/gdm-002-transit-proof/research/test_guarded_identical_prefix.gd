extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func configure(model) -> void:
	for item in [[1,3,1,3,1], [2,4,2,2,1]]:
		var service: Dictionary = model.services[item[0]]
		service.period = item[1]
		service.offset = item[2]
		service.duration = item[3]
		service.capacity = item[4]
		model.ledgers[service.id].capacity = item[4]
func arrival(model, id: String) -> int:
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == id:
			return event[0]
	return -1
func _initialize() -> void:
	var stable_stay = Fixture.new(Planner,20,false,false,false)
	var stable_guard = Fixture.new(Planner,20,true,false,true)
	var disrupted_stay = Fixture.new(Planner,20,false,false,false)
	var disrupted_guard = Fixture.new(Planner,20,true,false,true)
	for model in [stable_stay,stable_guard,disrupted_stay,disrupted_guard]:
		configure(model)
	for t in range(6):
		for model in [stable_stay,stable_guard,disrupted_stay,disrupted_guard]:
			model.step()
	check(stable_stay.trace == disrupted_stay.trace and stable_guard.trace == disrupted_guard.trace, "same histories before event")
	var switches := 0
	for event in stable_guard.trace:
		if event.size() >= 2 and event[1] == "capacity_replan":
			switches += 1
	check(switches > 0, "guard switched before event")
	for model in [disrupted_stay,disrupted_guard]:
		check(model.disrupt_service("b"), "disrupt B")
		for id in model.ledgers.b.aboard.duplicate():
			check(model.acknowledge_rescue(id,model.passengers[id].rescue_token,"hub"), "rescue")
	for t in range(194):
		for model in [stable_stay,stable_guard,disrupted_stay,disrupted_guard]:
			model.step()
	for id in stable_stay.passengers:
		check(arrival(stable_stay,id) >= 0 and arrival(stable_guard,id) >= 0, "static completion")
		check(arrival(stable_guard,id) <= arrival(stable_stay,id), "static guard no later for " + id)
	check(arrival(disrupted_stay,"npc01") == 8 and arrival(disrupted_guard,"npc01") == 12, "unexpected event changes outcome")
	print("Guarded identical-prefix counterexample: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; prior switches ", switches, "; static npc01 ", arrival(stable_stay,"npc01"), "/", arrival(stable_guard,"npc01"), "; disrupted 8/12)")
	quit(0 if failures == 0 else 1)
