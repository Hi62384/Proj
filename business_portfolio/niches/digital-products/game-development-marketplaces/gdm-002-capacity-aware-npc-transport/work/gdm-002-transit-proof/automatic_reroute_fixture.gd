extends RefCounted
# Bounded automatic-routing experiment, not a shipping coordinator.
const Ledger = preload("res://transit.gd")
const GraphValidation = preload("res://route_planner.gd")
var planner
var tick := 0
var capacity_replan := false
var forecast_replan := false
var guarded_replan := false
var baseline_evaluations := 0
var baseline_cache: Dictionary = {}
var baseline_cache_ready := false
var stops := ["origin", "hub", "end"]
var services := [
	{"id":"a", "from":"origin", "to":"hub", "period":4, "offset":0, "duration":2, "capacity":3, "enabled":true},
	{"id":"b", "from":"hub", "to":"end", "period":5, "offset":3, "duration":2, "capacity":2, "enabled":true},
	{"id":"c", "from":"hub", "to":"end", "period":7, "offset":4, "duration":3, "capacity":2, "enabled":true}
]
var passengers := {}
var ledgers := {}
var trace: Array = []

func _init(route_planner, count := 20, replan := false, forecast := false, guarded := false) -> void:
	planner = route_planner
	capacity_replan = replan or forecast or guarded
	forecast_replan = forecast and not guarded
	guarded_replan = guarded
	for s in services:
		ledgers[s.id] = Ledger.new(s.capacity)
	for i in range(count):
		var id := "npc%02d" % i
		passengers[id] = {"state":"routing", "stop":"origin", "service":"", "due":-1, "rescue_token":0}
		queue_next(id)

func queue_next(id: String, earliest_tick := -1) -> void:
	var p: Dictionary = passengers[id]
	if p.stop == "end":
		p.state = "completed"
		p.service = ""
		p.due = -1
		trace.append([tick, "completed", id])
		return
	var route = planner.plan(stops, services, p.stop, "end", tick if earliest_tick < 0 else earliest_tick)
	if not route.ok or route.legs.is_empty():
		p.state = "failed"
		p.service = ""
		p.due = -1
		trace.append([tick, "no_route", id])
		return
	var service: String = route.legs[0].service
	var accepted: bool = ledgers[service].request(id)
	assert(accepted)
	p.state = "waiting"
	p.service = service
	p.due = -1
	trace.append([tick, "queued", id, service])

func disable_waiting_service(service_id: String) -> bool:
	if not ledgers.has(service_id) or not ledgers[service_id].aboard.is_empty() or not ledgers[service_id].reserved.is_empty():
		return false
	var service: Dictionary = {}
	for s in services:
		if s.id == service_id:
			service = s
	if service.is_empty() or not service.enabled:
		return false
	service.enabled = false
	trace.append([tick, "disabled", service_id])
	for id in ledgers[service_id].waiting.duplicate():
		var cancelled: bool = ledgers[service_id].cancel(id)
		assert(cancelled)
		passengers[id].state = "routing"
		passengers[id].service = ""
		queue_next(id)
	return true

func disrupt_service(service_id: String) -> bool:
	if not ledgers.has(service_id) or not ledgers[service_id].reserved.is_empty():
		return false
	var service: Dictionary = {}
	for item in services:
		if item.id == service_id:
			service = item
	if service.is_empty() or not service.enabled:
		return false
	service.enabled = false
	trace.append([tick, "disrupted", service_id])
	for id in ledgers[service_id].aboard:
		passengers[id].state = "stranded"
		passengers[id].due = -1
		passengers[id].rescue_token += 1
		trace.append([tick, "stranded", id, service_id])
	for id in ledgers[service_id].waiting.duplicate():
		var cancelled: bool = ledgers[service_id].cancel(id)
		assert(cancelled)
		passengers[id].state = "routing"
		passengers[id].service = ""
		queue_next(id)
	return true

func acknowledge_rescue(id: String, token: int, safe_stop: String) -> bool:
	if not passengers.has(id):
		return false
	var p: Dictionary = passengers[id]
	if p.state != "stranded" or p.rescue_token != token:
		return false
	var service: Dictionary = {}
	for item in services:
		if item.id == p.service:
			service = item
	# This fixture supports only recovery to the service's origin stop.
	if service.is_empty() or safe_stop != service["from"]:
		return false
	if not ledgers[p.service].disembark(id):
		return false
	trace.append([tick, "rescued", id, p.service])
	p.stop = safe_stop
	p.state = "routing"
	p.service = ""
	queue_next(id)
	return true

