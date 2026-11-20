extends SceneTree
const Planner = preload("res://route_planner.gd")
const Fixture = preload("res://automatic_reroute_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var a = Fixture.new(Planner, 20, true, true)
	for i in range(4):
		a.step()
	check(a.passengers.npc02.state == "waiting" and a.passengers.npc02.service == "c", "forecast selects C in simple case")
	var saved = a.snapshot()
	var b = Fixture.restore(saved, Planner)
	check(b != null and b.forecast_replan, "forecast mode restored")
	if b == null:
		quit(1)
		return
	for i in range(150):
		a.step()
		b.step()
	check(a.snapshot() == b.snapshot(), "identical forecast replay")
	for p in a.passengers.values():
		check(p.state == "completed", "all completed")
	print("Queue forecast fixed fixture: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
