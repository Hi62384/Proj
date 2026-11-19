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
	var c = Candidate.new(Planner)
	var d = DIY.new(DIYPlanner)
	var cs = c.snapshot()
	var ds = d.snapshot()
	for key in ["duration", "period", "capacity", "offset"]:
		var a = cs.duplicate(true)
		var b = ds.duplicate(true)
		a.services[0][key] += 1
		b.services[0][key] += 1
		check(Candidate.restore(a, Planner) == null and DIY.restore(b, DIYPlanner) == null, "changed " + key + " rejected")
	var a = cs.duplicate(true)
	var b = ds.duplicate(true)
	a.services.reverse()
	b.services.reverse()
	check(Candidate.restore(a, Planner) == null and DIY.restore(b, DIYPlanner) == null, "reordered graph rejected")
	for i in range(4):
		c.step()
		d.step()
	check(c.disrupt_service("b") and d.disrupt_service("b"), "legitimate disruption")
	check(Candidate.restore(c.snapshot(), Planner) != null and DIY.restore(d.snapshot(), DIYPlanner) != null, "disabled state still restores")
	print("Graph revision validation: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
