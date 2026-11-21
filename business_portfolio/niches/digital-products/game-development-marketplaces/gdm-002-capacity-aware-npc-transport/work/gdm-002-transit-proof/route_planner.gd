extends RefCounted
# Feasibility-only earliest-arrival planner; capacity is not reserved here.
const MAX_TICK := 1000000

static func validate(stops: Array, services: Array) -> String:
	if stops.is_empty() or stops.size() > 100 or services.size() > 500:
		return "invalid_graph_size"
	var known := {}
	for stop in stops:
		if not stop is String or stop.is_empty() or known.has(stop):
			return "invalid_stop"
		known[stop] = true
	var ids := {}
	for s in services:
		if not s is Dictionary:
			return "invalid_service"
		if not s.get("id") is String or s.id.is_empty() or "/" in s.id or ids.has(s.id):
			return "invalid_service_id"
		ids[s.id] = true
		if not known.has(s.get("from")) or not known.has(s.get("to")) or s["from"] == s["to"]:
			return "invalid_endpoint"
		for key in ["period", "offset", "duration", "capacity"]:
			if not s.get(key) is int:
				return "invalid_schedule"
		if s.period < 1 or s.period > MAX_TICK or s.offset < 0 or s.offset >= s.period or s.duration < 1 or s.duration > MAX_TICK or s.capacity < 1 or not s.get("enabled") is bool:
			return "invalid_schedule"
	return ""

static func plan(stops: Array, services: Array, origin: String, destination: String, start_tick: int) -> Dictionary:
	var error := validate(stops, services)
	if not error.is_empty():
		return {"ok": false, "error": error}
	if not stops.has(origin) or not stops.has(destination) or start_tick < 0 or start_tick > MAX_TICK:
		return {"ok": false, "error": "invalid_request"}
	var best := {origin: start_tick}
	var keys := {origin: ""}
	var parent := {}
	var settled := {}
	while true:
		var current := ""
		for stop in best:
			if settled.has(stop):
				continue
			if current.is_empty() or best[stop] < best[current] or (best[stop] == best[current] and (keys[stop] < keys[current] or (keys[stop] == keys[current] and stop < current))):
				current = stop
		if current.is_empty():
			return {"ok": false, "error": "no_route"}
		if current == destination:
			var legs: Array = []
			var node := destination
			while node != origin:
				var leg: Dictionary = parent[node]
				legs.push_front(leg)
				node = leg["from"]
			return {"ok": true, "arrival": best[destination], "legs": legs}
		settled[current] = true
		for service in services:
			if not service.enabled or service["from"] != current or settled.has(service["to"]):
				continue
			var depart: int = service.offset
			if best[current] > depart:
				depart += ceili(float(best[current] - depart) / float(service.period)) * service.period
			var arrival: int = depart + service.duration
			if arrival > MAX_TICK:
				continue
			var next: String = service["to"]
			var route_key: String = keys[current] + "/" + service.id
			if not best.has(next) or arrival < best[next] or (arrival == best[next] and route_key < keys[next]):
				best[next] = arrival
				keys[next] = route_key
				parent[next] = {"service": service.id, "from": current, "to": next, "depart": depart, "arrive": arrival}
	return {"ok": false, "error": "no_route"}
