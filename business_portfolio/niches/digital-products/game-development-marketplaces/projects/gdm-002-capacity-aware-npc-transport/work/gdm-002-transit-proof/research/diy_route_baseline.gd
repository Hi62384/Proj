extends RefCounted
# Independent bounded simple-path enumeration for a small DIY comparison.
const LIMIT := 1000000
const MAX_SEARCH := 100000
var services: Array
var destination: String
var best_tick := LIMIT + 1
var best_key := ""
var best_legs: Array = []
var expansions := 0
var capped := false

static func plan(stops: Array, routes: Array, origin: String, target: String, start: int) -> Dictionary:
	if stops.is_empty() or stops.size() > 10 or routes.size() > 30:
		return {"ok": false, "error": "invalid_graph_size"}
	var stop_set := {}
	for stop in stops:
		if not stop is String or stop.is_empty() or stop_set.has(stop):
			return {"ok": false, "error": "invalid_stop"}
		stop_set[stop] = true
	var ids := {}
	for r in routes:
		if not r is Dictionary:
			return {"ok": false, "error": "invalid_service"}
		if not r.get("id") is String or r.id.is_empty() or "/" in r.id or ids.has(r.id):
			return {"ok": false, "error": "invalid_service_id"}
		ids[r.id] = true
		if not stop_set.has(r.get("from")) or not stop_set.has(r.get("to")) or r["from"] == r["to"]:
			return {"ok": false, "error": "invalid_endpoint"}
		for k in ["period", "offset", "duration", "capacity"]:
			if not r.get(k) is int:
				return {"ok": false, "error": "invalid_schedule"}
		if r.period < 1 or r.period > LIMIT or r.offset < 0 or r.offset >= r.period or r.duration < 1 or r.duration > LIMIT or r.capacity < 1 or not r.get("enabled") is bool:
			return {"ok": false, "error": "invalid_schedule"}
	if not stop_set.has(origin) or not stop_set.has(target) or start < 0 or start > LIMIT:
		return {"ok": false, "error": "invalid_request"}
	var search = load("res://research/diy_route_baseline.gd").new()
	search.services = routes
	search.destination = target
	search.visit(origin, start, {origin: true}, [], "")
	if search.capped:
		return {"ok": false, "error": "search_limit"}
	if search.best_tick > LIMIT:
		return {"ok": false, "error": "no_route"}
	return {"ok": true, "arrival": search.best_tick, "legs": search.best_legs}

func visit(stop: String, time: int, visited: Dictionary, legs: Array, key: String) -> void:
	expansions += 1
	if expansions > MAX_SEARCH:
		capped = true
		return
	if stop == destination:
		if time < best_tick or (time == best_tick and (best_key.is_empty() or key < best_key)):
			best_tick = time
			best_key = key
			best_legs = legs.duplicate(true)
		return
	for r in services:
		if not r.enabled or r["from"] != stop or visited.has(r["to"]):
			continue
		var depart: int = r.offset
		while depart < time:
			depart += r.period
		if depart + r.duration > LIMIT or depart + r.duration > best_tick:
			continue
		var leg = {"service": r.id, "from": stop, "to": r["to"], "depart": depart, "arrive": depart + r.duration}
		visited[r["to"]] = true
		legs.append(leg)
		visit(r["to"], leg.arrive, visited, legs, key + "/" + r.id)
		legs.pop_back()
		visited.erase(r["to"])
