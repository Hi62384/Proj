extends SceneTree
const Audit = preload("res://addons/transit_coordinator/core/continuity_audit.gd")
const Demo = preload("res://demo/transit_demo.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	var cfg := {"revision":"continuity-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":2}],"services":[{"id":"out","vehicle":"v","from":"a","to":"b","period":4,"offset":0,"duration":2,"enabled":true}]}
	var good: Dictionary = Audit.audit(cfg,{"b":{"a":2}},16)
	check(good.ok and good.feasible and good.events_checked == 4,"exact time to return")
	var bad: Dictionary = Audit.audit(cfg,{"b":{"a":3}},16)
	check(bad.ok and not bad.feasible and bad.conflicts.size() == 3,"late return flagged")
	check(bad.conflicts[0].previous_arrival == 2 and bad.conflicts[0].next_departure == 4,"correct conflicting ticks")
	check(Audit.audit(cfg,{},16).error == "missing_or_invalid_reposition_time","unknown return time not assumed")
	check(not Audit.audit(cfg,{"b":{"a":-1}},16).ok,"negative return rejected")
	check(not Audit.audit(cfg,{"b":{"a":2}},0).ok,"invalid horizon rejected")
	var disabled := cfg.duplicate(true)
	disabled.services[0].enabled = false
	var none: Dictionary = Audit.audit(disabled,{},16)
	check(none.ok and none.events_checked == 0 and none.feasible,"disabled service excluded")
	var demo = Demo.new()
	var demo_result: Dictionary = Audit.audit(demo.config(),{"hub":{"origin":1},"end":{"hub":1}},120)
	check(demo_result.ok and demo_result.feasible,"demo schedule with explicit empty return times")
	demo.free()
	print("Vehicle continuity audit: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	quit(0 if failures == 0 else 1)
