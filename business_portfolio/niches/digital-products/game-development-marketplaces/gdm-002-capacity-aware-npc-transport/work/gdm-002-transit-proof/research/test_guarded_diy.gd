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
func _initialize() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42931
	var started := Time.get_ticks_usec()
	for trial in range(30):
		var c = Candidate.new(Planner,20,true,false,true)
		var d = DIY.new(DIYPlanner,20,true,true)
		for i in [1,2]:
			var period := rng.randi_range(2,8)
			var offset := rng.randi_range(0,period-1)
			var duration := rng.randi_range(1,5)
			var capacity := rng.randi_range(1,3)
			for model in [c,d]:
				model.services[i].period = period
				model.services[i].offset = offset
				model.services[i].duration = duration
				model.services[i].capacity = capacity
			c.ledgers[c.services[i].id].capacity = capacity
		for t in range(200):
			c.step()
			d.step()
		check(c.trace == d.trace and c.passengers == d.passengers, "matching guarded trace %d" % trial)
		for p in c.passengers.values():
			check(p.state == "completed", "completed %d" % trial)
	var a = Candidate.new(Planner,20,true,false,true)
	var b = DIY.new(DIYPlanner,20,true,true)
	for t in range(4):
		a.step()
		b.step()
	var ar = Candidate.restore(a.snapshot(),Planner)
	var br = DIY.restore(b.snapshot(),DIYPlanner)
	check(ar != null and br != null and ar.guarded_replan and br.guarded_replan, "guard flag restored")
	if ar != null and br != null:
		for t in range(100):
			ar.step()
			br.step()
		check(ar.trace == br.trace and ar.passengers == br.passengers, "guarded restore continuation")
	print("Guarded DIY comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 30 cases; ", (Time.get_ticks_usec()-started)/1000000.0, " seconds)")
	quit(0 if failures == 0 else 1)
