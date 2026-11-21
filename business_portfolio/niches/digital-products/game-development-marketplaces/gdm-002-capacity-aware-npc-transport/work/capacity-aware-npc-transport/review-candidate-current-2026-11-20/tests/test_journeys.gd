extends SceneTree
const Coordinator = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func config() -> Dictionary:
	return {"revision":"journey-v1", "tick_unit":"simulation_tick", "stops":["origin", "hub", "end"],
		"vehicles":[{"id":"a", "capacity":3}, {"id":"b", "capacity":2}],
		"services":[
			{"id":"a-out", "vehicle":"a", "from":"origin", "to":"hub", "period":4, "offset":0, "duration":2, "enabled":true},
			{"id":"b-out", "vehicle":"b", "from":"hub", "to":"end", "period":5, "offset":3, "duration":2, "enabled":true}]}
func requested(events: Array, kind: String) -> Array:
	return events.filter(func(e): return e.type == kind)
func drive_one(core) -> Array:
	var all := []
	check(core.begin_tick(), "begin tick")
	var arrivals: Array = core.drain_events()
	all.append_array(arrivals)
	for event in requested(arrivals, "alighting_requested"):
		check(core.acknowledge_alighting(event.agent, event.details.vehicle, event.details.token, event.id), "alighting ack")
		check(not core.acknowledge_alighting(event.agent, event.details.vehicle, event.details.token, event.id), "duplicate alighting rejected")
	all.append_array(core.drain_events())
	check(core.open_boarding(), "open boarding")
	var boards: Array = core.drain_events()
	all.append_array(boards)
	for event in requested(boards, "boarding_requested"):
		check(core.acknowledge_boarding(event.agent, event.details.vehicle, event.details.token, event.id), "boarding ack")
		check(not core.acknowledge_boarding(event.agent, event.details.vehicle, event.details.token, event.id), "duplicate boarding rejected")
	all.append_array(core.drain_events())
	check(core.finish_tick(), "finish tick")
	all.append_array(core.drain_events())
	return all
func _initialize() -> void:
	var cfg := config()
	var made = Coordinator.create(cfg,"run-1")
	check(made.ok, "coordinator creation")
	if not made.ok:
		quit(1)
		return
	var original = made.coordinator
	for i in range(20):
		check(original.request_journey("npc%02d" % i, "origin", "end").ok, "request")
	original.drain_events()
	check(original.begin_tick() and original.open_boarding(), "open initial boarding")
	var initial = original.drain_events()
	var board_requests := requested(initial,"boarding_requested")
	check(board_requests.size() == 3, "capacity limited to three")
	check(board_requests[0].agent == "npc00" and board_requests[1].agent == "npc01" and board_requests[2].agent == "npc02", "FIFO order")
	var saved = original.snapshot()
	var file = FileAccess.open("user://journey-midboarding.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://journey-midboarding.dat", FileAccess.READ)
	var restored_result = Coordinator.restore(cfg,file.get_var())
	file.close()
	check(restored_result.ok, "restore mid-boarding")
	if not restored_result.ok:
		quit(1)
		return
	var restored = restored_result.coordinator
	check(restored.snapshot() == saved, "snapshot exact round trip")
	var old = saved.duplicate(true)
	old.version = 4
	var migrated = Coordinator.restore(cfg,old)
	check(migrated.ok and migrated.coordinator.snapshot() == saved,"version 4 migrates to 5")
	check(old.version == 4,"migration leaves source unchanged")
	for event in board_requests:
		check(restored.pending_request(event.agent) == event, "restore pending boarding request")
		check(not restored.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,"wrong"), "wrong callback rejected")
		check(original.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id), "original board")
		check(restored.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id), "restored board")
		check(restored.pending_request(event.agent).is_empty(), "acknowledged request no longer pending")
		check(not restored.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id), "replayed board rejected")
	check(original.drain_events() == restored.drain_events(), "matching boarding events")
	check(original.finish_tick() and restored.finish_tick(), "first departure")
	check(original.drain_events() == restored.drain_events(), "matching departure events")
	for i in range(120):
		var before = drive_one(original)
		var after = drive_one(restored)
		check(before == after, "event trace replay tick %d" % original.tick())
		check(original.snapshot() == restored.snapshot(), "state replay tick %d" % original.tick())
	for i in range(20):
		check(original.journey("npc%02d" % i).state == "completed", "completed after transfer")
	var changed := cfg.duplicate(true)
	changed.services[0].duration = 3
	check(Coordinator.restore(changed,saved).error == "graph_mismatch", "changed graph rejected")
	var corrupt = saved.duplicate(true)
	corrupt.ledgers.a.waiting.append("npc00")
	check(not Coordinator.restore(cfg,corrupt).ok, "duplicate ownership rejected")
	corrupt = saved.duplicate(true)
	corrupt.journeys.npc00.token += 1
	check(not Coordinator.restore(cfg,corrupt).ok, "claim token mismatch rejected")
	corrupt = saved.duplicate(true)
	corrupt.phase = "ready"
	check(not Coordinator.restore(cfg,corrupt).ok, "boarding state outside boarding rejected")
	var expiry = Coordinator.create(cfg,"expiry").coordinator
	check(expiry.request_journey("one","origin","end").ok, "expiry request")
	expiry.drain_events()
	check(expiry.begin_tick() and expiry.open_boarding(), "expiry window")
	var expired = requested(expiry.drain_events(),"boarding_requested")[0]
	check(expiry.finish_tick(), "missed departure closes")
	check(not expiry.acknowledge_boarding("one","a",expired.details.token,expired.id), "late callback rejected")
	for t in range(3):
		drive_one(expiry)
	check(expiry.begin_tick() and expiry.open_boarding(), "next boarding window")
	var renewed = requested(expiry.drain_events(),"boarding_requested")[0]
	check(renewed.details.token != expired.details.token and renewed.id != expired.id, "fresh token and request ID")
	check(not expiry.acknowledge_boarding("one","a",expired.details.token,expired.id), "old callback rejected in new window")
	check(expiry.cancel_journey("one"), "cancel reserved")
	check(not expiry.acknowledge_boarding("one","a",renewed.details.token,renewed.id), "cancelled callback rejected")
	print("Journey lifecycle: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 20 agents; two services)")
	quit(0 if failures == 0 else 1)
