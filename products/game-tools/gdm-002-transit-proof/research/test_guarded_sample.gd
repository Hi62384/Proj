extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func arrivals(model) -> Dictionary:
	var result := {}
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed":
			result[event[2]] = event[0]
	return result
func _initialize() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42931
	var improved_cases := 0
	var switches := 0
	var started := Time.get_ticks_usec()
	for trial in range(30):
		var stay = Fixture.new(Planner,20,false,false,false)
		var guard = Fixture.new(Planner,20,true,false,true)
		for i in [1,2]:
			var period := rng.randi_range(2,8)
			var offset := rng.randi_range(0,period-1)
			var duration := rng.randi_range(1,5)
			var capacity := rng.randi_range(1,3)
			for model in [stay,guard]:
				model.services[i].period = period
				model.services[i].offset = offset
				model.services[i].duration = duration
				model.services[i].capacity = capacity
				model.ledgers[model.services[i].id].capacity = capacity
		for t in range(200):
			stay.step()
			guard.step()
		var base = arrivals(stay)
		var changed = arrivals(guard)
		if base.size() != 20 or changed.size() != 20:
			failures += 1
			printerr("FAIL: incomplete trial ", trial)
			continue
		var improved := false
		for id in base:
			if changed[id] > base[id]:
				failures += 1
				printerr("FAIL: later passenger ", id, " trial ", trial, " stay ", base[id], " guard ", changed[id])
			elif changed[id] < base[id]:
				improved = true
		if improved:
			improved_cases += 1
		for event in guard.trace:
			if event.size() >= 2 and event[1] == "capacity_replan":
				switches += 1
	print("Guarded static sample: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", improved_cases, " cases improved; ", switches, " switches; 30 cases; ", (Time.get_ticks_usec()-started)/1000000.0, " seconds)")
	quit(0 if failures == 0 else 1)
