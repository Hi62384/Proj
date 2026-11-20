extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
const WARMUP := 2
const RUNS := 20
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func all_finished(model) -> bool:
	for p in model.passengers.values():
		if p.state != "completed":
			return false
	return true
func summarize(samples: Array) -> Dictionary:
	var ordered = samples.duplicate()
	ordered.sort()
	var sum := 0
	var over := 0
	for value in ordered:
		sum += value
		if value > 16667:
			over += 1
	return {"samples": ordered.size(), "mean_us": float(sum) / ordered.size(), "median_us": ordered[(ordered.size()-1)/2], "p95_us": ordered[ceili(ordered.size()*0.95)-1], "p99_us": ordered[ceili(ordered.size()*0.99)-1], "max_us": ordered.back(), "over_16_667us": over}
func _initialize() -> void:
	var samples = {"candidate_default": [], "diy_default": [], "candidate_guarded": [], "diy_guarded": []}
	var tick_counts := []
	for run_index in range(WARMUP + RUNS):
		var models = {
			"candidate_default": Candidate.new(Planner,20,false,false,false),
			"diy_default": DIY.new(DIYPlanner,20,false,false),
			"candidate_guarded": Candidate.new(Planner,20,true,false,true),
			"diy_guarded": DIY.new(DIYPlanner,20,true,true)
		}
		var names = ["candidate_default", "diy_default", "candidate_guarded", "diy_guarded"]
		if run_index % 2 == 1:
			names.reverse()
		for tick in range(100):
			var finished := true
			for name in names:
				var model = models[name]
				if all_finished(model):
					continue
				finished = false
				var start := Time.get_ticks_usec()
				model.step()
				var elapsed := Time.get_ticks_usec() - start
				if run_index >= WARMUP:
					samples[name].append(elapsed)
			if finished:
				break
		for name in names:
			check(all_finished(models[name]), "20 completed " + name)
		check(models.candidate_default.trace == models.diy_default.trace, "default traces match")
		check(models.candidate_guarded.trace == models.diy_guarded.trace, "guarded traces match")
		if run_index >= WARMUP:
			tick_counts.append([models.candidate_default.tick, models.candidate_guarded.tick])
	var result := {"runs": RUNS, "warmup_runs": WARMUP, "candidate_default":summarize(samples.candidate_default), "diy_default":summarize(samples.diy_default), "candidate_guarded":summarize(samples.candidate_guarded), "diy_guarded":summarize(samples.diy_guarded), "first_tick_counts":tick_counts[0]}
	print("Guarded tick measurement: ", "PASS" if failures == 0 else "FAIL", " ", JSON.stringify(result))
	quit(0 if failures == 0 else 1)
