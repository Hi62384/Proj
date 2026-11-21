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
	var worse_cases := 0
	var better_cases := 0
	var forecast_worse_cases := 0
	var forecast_better_cases := 0
	var incomplete_cases := 0
	var example := {}
	for trial in range(100):
		var stay = Fixture.new(Planner, 20, false)
		var replan = Fixture.new(Planner, 20, true)
		var forecast = Fixture.new(Planner, 20, true, true)
		for i in [1, 2]:
			var period := rng.randi_range(2,8)
			var offset := rng.randi_range(0,period-1)
			var duration := rng.randi_range(1,5)
			var capacity := rng.randi_range(1,3)
			for model in [stay, replan, forecast]:
				model.services[i].period = period
				model.services[i].offset = offset
				model.services[i].duration = duration
				model.services[i].capacity = capacity
				model.ledgers[model.services[i].id].capacity = capacity
		for tick in range(200):
			stay.step()
			replan.step()
			forecast.step()
		var base = arrivals(stay)
		var changed = arrivals(replan)
		var predicted = arrivals(forecast)
		if base.size() != 20 or changed.size() != 20 or predicted.size() != 20:
			incomplete_cases += 1
			continue
		var worse := false
		var better := false
		var forecast_worse := false
		var forecast_better := false
		for id in base:
			if changed[id] > base[id]:
				worse = true
				if example.is_empty():
					example = {"trial":trial, "service_b":stay.services[1].duplicate(true), "service_c":stay.services[2].duplicate(true), "passenger":id, "stay":base[id], "replan":changed[id]}
			elif changed[id] < base[id]:
				better = true
			if predicted[id] > base[id]:
				forecast_worse = true
			elif predicted[id] < base[id]:
				forecast_better = true
		if worse:
			worse_cases += 1
		if better:
			better_cases += 1
		if forecast_worse:
			forecast_worse_cases += 1
		if forecast_better:
			forecast_better_cases += 1
	if example.is_empty():
		failures += 1
		printerr("FAIL: no expected counterexample in seeded sample")
	else:
		print("Counterexample: ", JSON.stringify(example))
	print("Seeded capacity comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", worse_cases, " cases with later passenger, ", better_cases, " with earlier passenger; forecast ", forecast_worse_cases, " cases with later passenger, ", forecast_better_cases, " with earlier passenger; ", incomplete_cases, " incomplete; 100 cases)")
	quit(0 if failures == 0 else 1)
