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
	var c = Candidate.new(Planner, 20, true)
	var d = DIY.new(DIYPlanner, 20, true)
	for t in range(4):
		c.step()
		d.step()
	check(c.passengers.npc02.service == "c" and d.passengers.npc02.service == "c", "both replan missed departure")
	check(c.trace == d.trace and c.passengers == d.passengers, "matching early state")
	var file = FileAccess.open("user://capacity-independent.dat", FileAccess.WRITE)
	file.store_var({"candidate":c.snapshot(), "diy":d.snapshot()})
	file.close()
	file = FileAccess.open("user://capacity-independent.dat", FileAccess.READ)
	var data: Dictionary = file.get_var()
	file.close()
	var old_candidate = data.candidate.duplicate(true)
	var old_diy = data.diy.duplicate(true)
	old_candidate.version = 2
	old_diy.version = 1
	check(Candidate.restore(old_candidate, Planner) == null and DIY.restore(old_diy, DIYPlanner) == null, "unsupported snapshot versions rejected")
	var cr = Candidate.restore(data.candidate, Planner)
	var dr = DIY.restore(data.diy, DIYPlanner)
	check(cr != null and dr != null, "both restore")
	if cr == null or dr == null:
		quit(1)
		return
	for t in range(150):
		cr.step()
		dr.step()
	check(cr.trace == dr.trace and cr.passengers == dr.passengers, "same full trace and outcomes")
	var arrival := -1
	for event in cr.trace:
		if event.size() >= 3 and event[1] == "completed" and event[2] == "npc02":
			arrival = event[0]
	check(arrival == 7, "both arrive at tick 7")
	for p in cr.passengers.values():
		check(p.state == "completed", "all completed")
	# Both onward services depart at tick 3; replan is deferred until both are closed.
	var simultaneous_c = Candidate.new(Planner, 20, true)
	var simultaneous_d = DIY.new(DIYPlanner, 20, true)
	for model in [simultaneous_c, simultaneous_d]:
		model.services[1].period = 10
		model.services[2].period = 5
		model.services[2].offset = 3
		for t in range(4):
			model.step()
		check(model.passengers.npc02.state == "waiting" and model.passengers.npc02.service == "c", "simultaneous departure is not boarded retroactively")
	check(simultaneous_c.trace == simultaneous_d.trace, "same simultaneous-departure trace")
	print("Capacity replan comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; npc02 arrival ", arrival, ")")
	quit(0 if failures == 0 else 1)
