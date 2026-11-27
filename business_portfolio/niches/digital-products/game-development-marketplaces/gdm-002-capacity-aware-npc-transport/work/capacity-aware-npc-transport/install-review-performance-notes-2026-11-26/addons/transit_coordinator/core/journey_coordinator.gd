extends RefCounted

# Single-owner, synchronous journey coordinator. External movement controllers
# acknowledge each boarding/alighting request; no scene nodes are stored here.
const Graph = preload("res://addons/transit_coordinator/core/transit_graph.gd")
const Ledger = preload("res://addons/transit_coordinator/core/seat_ledger.gd")
const MAX_JOURNEYS := 10000
var _graph
var _config: Dictionary
var _fingerprint := ""
var _run_id := ""
var _tick := 0
var _phase := "ready"
var _sequence := 0
var _events: Array = []
var _journeys := {}
var _ledgers := {}
var _services := {}
var _service_available := {}
var _stop_available := {}

static func create(config: Dictionary, run_id: String) -> Dictionary:
	if not Graph._valid_id(run_id):
		return {"ok": false, "error": "invalid_run_id"}
	var result := Graph.create(config)
	if not result.ok:
		return result
	var core = load("res://addons/transit_coordinator/core/journey_coordinator.gd").new()
	core._graph = result.graph
	core._config = result.graph.export_config()
	core._fingerprint = JSON.stringify(core._config, "", true).sha256_text()
	core._run_id = run_id
	for vehicle in core._config.vehicles:
		core._ledgers[vehicle.id] = Ledger.create(vehicle.capacity)
	for stop in core._config.stops:
		core._stop_available[stop] = true
	for service in core._config.services:
		core._services[service.id] = service
		core._service_available[service.id] = service.enabled
	return {"ok": true, "coordinator": core}

func _emit(kind: String, agent: String, details := {}) -> String:
	_sequence += 1
	var event_id := _run_id + "|" + str(_sequence)
	_events.append({"id": event_id, "tick": _tick, "type": kind, "agent": agent, "details": details.duplicate(true)})
	return event_id

func drain_events() -> Array:
	var result := _events.duplicate(true)
	_events.clear()
	return result

func journey(agent: String) -> Dictionary:
	return _journeys.get(agent, {}).duplicate(true)

func pending_request(agent: String) -> Dictionary:
	# Reconstruct an outstanding request after restore. The request ID and
	# token remain authoritative; tick is the current coordinator tick.
	if not _journeys.has(agent):
		return {}
	var p: Dictionary = _journeys[agent]
	var details := {"vehicle":p.vehicle,"service":p.service,"token":p.token}
	var kind := ""
	if p.state == "boarding":
		kind = "boarding_requested"
	elif p.state == "alighting":
		kind = "alighting_requested"
		details["stop"] = _services[p.service]["to"]
	elif p.state == "stranded":
		kind = "recovery_requested"
		details["safe_stops"] = _safe_stops(p.service)
	else:
		return {}
	return {"id":p.request_id,"tick":_tick,"type":kind,"agent":agent,"details":details}

func tick() -> int:
	return _tick

func request_journey(agent: String, origin: String, destination: String) -> Dictionary:
	if _phase != "ready":
		return {"ok": false, "error": "wrong_phase"}
	if not Ledger._valid_agent(agent) or (_journeys.size() >= MAX_JOURNEYS and not _journeys.has(agent)):
		return {"ok": false, "error": "invalid_agent_or_limit"}
	if _journeys.has(agent) and _journeys[agent].state not in ["completed", "cancelled", "failed"]:
		return {"ok": false, "error": "journey_exists"}
	if not _stop_available.get(origin, false) or not _stop_available.get(destination, false):
		return {"ok": false, "error": "stop_inaccessible"}
	var route = _graph.plan(origin, destination, _tick)
	if not route.ok:
		return route
	_journeys[agent] = {"state":"routing", "stop":origin, "destination":destination, "service":"", "vehicle":"", "token":0, "due":-1, "request_id":"", "reason":""}
	_emit("journey_requested", agent, {"origin": origin, "destination": destination})
	_queue_next(agent)
	return {"ok": true}

