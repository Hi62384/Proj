extends SceneTree
const Planner = preload("res://route_planner.gd")
const DIYPlanner = preload("res://research/diy_route_baseline.gd")
const Candidate = preload("res://automatic_reroute_fixture.gd")
const DIY = preload("res://research/diy_auto_validated.gd")
const CandidateRef = preload("res://research/auto_uncached_reference.gd")
const DIYRef = preload("res://research/diy_uncached_reference.gd")
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
	var samples = {"candidate_cached": [], "candidate_uncached": [], "diy_cached": [], "diy_uncached": []}
	var tick_counts := []
	var evaluations = {"candidate_cached":0, "candidate_uncached":0, "diy_cached":0, "diy_uncached":0}
	for run_index in range(WARMUP + RUNS):
		var models = {
			"candidate_cached": Candidate.new(Planner,20,true,false,true),
			"candidate_uncached": CandidateRef.new(Planner,20,true,false,true),
			"diy_cached": DIY.new(DIYPlanner,20,true,true),
			"diy_uncached": DIYRef.new(DIYPlanner,20,true,true)
		}
		var names = ["candidate_cached", "candidate_uncached", "diy_cached", "diy_uncached"]
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
		check(models.candidate_cached.trace == models.candidate_uncached.trace, "candidate traces match")
		check(models.diy_cached.trace == models.diy_uncached.trace, "DIY traces match")
		if run_index >= WARMUP:
			for name in names:
				evaluations[name] += models[name].baseline_evaluations
			tick_counts.append([models.candidate_cached.tick, models.diy_cached.tick])
	var result := {"runs": RUNS, "warmup_runs": WARMUP, "candidate_cached":summarize(samples.candidate_cached), "candidate_uncached":summarize(samples.candidate_uncached), "diy_cached":summarize(samples.diy_cached), "diy_uncached":summarize(samples.diy_uncached), "first_tick_counts":tick_counts[0], "baseline_projections":evaluations}
	print("Guard cache tick measurement: ", "PASS" if failures == 0 else "FAIL", " ", JSON.stringify(result))
	quit(0 if failures == 0 else 1)