func forecast_direct_arrival(id: String, service: Dictionary, earliest: int) -> int:
	# Fixed-graph experiment: forecast only currently known queues and onboard riders.
	var ledger = ledgers[service.id]
	var ahead: int = ledger.waiting.find(id)
	if ahead < 0:
		ahead = ledger.waiting.size()
	var releases: Array[int] = []
	for rider in ledger.aboard:
		if passengers[rider].due < 0:
			return GraphValidation.MAX_TICK + 1
		releases.append(passengers[rider].due)
	var depart: int = service.offset
	if depart < earliest:
		depart += ceili(float(earliest - depart) / float(service.period)) * service.period
	while depart <= GraphValidation.MAX_TICK:
		for due in releases.duplicate():
			if due <= depart:
				releases.erase(due)
		var free: int = maxi(0, service.capacity - releases.size())
		if ahead < free:
			return depart + service.duration
		var taken: int = mini(ahead, free)
		ahead -= taken
		for seat in range(taken):
			releases.append(depart + service.duration)
		depart += service.period
	return GraphValidation.MAX_TICK + 1

func choose_forecast_service(id: String, current_service: String, earliest: int) -> String:
	# Only direct hub-to-end services are comparable in this three-stop fixture.
	if passengers[id].stop != "hub":
		return current_service
	var best := current_service
	var best_arrival := GraphValidation.MAX_TICK + 1
	for service in services:
		if service.id == current_service and service.enabled:
			best_arrival = forecast_direct_arrival(id, service, earliest)
	for service in services:
		if not service.enabled or service["from"] != "hub" or service["to"] != "end" or service.id == current_service:
			continue
		var estimated := forecast_direct_arrival(id, service, earliest)
		if estimated < best_arrival:
			best = service.id
			best_arrival = estimated
	return best

func shadow_copy_after_tick():
	# Internal test-only copy. No untrusted input is accepted by this helper.
	var copy = load("res://automatic_reroute_fixture.gd").new(planner, 0)
	copy.tick = tick + 1
	copy.services = services.duplicate(true)
	copy.passengers = passengers.duplicate(true)
	copy.trace = []
	for service_id in ledgers:
		var restored = Ledger.restore(ledgers[service_id].snapshot())
		if restored == null:
			return null
		copy.ledgers[service_id] = restored
	return copy

func projected_completions(model) -> Dictionary:
	var results := {}
	if model == null or model.passengers.size() > 20:
		return {}
	for id in model.passengers:
		var state: String = model.passengers[id].state
		if state == "completed":
			results[id] = -1
		elif state not in ["waiting", "onboard"]:
			return {}
	for step_index in range(512):
		if results.size() == model.passengers.size():
			return results
		var before: int = model.trace.size()
		model.step()
		for index in range(before, model.trace.size()):
			var event: Array = model.trace[index]
			if event.size() >= 3 and event[1] == "completed":
				results[event[2]] = event[0]
	return {}

func guarded_switch_is_pareto(id: String, old_service: String, new_service: String) -> bool:
	# Conservative fixed-fixture trial: no unseen requests, disruptions, or future replans.
	var alternative = shadow_copy_after_tick()
	if alternative == null:
		return false
	if not alternative.ledgers[old_service].cancel(id):
		return false
	if not alternative.ledgers[new_service].request(id):
		return false
	alternative.passengers[id].service = new_service
	if not baseline_cache_ready:
		baseline_evaluations += 1
		baseline_cache = projected_completions(shadow_copy_after_tick())
		baseline_cache_ready = true
	var before := baseline_cache
	var after := projected_completions(alternative)
	if before.is_empty() or after.size() != before.size():
		return false
	var improved := false
	for passenger_id in before:
		if not after.has(passenger_id) or after[passenger_id] > before[passenger_id]:
			return false
		if after[passenger_id] < before[passenger_id]:
			improved = true
	return improved

