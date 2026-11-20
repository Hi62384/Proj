extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
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
	var incomplete := 0
	var example := {}
	for trial in range(100):
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
			if t == 6:
				for model in [stay,guard]:
					model.disrupt_service("b")
					for id in model.ledgers.b.aboard.duplicate():
						model.acknowledge_rescue(id, model.passengers[id].rescue_token, "hub")
			stay.step()
			guard.step()
		var base = arrivals(stay)
		var changed = arrivals(guard)
		if base.size() != 20 or changed.size() != 20:
			incomplete += 1
			continue
		var worse := false
		var better := false
		for id in base:
			if changed[id] > base[id]:
				worse = true
				if example.is_empty():
					example = {"trial":trial,"id":id,"stay":base[id],"guard":changed[id],"service_b":stay.services[1],"service_c":stay.services[2]}
			elif changed[id] < base[id]:
				better = true
		if worse:
			worse_cases += 1
		if better:
			better_cases += 1
	print("Dynamic disruption sample: ", worse_cases, " cases with later passenger, ", better_cases, " with earlier passenger, ", incomplete, " incomplete; example=", JSON.stringify(example))
	quit(0 if incomplete == 0 else 1)
