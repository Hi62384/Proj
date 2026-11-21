extends RefCounted
# Independent FIFO coordinator for this fixed three-service comparison.
var planner
var tick := 0
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

func _init(route_planner, count := 20) -> void:
	planner = route_planner
	for i in range(count):
		var id := "npc%02d" % i
		passengers[id] = {"state":"routing", "stop":"origin", "service":"", "due":-1, "rescue_token":0}
		queue_next(id)

func queue_next(id: String) -> void:
	var p: Dictionary = passengers[id]
	if p.stop == "end":
		p.state = "completed"
		p.service = ""
		p.due = -1
		trace.append([tick, "completed", id])
		return
	var route = planner.plan(stops, services, p.stop, "end", tick)
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
	for service in services:
		if not service.enabled or tick % service.period != service.offset:
			continue
		while not waiting[service.id].is_empty() and aboard[service.id].size() < service.capacity:
			var id = waiting[service.id].pop_front()
			aboard[service.id].append(id)
			passengers[id].state = "onboard"
			passengers[id].due = tick + service.duration
			trace.append([tick, "departed", id, service.id])
	tick += 1

func snapshot() -> Dictionary:
	return {"version":1, "tick":tick, "services":services.duplicate(true), "passengers":passengers.duplicate(true), "waiting":waiting.duplicate(true), "aboard":aboard.duplicate(true), "trace":trace.duplicate(true)}

static func restore(data: Dictionary, route_planner):
	# Trusted fixed-fixture data: check ownership and capacity; not a general save parser.
	if data.get("version") != 1 or not data.get("tick") is int or data.tick < 0 or not data.get("services") is Array or not data.get("passengers") is Dictionary or not data.get("waiting") is Dictionary or not data.get("aboard") is Dictionary or not data.get("trace") is Array:
		return null
	var result = load("res://research/diy_auto_coordinator.gd").new(route_planner, 0)
	if data.services.size() != 3 or data.waiting.size() != 3 or data.aboard.size() != 3:
		return null
	var seen := {}
	for service in data.services:
		if not service is Dictionary or not result.waiting.has(service.get("id")) or not data.waiting.get(service.id) is Array or not data.aboard.get(service.id) is Array:
			return null
		if not service.get("capacity") is int or service.capacity < 1 or data.aboard[service.id].size() > service.capacity:
			return null
		for group in [["waiting", "waiting"], ["aboard", "onboard"]]:
			for id in data[group[0]][service.id]:
				if seen.has(id) or not data.passengers.has(id):
					return null
				var p = data.passengers[id]
				if not p is Dictionary or p.get("service") != service.id or (p.get("state") != group[1] and not (group[0] == "aboard" and p.get("state") == "stranded")):
					return null
				seen[id] = true
	for id in data.passengers:
		var p = data.passengers[id]
		if not p is Dictionary:
			return null
		if p.get("state") in ["completed", "failed"]:
			if seen.has(id):
				return null
		elif not seen.has(id):
			return null
	result.tick = data.tick
	result.services = data.services.duplicate(true)
	result.passengers = data.passengers.duplicate(true)
	result.waiting = data.waiting.duplicate(true)
	result.aboard = data.aboard.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result
