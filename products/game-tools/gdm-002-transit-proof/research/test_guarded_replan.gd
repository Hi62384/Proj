extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func arrivals(model) -> Dictionary:
	var result := {}
	for event in model.trace:
		if event.size() >= 3 and event[1] == "completed":
			result[event[2]] = event[0]
	return result
func configure(model) -> void:
	for item in [[1,7,3,4,3], [2,6,1,5,2]]:
		var service: Dictionary = model.services[item[0]]
		service.period = item[1]
		service.offset = item[2]
		service.duration = item[3]
		service.capacity = item[4]
		model.ledgers[service.id].capacity = item[4]
func run_pair(altered: bool) -> void:
	var stay = Fixture.new(Planner,20,false,false,false)
	var guarded = Fixture.new(Planner,20,true,false,true)
	if altered:
		configure(stay)
		configure(guarded)
	for t in range(150):
		stay.step()
		guarded.step()
	var base = arrivals(stay)
	var chosen = arrivals(guarded)
	check(base.size() == 20 and chosen.size() == 20, "all complete")
	for id in base:
		check(chosen[id] <= base[id], "no later passenger in static trial " + id)
	if altered:
		check(base.npc08 == 14 and chosen.npc08 <= 14, "known counterexample avoided")
	print("guarded scenario ", "altered" if altered else "default", ": stay npc02=", base.npc02, " guarded npc02=", chosen.npc02, "; stay npc08=", base.npc08, " guarded npc08=", chosen.npc08)
func _initialize() -> void:
	run_pair(false)
	run_pair(true)
	var f = Fixture.new(Planner,20,true,false,true)
	for i in range(4):
		f.step()
	var restored = Fixture.restore(f.snapshot(),Planner)
	check(restored != null and restored.guarded_replan, "guarded mode restores")
	if restored != null:
		for i in range(100):
			f.step()
			restored.step()
		check(f.snapshot() == restored.snapshot(), "guarded snapshot replay")
	print("Guarded replan hypothesis: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