func step() -> void:
	for service in services:
		var ledger = ledgers[service.id]
		for id in ledger.aboard.duplicate():
			if passengers[id].due == tick:
				var exited: bool = ledger.disembark(id)
				assert(exited)
				passengers[id].stop = service["to"]
				passengers[id].state = "routing"
				passengers[id].service = ""
				trace.append([tick, "arrived", id, service.id])
				queue_next(id)
	var missed: Array = []
	for service in services:
		if not service.enabled or tick % service.period != service.offset:
			continue
		var ledger = ledgers[service.id]
		ledger.allocate()
		for id in ledger.reserved.duplicate():
			var boarded: bool = ledger.board(id)
			assert(boarded)
			passengers[id].state = "onboard"
			passengers[id].due = tick + service.duration
			trace.append([tick, "departed", id, service.id])
		if capacity_replan:
			for id in ledger.waiting.duplicate():
				missed.append([id, service.id])
	# Defer transfers until every departure in this tick has closed.
	baseline_cache_ready = false
	baseline_cache = {}
	for item in missed:
		var id: String = item[0]
		var old_service: String = item[1]
		var chosen := old_service
		if forecast_replan:
			chosen = choose_forecast_service(id, old_service, tick + 1)
		else:
			var alternative = planner.plan(stops, services, passengers[id].stop, "end", tick + 1)
			if alternative.ok and not alternative.legs.is_empty():
				chosen = alternative.legs[0].service
		if chosen != old_service and guarded_replan and not guarded_switch_is_pareto(id, old_service, chosen):
			chosen = old_service
		if chosen != old_service:
			baseline_cache_ready = false
			var cancelled: bool = ledgers[old_service].cancel(id)
			assert(cancelled)
			var accepted: bool = ledgers[chosen].request(id)
			assert(accepted)
			passengers[id].state = "waiting"
			passengers[id].service = chosen
			passengers[id].due = -1
			trace.append([tick, "capacity_replan", id, old_service])
			trace.append([tick, "queued", id, chosen])
	tick += 1

func snapshot() -> Dictionary:
	var saved_ledgers := {}
	for id in ledgers:
		saved_ledgers[id] = ledgers[id].snapshot()
	return {"version":5, "tick":tick, "capacity_replan":capacity_replan, "forecast_replan":forecast_replan, "guarded_replan":guarded_replan, "services":services.duplicate(true), "passengers":passengers.duplicate(true), "ledgers":saved_ledgers, "trace":trace.duplicate(true)}

static func restore(data: Dictionary, route_planner):
	if data.get("version") != 5 or not data.get("tick") is int or data.tick < 0 or not data.get("services") is Array or not data.get("passengers") is Dictionary or not data.get("ledgers") is Dictionary or not data.get("trace") is Array:
		return null
	if not data.get("capacity_replan") is bool or not data.get("forecast_replan") is bool or not data.get("guarded_replan") is bool or ((data.forecast_replan or data.guarded_replan) and not data.capacity_replan) or (data.forecast_replan and data.guarded_replan):
		return null
	if not GraphValidation.validate(["origin", "hub", "end"], data.services).is_empty():
		return null
	var result = load("res://automatic_reroute_fixture.gd").new(route_planner, 0)
	if data.services.size() != 3 or data.ledgers.size() != 3:
		return null
	# This fixed fixture supports only its original ordered graph; enabled flags may change.
	for index in range(result.services.size()):
		var expected: Dictionary = result.services[index]
		var stored = data.services[index]
		if not stored is Dictionary:
			return null
		for key in ["id", "from", "to", "period", "offset", "duration", "capacity"]:
			if stored.get(key) != expected[key]:
				return null
		if not stored.get("enabled") is bool:
			return null
	var owners := {}
	for service in data.services:
		if not result.ledgers.has(service.id) or not data.ledgers.has(service.id) or not data.ledgers[service.id] is Dictionary:
			return null
		var l = Ledger.restore(data.ledgers[service.id])
		if l == null or l.capacity != service.capacity or not l.reserved.is_empty():
			return null
		result.ledgers[service.id] = l
		for entry in [[l.waiting,"waiting"], [l.aboard,"onboard"]]:
			for id in entry[0]:
				if owners.has(id) or not data.passengers.has(id):
					return null
				owners[id] = [service.id, entry[1]]
	var service_by_id := {}
	for service in data.services:
		service_by_id[service.id] = service
	for id in data.passengers:
		var p = data.passengers[id]
		if not id is String or not p is Dictionary or p.get("stop") not in ["origin","hub","end"] or not p.get("service") is String or not p.get("due") is int or not p.get("rescue_token") is int or p.rescue_token < 0:
			return null
		if p.get("state") in ["waiting", "onboard", "stranded"]:
			var ledger_state: String = "onboard" if p.state == "stranded" else p.state
			if not owners.has(id) or owners[id] != [p.service, ledger_state] or not service_by_id.has(p.service):
				return null
			var service: Dictionary = service_by_id[p.service]
			if p.stop != service["from"] or (p.state == "waiting" and (p.due != -1 or not service.enabled)) or (p.state == "onboard" and (p.due < data.tick or p.due > data.tick + service.duration)) or (p.state == "stranded" and (p.due != -1 or service.enabled)) :
				return null
		elif p.get("state") in ["completed", "failed"]:
			if owners.has(id) or p.service != "" or p.due != -1 or (p.state == "completed" and p.stop != "end"):
				return null
		else:
			return null
	result.tick = data.tick
	result.capacity_replan = data.capacity_replan
	result.forecast_replan = data.forecast_replan
	result.guarded_replan = data.guarded_replan
	result.services = data.services.duplicate(true)
	result.passengers = data.passengers.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result

