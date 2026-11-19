extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
const Graph = preload("res://addons/transit_coordinator/core/transit_graph.gd")
const Ledger = preload("res://addons/transit_coordinator/core/seat_ledger.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func bidirectional() -> Dictionary:
	return {"revision":"edge-v1", "tick_unit":"simulation_tick", "stops":["a","b"],
		"vehicles":[{"id":"lift","capacity":1}],
		"services":[
			{"id":"up","vehicle":"lift","from":"a","to":"b","period":4,"offset":0,"duration":1,"enabled":true},
			{"id":"down","vehicle":"lift","from":"b","to":"a","period":4,"offset":2,"duration":1,"enabled":true}]}
func requests(events: Array, kind: String) -> Array:
	return events.filter(func(e): return e.type == kind)
func _initialize() -> void:
	var ledger = Ledger.create(1)
	check(ledger.request("other-stop") and ledger.request("eligible"), "queue two stops")
	var claims = ledger.allocate_matching(["eligible"])
	check(claims.size() == 1 and claims[0].agent == "eligible", "FIFO among eligible passengers")
	check(ledger.snapshot().waiting == ["other-stop"], "ineligible remains queued")
	var config := bidirectional()
	check(Graph.validate(config).is_empty(), "same vehicle non-overlapping service valid")
	var invalid := config.duplicate(true)
	invalid.services[1].offset = 0
	check(Graph.validate(invalid) == "vehicle_schedule_overlap", "same vehicle overlap rejected")
	invalid = config.duplicate(true)
	invalid.unexpected = "ignored?"
	check(Graph.validate(invalid) == "invalid_fields", "unknown configuration field rejected")
	var core = Core.create(config,"late").coordinator
	check(core.request_journey("up-rider","a","b").ok, "up request")
	check(core.request_journey("down-rider","b","a").ok, "down request")
	core.drain_events()
	check(core.begin_tick() and core.open_boarding(), "tick zero window")
	var first: Array = requests(core.drain_events(),"boarding_requested")
	check(first.size() == 1 and first[0].agent == "up-rider", "correct service boarded first")
	check(core.acknowledge_boarding(first[0].agent,first[0].details.vehicle,first[0].details.token,first[0].id), "board up")
	core.drain_events()
	check(core.finish_tick(), "depart")
	core.drain_events()
	check(core.begin_tick(), "arrival tick")
	var late_requests: Array = requests(core.drain_events(),"alighting_requested")
	check(late_requests.size() == 1, "alighting requested")
	var old = core.snapshot()
	old.version = 4
	var migrated = Core.restore(config,old)
	check(migrated.ok and migrated.coordinator.pending_request("up-rider") == late_requests[0], "migrate pending alighting")
	check(core.open_boarding() and core.finish_tick(), "defer alighting")
	core.drain_events()
	check(core.begin_tick(), "next tick")
	var current: Array = requests(core.drain_events(),"alighting_requested")
	check(current.size() == 1 and current[0].id != late_requests[0].id, "fresh alighting request")
	check(not core.acknowledge_alighting("up-rider","lift",current[0].details.token,late_requests[0].id), "stale alighting rejected")
	check(core.open_boarding(), "down window")
	var blocked = requests(core.drain_events(),"departure_blocked")
	check(blocked.size() == 1 and blocked[0].details.reason == "vehicle_occupied", "occupied vehicle departure blocked")
	check(core.finish_tick(), "close blocked window")
	core.drain_events()
	check(core.begin_tick(), "retry alighting")
	current = requests(core.drain_events(),"alighting_requested")
	check(core.acknowledge_alighting("up-rider","lift",current[0].details.token,current[0].id), "eventual alighting")
	check(core.journey("up-rider").state == "completed", "arrived")
	check(core.open_boarding() and core.finish_tick(), "advance after alight")
	core.drain_events()
	check(core.begin_tick() and core.open_boarding() and core.finish_tick(), "tick four")
	core.drain_events()
	check(core.begin_tick() and core.open_boarding() and core.finish_tick(), "tick five")
	core.drain_events()
	check(core.begin_tick() and core.open_boarding(), "next down service")
	var down = requests(core.drain_events(),"boarding_requested")
	check(down.size() == 1 and down[0].agent == "down-rider", "waiting agent recovers next service")
	var change = Core.create(config,"change").coordinator
	check(change.request_journey("one","a","b").ok, "change setup")
	check(change.change_destination("one","a"), "change to current stop")
	check(change.journey("one").state == "completed", "no seat leaked at current destination")
	check(change.request_journey("one","a","b").ok, "new journey after completion")
	check(not change.change_destination("one","missing"), "unknown destination rejected")
	check(change.journey("one").state == "queued", "invalid change leaves original journey")
	var horizon = {"revision":"limit", "tick_unit":"simulation_tick", "stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":1,"offset":0,"duration":1,"enabled":true}]}
	var base = Core.create(horizon,"horizon").coordinator
	var snap = base.snapshot()
	snap.tick = Graph.MAX_TICK - 1
	var restored = Core.restore(horizon,snap)
	check(restored.ok, "near-horizon snapshot")
	if restored.ok:
		var h = restored.coordinator
		check(h.request_journey("a1","a","b").ok and h.request_journey("a2","a","b").ok, "horizon requests")
		h.drain_events()
		check(h.begin_tick() and h.open_boarding(), "last viable departure")
		var first_h = requests(h.drain_events(),"boarding_requested")[0]
		check(h.acknowledge_boarding(first_h.agent,"v",first_h.details.token,first_h.id) and h.finish_tick(), "first departure")
		h.drain_events()
		check(h.begin_tick(), "last arrival")
		var arrival_h = requests(h.drain_events(),"alighting_requested")[0]
		check(h.acknowledge_alighting(arrival_h.agent,"v",arrival_h.details.token,arrival_h.id), "last alight")
		h.drain_events()
		check(h.open_boarding(), "horizon handling")
		check(h.journey("a2").state == "failed", "unserviceable waiter fails explicitly")
	print("Transit lifecycle edge cases: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
