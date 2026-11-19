extends RefCounted
# Independent FIFO coordinator for this fixed three-service comparison.
var planner
var tick := 0
var capacity_replan := false
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
var waiting := {"a": [], "b": [], "c": []}
var aboard := {"a": [], "b": [], "c": []}
var trace: Array = []

func _init(route_planner, count := 20, replan := false, guarded := false) -> void:
	planner = route_planner
	capacity_replan = replan or guarded
	guarded_replan = guarded
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
	waiting[service].append(id)
	p.state = "waiting"
	p.service = service
	p.due = -1
	trace.append([tick, "queued", id, service])

func disrupt_service(service_id: String) -> bool:
	var service: Dictionary = {}
	for item in services:
		if item.id == service_id:
			service = item
	if service.is_empty() or not service.enabled:
		return false
	service.enabled = false
	trace.append([tick, "disrupted", service_id])
	for id in aboard[service_id]:
		passengers[id].state = "stranded"
		passengers[id].due = -1
		passengers[id].rescue_token += 1
		trace.append([tick, "stranded", id, service_id])
	var displaced: Array = waiting[service_id].duplicate()
	waiting[service_id].clear()
	for id in displaced:
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
	if service.is_empty() or safe_stop != service["from"] or not aboard[p.service].has(id):
		return false
	aboard[p.service].erase(id)
	trace.append([tick, "rescued", id, p.service])
	p.stop = safe_stop
	p.state = "routing"
	p.service = ""
	queue_next(id)
	return true

func shadow_copy_after_tick():
	var copy = load("res://research/diy_auto_validated.gd").new(planner, 0)
	copy.tick = tick + 1
	copy.services = services.duplicate(true)
	copy.passengers = passengers.duplicate(true)
	copy.waiting = waiting.duplicate(true)
	copy.aboard = aboard.duplicate(true)
	copy.trace = []
	return copy

func projected_completions(model) -> Dictionary:
	var results := {}
	if model.passengers.size() > 20:
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
	var alternative = shadow_copy_after_tick()
	if not alternative.waiting[old_service].has(id):
		return false
	alternative.waiting[old_service].erase(id)
	alternative.waiting[new_service].append(id)
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
		for id in aboard[service.id].duplicate():
			if passengers[id].due == tick:
				aboard[service.id].erase(id)
				passengers[id].stop = service["to"]
				passengers[id].state = "routing"
				passengers[id].service = ""
				trace.append([tick, "arrived", id, service.id])
				queue_next(id)
	var missed: Array = []
	for service in services:
		if not service.enabled or tick % service.period != service.offset:
			continue
		while not waiting[service.id].is_empty() and aboard[service.id].size() < service.capacity:
			var id = waiting[service.id].pop_front()
			aboard[service.id].append(id)
			passengers[id].state = "onboard"
			passengers[id].due = tick + service.duration
			trace.append([tick, "departed", id, service.id])
		if capacity_replan:
			for id in waiting[service.id].duplicate():
				missed.append([id, service.id])
	baseline_cache_ready = false
	baseline_cache = {}
	for item in missed:
		var id: String = item[0]
		var old_service: String = item[1]
		var alternative = planner.plan(stops, services, passengers[id].stop, "end", tick + 1)
		if alternative.ok and not alternative.legs.is_empty() and alternative.legs[0].service != old_service:
			if guarded_replan and not guarded_switch_is_pareto(id, old_service, alternative.legs[0].service):
				continue
			baseline_cache_ready = false
			waiting[old_service].erase(id)
			passengers[id].state = "routing"
			passengers[id].service = ""
			trace.append([tick, "capacity_replan", id, old_service])
			queue_next(id, tick + 1)
	tick += 1

func snapshot() -> Dictionary:
	return {"version":3, "tick":tick, "capacity_replan":capacity_replan, "guarded_replan":guarded_replan, "services":services.duplicate(true), "passengers":passengers.duplicate(true), "waiting":waiting.duplicate(true), "aboard":aboard.duplicate(true), "trace":trace.duplicate(true)}

static func restore(data: Dictionary, route_planner):
	# Trusted fixed-fixture data: check ownership and capacity; not a general save parser.
	if data.get("version") != 3 or not data.get("tick") is int or data.tick < 0 or not data.get("services") is Array or not data.get("passengers") is Dictionary or not data.get("waiting") is Dictionary or not data.get("aboard") is Dictionary or not data.get("trace") is Array:
		return null
	if not data.get("capacity_replan") is bool or not data.get("guarded_replan") is bool or (data.guarded_replan and not data.capacity_replan):
		return null
	var result = load("res://research/diy_auto_validated.gd").new(route_planner, 0)
	if data.services.size() != 3 or data.waiting.size() != 3 or data.aboard.size() != 3:
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
	var seen := {}
	var service_ids := {}
	for service in data.services:
		if not service is Dictionary or not result.waiting.has(service.get("id")) or not data.waiting.get(service.id) is Array or not data.aboard.get(service.id) is Array:
			return null
		if service_ids.has(service.id):
			return null
		service_ids[service.id] = true
		if service.get("from") not in ["origin", "hub", "end"] or service.get("to") not in ["origin", "hub", "end"] or service["from"] == service["to"] or not service.get("enabled") is bool:
			return null
		for key in ["capacity", "period", "offset", "duration"]:
			if not service.get(key) is int:
				return null
		if service.capacity < 1 or service.period < 1 or service.offset < 0 or service.offset >= service.period or service.duration < 1 or data.aboard[service.id].size() > service.capacity:
			return null
		for group in [["waiting", "waiting"], ["aboard", "onboard"]]:
			for id in data[group[0]][service.id]:
				if seen.has(id) or not data.passengers.has(id):
					return null
				var p = data.passengers[id]
				if not p is Dictionary or p.get("service") != service.id or (p.get("state") != group[1] and not (group[0] == "aboard" and p.get("state") == "stranded")):
					return null
				if p.get("stop") != service["from"] or not p.get("due") is int or not p.get("rescue_token") is int or p.rescue_token < 0:
					return null
				if (p.state == "waiting" and (p.due != -1 or not service.enabled)) or (p.state == "onboard" and (p.due < data.tick or p.due > data.tick + service.duration)) or (p.state == "stranded" and (p.due != -1 or service.enabled)):
					return null
				seen[id] = true
	for id in data.passengers:
		var p = data.passengers[id]
		if not id is String or not p is Dictionary or not p.get("rescue_token") is int or p.rescue_token < 0:
			return null
		if p.get("state") in ["completed", "failed"]:
			if seen.has(id) or p.get("service") != "" or p.get("due") != -1 or (p.state == "completed" and p.get("stop") != "end"):
				return null
		elif not seen.has(id):
			return null
	result.tick = data.tick
	result.capacity_replan = data.capacity_replan
	result.guarded_replan = data.guarded_replan
	result.services = data.services.duplicate(true)
	result.passengers = data.passengers.duplicate(true)
	result.waiting = data.waiting.duplicate(true)
	result.aboard = data.aboard.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result