func _queue_next(agent: String) -> void:
	var p: Dictionary = _journeys[agent]
	if p.stop == p.destination:
		p.state = "completed"
		p.reason = "completed"
		p.service = ""
		p.vehicle = ""
		p.token = 0
		p.due = -1
		p.request_id = ""
		_emit("journey_completed", agent)
		return
	if not _stop_available[p.stop] or not _stop_available[p.destination]:
		_fail_journey(agent, "stop_inaccessible")
		return
	var route = _graph.plan(p.stop, p.destination, _tick)
	if not route.ok or route.legs.is_empty():
		_fail_journey(agent, "no_route")
		return
	var leg: Dictionary = route.legs[0]
	if not _ledgers[leg.vehicle].request(agent):
		_fail_journey(agent, "queue_rejected")
		return
	p.state = "queued"
	p.reason = "waiting_for_service"
	p.service = leg.service
	p.vehicle = leg.vehicle
	p.token = 0
	p.due = -1
	p.request_id = ""
	_emit("queued", agent, {"service": leg.service, "vehicle": leg.vehicle})

func inspect_vehicle(vehicle: String) -> Dictionary:
	if not _ledgers.has(vehicle):
		return {"ok":false,"reason":"unknown_vehicle"}
	return {"ok":true,"ledger":_ledgers[vehicle].snapshot()}

func diagnose(agent: String) -> Dictionary:
	if not _journeys.has(agent):
		return {"ok": false, "reason": "unknown_agent"}
	var p: Dictionary = _journeys[agent]
	return {"ok": true, "state": p.state, "reason": p.reason, "stop": p.stop, "service": p.service, "vehicle": p.vehicle, "due": p.due}

func _fail_journey(agent: String, reason: String) -> void:
	var p: Dictionary = _journeys[agent]
	p.state = "failed"
	p.reason = reason
	p.service = ""
	p.vehicle = ""
	p.token = 0
	p.due = -1
	p.request_id = ""
	_emit("journey_failed", agent, {"reason": reason})

func _refresh_graph() -> bool:
	for service_id in _services:
		var service: Dictionary = _services[service_id]
		service.enabled = _service_available[service_id] and _stop_available[service["from"]] and _stop_available[service["to"]]
	var updated := Graph.create(_config)
	if not updated.ok:
		return false
	_graph = updated.graph
	return true

func _safe_stops(service_id: String) -> Array:
	var service: Dictionary = _services[service_id]
	var result: Array = []
	for stop in [service["from"], service["to"]]:
		if _stop_available[stop]:
			result.append(stop)
	return result

func _request_recovery(agent: String, cancel_requested := false) -> void:
	var p: Dictionary = _journeys[agent]
	cancel_requested = cancel_requested or p.reason == "waiting_for_cancel_recovery"
	p.state = "stranded"
	p.reason = "waiting_for_cancel_recovery" if cancel_requested else "waiting_for_recovery"
	p.due = -1
	p.request_id = _emit("recovery_requested", agent, {"vehicle": p.vehicle, "service": p.service, "token": p.token, "safe_stops": _safe_stops(p.service)})

func _reconcile_availability(previous: Dictionary) -> void:
	for agent in _journeys:
		var p: Dictionary = _journeys[agent]
		if p.state not in ["queued", "onboard", "alighting", "stranded"]:
			continue
		var service_id: String = p.service
		if p.state == "queued" and not _stop_available[p.stop]:
			if _ledgers[p.vehicle].cancel(agent):
				_fail_journey(agent, "stop_inaccessible")
		elif p.state == "queued" and previous[service_id] and not _services[service_id].enabled:
			if _ledgers[p.vehicle].cancel(agent):
				p.state = "routing"
				_emit("rerouting", agent, {"reason": "service_unavailable", "service": service_id})
				_queue_next(agent)
		elif p.state in ["onboard", "alighting"] and previous[service_id] and not _services[service_id].enabled:
			_request_recovery(agent)
		elif p.state == "stranded":
			# A new availability state supersedes any older safe-point request.
			_request_recovery(agent)

