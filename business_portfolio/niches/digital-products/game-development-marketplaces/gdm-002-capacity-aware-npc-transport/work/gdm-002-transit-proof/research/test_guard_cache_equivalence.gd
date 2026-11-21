extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const CandidateRef = preload("res://research/auto_uncached_reference.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
const DIYRef = preload("res://research/diy_uncached_reference.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 78603
	var candidate_cached := 0
	var candidate_reference := 0
	var diy_cached := 0
	var diy_reference := 0
	for trial in range(50):
		var c = Candidate.new(Planner,20,true,false,true)
		var cr = CandidateRef.new(Planner,20,true,false,true)
		var d = DIY.new(DIYPlanner,20,true,true)
		var dr = DIYRef.new(DIYPlanner,20,true,true)
		for i in [1,2]:
			var period := rng.randi_range(2,8)
			var offset := rng.randi_range(0,period-1)
			var duration := rng.randi_range(1,5)
			var capacity := rng.randi_range(1,3)
			for model in [c,cr,d,dr]:
				model.services[i].period = period
				model.services[i].offset = offset
				model.services[i].duration = duration
				model.services[i].capacity = capacity
			c.ledgers[c.services[i].id].capacity = capacity
			cr.ledgers[cr.services[i].id].capacity = capacity
		for t in range(150):
			if t == 6 and trial % 2 == 1:
				for model in [c,cr,d,dr]:
					check(model.disrupt_service("b"), "disable B")
					for id in model.passengers:
						if model.passengers[id].state == "stranded" and model.passengers[id].service == "b":
							check(model.acknowledge_rescue(id,model.passengers[id].rescue_token,"hub"), "rescue")
			c.step()
			cr.step()
			d.step()
			dr.step()
			if c.trace != cr.trace or c.passengers != cr.passengers or d.trace != dr.trace or d.passengers != dr.passengers:
				failures += 1
				printerr("FAIL: trace mismatch at trial ", trial, " tick ", t)
				break
		check(c.trace == d.trace and c.passengers == d.passengers, "candidate/DIY equality " + str(trial))
		candidate_cached += c.baseline_evaluations
		candidate_reference += cr.baseline_evaluations
		diy_cached += d.baseline_evaluations
		diy_reference += dr.baseline_evaluations
	check(candidate_cached < candidate_reference and diy_cached < diy_reference, "cache reduced baseline projections")
	print("Guard cache equivalence: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 50 cases; candidate projections ", candidate_cached, "/", candidate_reference, "; DIY ", diy_cached, "/", diy_reference, ")")
	quit(0 if failures == 0 else 1)
