extends SceneTree
const Coordinator = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func cfg() -> Dictionary:
	return {"revision":"disrupt-v1", "tick_unit":"simulation_tick", "stops":["origin","hub","end"],
	"vehicles":[{"id":"a","capacity":3},{"id":"b","capacity":2},{"id":"c","capacity":2}],
	"services":[
		{"id":"a","vehicle":"a","from":"origin","to":"hub","period":4,"offset":0,"duration":2,"enabled":true},
		{"id":"b","vehicle":"b","from":"hub","to":"end","period":5,"offset":3,"duration":2,"enabled":true},
		{"id":"c","vehicle":"c","from":"hub","to":"end","period":7,"offset":4,"duration":3,"enabled":true}]}
func requests(events: Array, kind: String) -> Array:
	return events.filter(func(e): return e.type == kind)
func tick_all(core) -> void:
	check(core.begin_tick(), "begin")
	var arrival = core.drain_events()
	for e in requests(arrival,"alighting_requested"):
		check(core.acknowledge_alighting(e.agent,e.details.vehicle,e.details.token,e.id), "alight")
	core.drain_events()
	check(core.open_boarding(), "open")
	var boards = core.drain_events()
	for e in requests(boards,"boarding_requested"):
		check(core.acknowledge_boarding(e.agent,e.details.vehicle,e.details.token,e.id), "board")
	core.drain_events()
	check(core.finish_tick(), "finish")
	core.drain_events()
func _initialize() -> void:
	var config := cfg()
	var core = Coordinator.create(config,"disrupt").coordinator
	for i in range(20):
		check(core.request_journey("npc%02d" % i,"origin","end").ok, "request")
	core.drain_events()
	for t in range(4):
		tick_all(core)
	check(core.journey("npc00").state == "onboard" and core.journey("npc00").vehicle == "b", "two riders in transit")
	check(core.set_service_enabled("b",false), "disable service between ticks")
	var disruption: Array = core.drain_events()
	var rescues := requests(disruption,"recovery_requested")
	check(rescues.size() == 2, "recovery requested for both riders")
	check(core.journey("npc02").state == "queued" and core.journey("npc02").service == "c", "waiting rider reroutes")
	check(core.diagnose("npc00").reason == "waiting_for_recovery", "stranded diagnostic")
	check(not core.set_service_enabled("b",false), "duplicate disruption rejected")
	var state = core.snapshot()
	var restored_result = Coordinator.restore(config,state)
	check(restored_result.ok, "stranded state restores")
	if not restored_result.ok:
		quit(1)
		return
	var restored = restored_result.coordinator
	check(restored.snapshot() == state, "snapshot exact")
	var old = state.duplicate(true)
	old.version = 4
	var migrated = Coordinator.restore(config,old)
	check(migrated.ok and migrated.coordinator.snapshot() == state,"migrate stranded version 4")
	for e in rescues:
		check(restored.pending_request(e.agent) == e, "restore pending recovery request")
		check(not core.acknowledge_recovery(e.agent,e.details.vehicle,e.details.token,e.id,"origin"), "invalid safe stop rejected")
		check(not core.acknowledge_recovery(e.agent,e.details.vehicle,e.details.token,"wrong","hub"), "stale recovery rejected")
		check(core.acknowledge_recovery(e.agent,e.details.vehicle,e.details.token,e.id,"hub"), "recover")
		check(restored.acknowledge_recovery(e.agent,e.details.vehicle,e.details.token,e.id,"hub"), "recover after restore")
		check(not core.acknowledge_recovery(e.agent,e.details.vehicle,e.details.token,e.id,"hub"), "duplicate recovery rejected")
	check(core.drain_events() == restored.drain_events(), "matching recovery events")
	for t in range(150):
		tick_all(core)
		tick_all(restored)
		check(core.snapshot() == restored.snapshot(), "identical continuation")
	for i in range(20):
		check(core.journey("npc%02d" % i).state == "completed", "all complete after reroute")
	var reenable = Coordinator.create(config,"reenable").coordinator
	check(reenable.request_journey("one","origin","end").ok, "reenable setup")
	reenable.drain_events()
	for t in range(4):
		tick_all(reenable)
	check(reenable.set_service_enabled("b",false), "disable with rider")
	var pending = requests(reenable.drain_events(),"recovery_requested")
	check(pending.size() == 1 and reenable.set_service_enabled("b",true), "reenable while stranded")
	check(Coordinator.restore(config,reenable.snapshot()).ok, "reenabled stranded state restores")
	var bad = state.duplicate(true)
	bad.service_enabled.b = true
	check(Coordinator.restore(config,bad).ok, "stranded seat can remain occupied after reenable")
	bad = state.duplicate(true)
	bad.service_enabled.b = "false"
	check(not Coordinator.restore(config,bad).ok, "nonboolean service flag rejected")
	print("Disruption lifecycle: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 20 agents)")
	quit(0 if failures == 0 else 1)