func set_service_enabled(service_id: String, enabled: bool) -> bool:
	if _phase != "ready" or not _services.has(service_id) or _service_available[service_id] == enabled:
		return false
	var previous := {}
	for id in _services:
		previous[id] = _services[id].enabled
	_service_available[service_id] = enabled
	if not _refresh_graph():
		_service_available[service_id] = not enabled
		_refresh_graph()
		return false
	_emit("service_enabled" if enabled else "service_disabled", "", {"service": service_id})
	_reconcile_availability(previous)
	return true

func set_stop_enabled(stop_id: String, enabled: bool) -> bool:
	if _phase != "ready" or not _stop_available.has(stop_id) or _stop_available[stop_id] == enabled:
		return false
	var previous := {}
	for id in _services:
		previous[id] = _services[id].enabled
	_stop_available[stop_id] = enabled
	if not _refresh_graph():
		_stop_available[stop_id] = not enabled
		_refresh_graph()
		return false
	_emit("stop_enabled" if enabled else "stop_disabled", "", {"stop": stop_id})
	_reconcile_availability(previous)
	return true

func acknowledge_recovery(agent: String, vehicle: String, token: int, request_id: String, safe_stop: String) -> bool:
	if _phase not in ["ready", "arrivals"] or not _journeys.has(agent):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state != "stranded" or p.vehicle != vehicle or p.token != token or p.request_id != request_id:
		return false
	var service: Dictionary = _services[p.service]
	if safe_stop not in [service["from"], service["to"]] or not _stop_available[safe_stop] or not _ledgers[vehicle].release(agent, token):
		return false
	var cancelled: bool = p.reason == "waiting_for_cancel_recovery"
	p.stop = safe_stop
	p.state = "routing"
	p.request_id = ""
	_emit("recovered", agent, {"vehicle": vehicle, "stop": safe_stop})
	if cancelled:
		_mark_cancelled(agent)
	else:
		_queue_next(agent)
	return true

func change_destination(agent: String, destination: String) -> bool:
	# Boarding windows are intentionally closed to destination changes; the
	# controller may cancel a claim or wait until the next ready phase.
	if _phase != "ready" or not _journeys.has(agent) or not _stop_available.get(destination, false):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state not in ["queued", "onboard", "alighting", "stranded"] or p.reason == "waiting_for_cancel_recovery" or p.destination == destination:
		return false
	if p.state == "queued":
		if not _ledgers[p.vehicle].cancel(agent):
			return false
		p.destination = destination
		p.state = "routing"
		_emit("destination_changed", agent, {"destination": destination})
		_queue_next(agent)
	else:
		p.destination = destination
		_emit("destination_changed", agent, {"destination": destination})
	return true

func cancel_journey(agent: String) -> bool:
	if not _journeys.has(agent):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state in ["onboard", "alighting", "stranded"] and _phase in ["ready", "arrivals"]:
		if p.reason == "waiting_for_cancel_recovery":
			return false
		_request_recovery(agent,true)
		return true
	if p.state not in ["queued", "boarding"] or not _ledgers[p.vehicle].cancel(agent):
		return false
	_mark_cancelled(agent)
	return true

func remove_destroyed_agent(agent: String) -> bool:
	# Explicit game assertion: the physical agent is gone, so recovery cannot
	# occur. This is not a substitute for safe passenger cancellation.
	if not _journeys.has(agent):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state in ["queued", "boarding"]:
		if not _ledgers[p.vehicle].cancel(agent):
			return false
	elif p.state in ["boarding_confirmed", "onboard", "alighting", "stranded"]:
		if not _ledgers[p.vehicle].release(agent,p.token):
			return false
	else:
		return false
	_emit("agent_removed",agent,{"reason":"physical_agent_destroyed"})
	_mark_cancelled(agent)
	return true

func _mark_cancelled(agent: String) -> void:
	var p: Dictionary = _journeys[agent]
	p.state = "cancelled"
	p.reason = "cancelled"
	p.service = ""
	p.vehicle = ""
	p.token = 0
	p.due = -1
	p.request_id = ""
	_emit("journey_cancelled", agent)

