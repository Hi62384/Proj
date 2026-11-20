extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func setup(model) -> void:
	for item in [[1,7,3,4,3], [2,6,1,5,2]]:
		var service: Dictionary = model.services[item[0]]
		service.period = item[1]
		service.offset = item[2]
		service.duration = item[3]
		service.capacity = item[4]
		model.ledgers[service.id].capacity = item[4]
func completed_at(model, id: String) -> int:
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == id:
			return event[0]
	return -1
func _initialize() -> void:
	var stay = Fixture.new(Planner,20,false,false)
	var heuristic = Fixture.new(Planner,20,true,false)
	var forecast = Fixture.new(Planner,20,true,true)
	for model in [stay, heuristic, forecast]:
		setup(model)
	for t in range(200):
		stay.step()
		heuristic.step()
		forecast.step()
	var base := completed_at(stay, "npc08")
	var old := completed_at(heuristic, "npc08")
	var new := completed_at(forecast, "npc08")
	# Reproduction: even the forecast can be worse than leaving the queue unchanged.
	check(base == 14 and old == 18 and new == 18, "known forecast counterexample reproduced")
	for p in forecast.passengers.values():
		check(p.state == "completed", "all passengers complete")
	print("Queue forecast counterexample reproduction: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; stay=", base, " heuristic=", old, " forecast=", new, ")")
	quit(0 if failures == 0 else 1)
