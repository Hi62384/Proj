extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func cfg() -> Dictionary:
	return {"revision":"stops-v1", "tick_unit":"simulation_tick", "stops":["origin","hub","end","x","y"],
		"vehicles":[{"id":"a","capacity":3},{"id":"b","capacity":2},{"id":"c","capacity":2},{"id":"d","capacity":1}],
		"services":[
			{"id":"a","vehicle":"a","from":"origin","to":"hub","period":4,"offset":0,"duration":2,"enabled":true},
			{"id":"b","vehicle":"b","from":"hub","to":"end","period":5,"offset":3,"duration":2,"enabled":true},
			{"id":"c","vehicle":"c","from":"hub","to":"end","period":7,"offset":4,"duration":3,"enabled":true},
			{"id":"d","vehicle":"d","from":"x","to":"y","period":4,"offset":0,"duration":3,"enabled":true}]}
func events_of(events: Array, kind: String) -> Array:
	return events.filter(func(e): return e.type == kind)
func tick_all(core) -> void:
	check(core.begin_tick(), "begin")
	for event in events_of(core.drain_events(),"alighting_requested"):
		check(core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id), "alight")
	core.drain_events()
	check(core.open_boarding(), "open")
	for event in events_of(core.drain_events(),"boarding_requested"):
		check(core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id), "board")
	core.drain_events()
	check(core.finish_tick(), "finish")
	core.drain_events()
func _initialize() -> void:
	var config := cfg()
	var core = Core.create(config,"stops").coordinator
	for i in range(3):
		check(core.request_journey("npc%02d" % i,"origin","end").ok, "request traveler")
	check(core.request_journey("bystander","x","y").ok, "request unaffected")
	core.drain_events()
	for i in range(3):
		tick_all(core)
	check(core.journey("npc00").stop == "hub" and core.journey("npc00").state == "queued", "waiting at transfer")
	check(core.journey("bystander").state == "onboard", "independent rider in transit")
	check(core.set_stop_enabled("hub",false), "disable transfer stop")
	check(core.journey("npc00").state == "failed" and core.diagnose("npc00").reason == "stop_inaccessible", "explicit inaccessible stop reason")
	check(core.journey("bystander").state == "onboard", "independent rider preserved")
	check(core.request_journey("new","hub","end").error == "stop_inaccessible", "new request to closed stop rejected")
	var restored = Core.restore(config,core.snapshot())
	check(restored.ok, "closed stop snapshot restores")
	core.drain_events()
	tick_all(core)
	check(core.journey("bystander").state == "completed", "independent rider completes")
	var stranded = Core.create(config,"stranded").coordinator
	check(stranded.request_journey("rider","origin","end").ok, "stranded setup")
	stranded.drain_events()
	tick_all(stranded)
	check(stranded.set_stop_enabled("hub",false), "close destination during ride")
	var recovery = events_of(stranded.drain_events(),"recovery_requested")
	check(recovery.size() == 1 and recovery[0].details.safe_stops == ["origin"], "safe endpoint excludes closed stop")
	check(not stranded.acknowledge_recovery("rider","a",recovery[0].details.token,recovery[0].id,"hub"), "closed recovery stop rejected")
	check(stranded.set_stop_enabled("hub",true), "reopen stop")
	var newer = events_of(stranded.drain_events(),"recovery_requested")
	check(newer.size() == 1 and newer[0].id != recovery[0].id, "recovery request refreshed")
	check(not stranded.acknowledge_recovery("rider","a",recovery[0].details.token,recovery[0].id,"origin"), "superseded recovery rejected")
	check(stranded.acknowledge_recovery("rider","a",newer[0].details.token,newer[0].id,"origin"), "valid recovery accepted")
	check(stranded.journey("rider").state == "queued", "recovered journey replans")
	var flags = Core.create(config,"flags").coordinator
	check(flags.set_stop_enabled("hub",false) and flags.set_service_enabled("b",false), "disable service while stop closed")
	check(flags.set_stop_enabled("hub",true), "reopen stop without re-enabling service")
	var saved = flags.snapshot()
	check(not saved.service_enabled.b and saved.stop_enabled.hub, "explicit availability retained")
	check(Core.restore(config,saved).ok, "availability state restores")
	print("Stop availability and recovery: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