func begin_tick() -> bool:
	if _phase != "ready" or _tick > Graph.MAX_TICK:
		return false
	_phase = "arrivals"
	for agent in _journeys:
		var p: Dictionary = _journeys[agent]
		if (p.state == "onboard" or p.state == "alighting") and p.due <= _tick:
			p.state = "alighting"
			p.reason = "waiting_for_alighting_ack"
			p.request_id = _emit("alighting_requested", agent, {"vehicle": p.vehicle, "service": p.service, "token": p.token, "stop": _services[p.service]["to"]})
	return true

func acknowledge_alighting(agent: String, vehicle: String, token: int, request_id: String) -> bool:
	if _phase != "arrivals" or not _journeys.has(agent):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state != "alighting" or p.vehicle != vehicle or p.token != token or p.request_id != request_id:
		return false
	if not _ledgers[vehicle].release(agent, token):
		return false
	p.stop = _services[p.service]["to"]
	p.state = "routing"
	p.request_id = ""
	_emit("alighted", agent, {"vehicle": vehicle, "stop": p.stop})
	_queue_next(agent)
	return true

func open_boarding() -> bool:
	if _phase != "arrivals":
		return false
	_phase = "boarding"
	for service in _config.services:
		if not service.enabled or _tick < service.offset or (_tick - service.offset) % service.period != 0:
			continue
		var ledger = _ledgers[service.vehicle]
		var eligible: Array = []
		for agent in _journeys:
			var p: Dictionary = _journeys[agent]
			if p.state == "queued" and p.service == service.id:
				eligible.append(agent)
		if eligible.is_empty():
			continue
		if _tick + service.duration > Graph.MAX_TICK:
			for agent in eligible:
				if ledger.cancel(agent):
					_fail_journey(agent, "schedule_horizon")
			continue
		if not ledger.snapshot().aboard.is_empty():
			_emit("departure_blocked", "", {"service": service.id, "reason": "vehicle_occupied"})
			continue
		for claim in ledger.allocate_matching(eligible):
			var p: Dictionary = _journeys[claim.agent]
			p.state = "boarding"
			p.reason = "waiting_for_boarding_ack"
			p.token = claim.token
			p.request_id = _emit("boarding_requested", claim.agent, {"vehicle": service.vehicle, "service": service.id, "token": claim.token})
	return true

func acknowledge_boarding(agent: String, vehicle: String, token: int, request_id: String) -> bool:
	if _phase != "boarding" or not _journeys.has(agent):
		return false
	var p: Dictionary = _journeys[agent]
	if p.state != "boarding" or p.vehicle != vehicle or p.token != token or p.request_id != request_id:
		return false
	if not _ledgers[vehicle].board(agent, token):
		return false
	p.state = "boarding_confirmed"
	p.reason = "waiting_for_departure"
	_emit("boarded", agent, {"vehicle": vehicle, "service": p.service, "token": token})
	return true

func finish_tick() -> bool:
	if _phase != "boarding":
		return false
	for agent in _journeys:
		var p: Dictionary = _journeys[agent]
		if p.state == "boarding_confirmed":
			p.state = "onboard"
			p.reason = "in_transit"
			p.due = _tick + _services[p.service].duration
			p.request_id = ""
			_emit("departed", agent, {"vehicle": p.vehicle, "service": p.service, "arrival_tick": p.due})
	for vehicle in _ledgers:
		for claim in _ledgers[vehicle].expire_claims():
			var p: Dictionary = _journeys[claim.agent]
			p.state = "queued"
			p.reason = "missed_departure"
			p.token = 0
			p.request_id = ""
			_emit("boarding_missed", claim.agent, {"vehicle": vehicle, "service": p.service})
	_tick += 1
	_phase = "ready"
	return true

func snapshot() -> Dictionary:
	var ledgers := {}
	for vehicle in _ledgers:
		ledgers[vehicle] = _ledgers[vehicle].snapshot()
	return {"version":5, "graph_fingerprint":_fingerprint, "service_enabled":_service_available.duplicate(), "stop_enabled":_stop_available.duplicate(), "run_id":_run_id, "tick":_tick, "phase":_phase, "sequence":_sequence, "journeys":_journeys.duplicate(true), "ledgers":ledgers, "events":_events.duplicate(true)}

static func _event_number(event_id: String, run_id: String) -> int:
	var prefix := run_id + "|"
	if not event_id.begins_with(prefix):
		return -1
	var suffix := event_id.substr(prefix.length())
	if not suffix.is_valid_int():
		return -1
	var value := int(suffix)
	if value < 1 or str(value) != suffix:
		return -1
	return value

static func restore(config: Dictionary, data: Dictionary) -> Dictionary:
	# Version 4 has the same shape but predates cancellation recovery.
	# Upgrade a copy, then apply the full version-5 validation below.
	if data.get("version") == 4:
		if not data.get("journeys") is Dictionary:
			return {"ok":false,"error":"invalid_snapshot"}
		for journey in data.journeys.values():
			if not journey is Dictionary or journey.get("reason") == "waiting_for_cancel_recovery":
				return {"ok":false,"error":"invalid_snapshot"}
		data = data.duplicate(true)
		data.version = 5
	if data.get("version") != 5 or not data.get("run_id") is String or not data.get("tick") is int or not data.get("sequence") is int or not data.get("phase") is String:
		return {"ok": false, "error": "invalid_snapshot"}
	if data.tick < 0 or data.tick > Graph.MAX_TICK + 1 or data.sequence < 0 or data.phase not in ["ready", "arrivals", "boarding"]:
		return {"ok": false, "error": "invalid_snapshot"}
	for field in ["journeys", "ledgers"]:
		if not data.get(field) is Dictionary:
			return {"ok": false, "error": "invalid_snapshot"}
	if not data.get("events") is Array or data.journeys.size() > MAX_JOURNEYS:
		return {"ok": false, "error": "invalid_snapshot"}
	var created := create(config, data.run_id)
	if not created.ok:
		return created
	var core = created.coordinator
	if data.get("graph_fingerprint") != core._fingerprint:
		return {"ok": false, "error": "graph_mismatch"}
	if not data.get("service_enabled") is Dictionary or data.service_enabled.size() != core._services.size() or not data.get("stop_enabled") is Dictionary or data.stop_enabled.size() != core._stop_available.size():
		return {"ok": false, "error": "invalid_snapshot"}
	for service_id in core._services:
		if not data.service_enabled.has(service_id) or not data.service_enabled[service_id] is bool:
			return {"ok": false, "error": "invalid_snapshot"}
		core._service_available[service_id] = data.service_enabled[service_id]
	for stop_id in core._stop_available:
		if not data.stop_enabled.has(stop_id) or not data.stop_enabled[stop_id] is bool:
			return {"ok": false, "error": "invalid_snapshot"}
		core._stop_available[stop_id] = data.stop_enabled[stop_id]
	if not core._refresh_graph():
		return {"ok": false, "error": "invalid_snapshot"}
	if data.ledgers.size() != core._ledgers.size():
		return {"ok": false, "error": "invalid_snapshot"}
	var owners := {}
	for vehicle in core._ledgers:
		if not data.ledgers.has(vehicle) or not data.ledgers[vehicle] is Dictionary:
			return {"ok": false, "error": "invalid_snapshot"}
		var ledger = Ledger.restore(data.ledgers[vehicle])
		if ledger == null or ledger.snapshot().capacity != core._ledgers[vehicle].snapshot().capacity:
			return {"ok": false, "error": "invalid_snapshot"}
		core._ledgers[vehicle] = ledger
		var state = ledger.snapshot()
		for id in state.waiting:
			if owners.has(id):
				return {"ok": false, "error": "invalid_snapshot"}
			owners[id] = {"vehicle":vehicle, "kind":"waiting", "token":0}
		for group in ["claims", "aboard"]:
			for entry in state[group]:
				if owners.has(entry.agent):
					return {"ok": false, "error": "invalid_snapshot"}
				owners[entry.agent] = {"vehicle":vehicle, "kind":group, "token":entry.token}
	var active_requests := {}
	for agent in data.journeys:
		var p = data.journeys[agent]
		if not Ledger._valid_agent(agent) or not p is Dictionary:
			return {"ok": false, "error": "invalid_snapshot"}
		for field in ["state", "stop", "destination", "service", "vehicle", "request_id", "reason"]:
			if not p.get(field) is String:
				return {"ok": false, "error": "invalid_snapshot"}
		if not p.get("token") is int or not p.get("due") is int or not core._config.stops.has(p.stop) or not core._config.stops.has(p.destination):
			return {"ok": false, "error": "invalid_snapshot"}
		var allowed_reasons = {"queued":["waiting_for_service", "missed_departure"], "boarding":["waiting_for_boarding_ack"], "boarding_confirmed":["waiting_for_departure"], "onboard":["in_transit"], "alighting":["waiting_for_alighting_ack"], "stranded":["waiting_for_recovery", "waiting_for_cancel_recovery"], "completed":["completed"], "cancelled":["cancelled"], "failed":["no_route", "stop_inaccessible", "queue_rejected", "schedule_horizon"]}
		if not allowed_reasons.has(p.state) or not allowed_reasons[p.state].has(p.reason):
			return {"ok": false, "error": "invalid_snapshot"}
		if p.state in ["completed", "cancelled", "failed"]:
			if owners.has(agent) or p.service != "" or p.vehicle != "" or p.token != 0 or p.due != -1 or p.request_id != "" or (p.state == "completed" and p.stop != p.destination):
				return {"ok": false, "error": "invalid_snapshot"}
			continue
		if p.state not in ["queued", "boarding", "boarding_confirmed", "onboard", "alighting", "stranded"] or not owners.has(agent) or not core._services.has(p.service):
			return {"ok": false, "error": "invalid_snapshot"}
		var service: Dictionary = core._services[p.service]
		var owner: Dictionary = owners[agent]
		if p.vehicle != service.vehicle or p.stop != service["from"] or owner.vehicle != p.vehicle or (not service.enabled and p.state != "stranded"):
			return {"ok": false, "error": "invalid_snapshot"}
		if p.state == "queued":
			if owner.kind != "waiting" or p.token != 0 or p.due != -1 or p.request_id != "":
				return {"ok": false, "error": "invalid_snapshot"}
		else:
			var expected_kind := "claims" if p.state == "boarding" else "aboard"
			if owner.kind != expected_kind or owner.token != p.token or p.token < 1:
				return {"ok": false, "error": "invalid_snapshot"}
			if p.state in ["boarding", "boarding_confirmed"]:
				if data.phase != "boarding" or p.due != -1 or data.tick < service.offset or (data.tick - service.offset) % service.period != 0:
					return {"ok": false, "error": "invalid_snapshot"}
			elif p.state == "onboard":
				if p.due < data.tick or p.request_id != "":
					return {"ok": false, "error": "invalid_snapshot"}
			elif p.state == "alighting" and p.due > data.tick:
				return {"ok": false, "error": "invalid_snapshot"}
			elif p.state == "stranded" and p.due != -1:
				return {"ok": false, "error": "invalid_snapshot"}
			if p.state in ["boarding", "boarding_confirmed", "alighting", "stranded"]:
				var request_number := _event_number(p.request_id, data.run_id)
				if request_number < 1 or request_number > data.sequence or active_requests.has(p.request_id):
					return {"ok": false, "error": "invalid_snapshot"}
				active_requests[p.request_id] = true
			if p.state in ["onboard", "alighting"]:
				var departure: int = p.due - service.duration
				if departure < service.offset or (departure - service.offset) % service.period != 0:
					return {"ok": false, "error": "invalid_snapshot"}
	for agent in owners:
		if not data.journeys.has(agent):
			return {"ok": false, "error": "invalid_snapshot"}
	var previous := 0
	for event in data.events:
		if not event is Dictionary or not event.get("id") is String or not event.get("tick") is int or not event.get("type") is String or not event.get("agent") is String or not event.get("details") is Dictionary:
			return {"ok": false, "error": "invalid_snapshot"}
		var number := _event_number(event.id, data.run_id)
		if number <= previous or number > data.sequence or event.tick < 0 or event.tick > data.tick:
			return {"ok": false, "error": "invalid_snapshot"}
		previous = number
	core._tick = data.tick
	core._phase = data.phase
	core._sequence = data.sequence
	core._journeys = data.journeys.duplicate(true)
	core._events = data.events.duplicate(true)
	return {"ok": true, "coordinator": core}
