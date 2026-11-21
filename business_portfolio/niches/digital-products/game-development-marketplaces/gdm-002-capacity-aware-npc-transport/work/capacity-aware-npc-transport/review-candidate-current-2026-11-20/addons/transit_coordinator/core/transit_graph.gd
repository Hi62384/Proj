extends RefCounted

# Pure deterministic timetable graph. Ticks are integer simulation ticks.
# It proposes routes; it does not reserve a vehicle seat.
const MAX_TICK := 1000000000
const MAX_STOPS := 256
const MAX_VEHICLES := 256
const MAX_SERVICES := 1024
const MAX_SERVICES_PER_VEHICLE := 32
var _config: Dictionary

static func _valid_id(value) -> bool:
	if not value is String or value.is_empty() or value.length() > 64:
		return false
	for i in range(value.length()):
		var code: int = value.unicode_at(i)
		if not ((code >= 48 and code <= 57) or (code >= 65 and code <= 90) or (code >= 97 and code <= 122) or code in [45, 46, 95]):
			return false
	return true

static func _exact_keys(value: Dictionary, allowed: Array) -> bool:
	if value.size() != allowed.size():
		return false
	for key in value:
		if not key is String or not allowed.has(key):
			return false
	return true

static func _gcd(a: int, b: int) -> int:
	while b != 0:
		var remainder := a % b
		a = b
		b = remainder
	return a

static func _services_overlap(a: Dictionary, b: Dictionary) -> bool:
	# Integer, half-open occupancy intervals [departure, departure + duration).
	# Periodic start differences are congruent modulo gcd(period_a, period_b).
	var g := _gcd(a.period, b.period)
	var remainder: int = (b.offset - a.offset) % g
	if remainder < 0:
		remainder += g
	var lower: int = 1 - b.duration
	var upper: int = a.duration - 1
	var k := ceili(float(lower - remainder) / float(g))
	return remainder + k * g <= upper

static func validate(config: Dictionary) -> String:
	if not _exact_keys(config, ["revision", "tick_unit", "stops", "vehicles", "services"]):
		return "invalid_fields"
	if not _valid_id(config.get("revision")) or config.get("tick_unit") != "simulation_tick":
		return "invalid_revision_or_tick_unit"
	for field in ["stops", "vehicles", "services"]:
		if not config.get(field) is Array:
			return "invalid_collection"
	if config.stops.is_empty() or config.stops.size() > MAX_STOPS or config.vehicles.size() > MAX_VEHICLES or config.services.size() > MAX_SERVICES:
		return "invalid_graph_size"
	var stops := {}
	for stop in config.stops:
		if not _valid_id(stop) or stops.has(stop):
			return "invalid_stop"
		stops[stop] = true
	var vehicles := {}
	for vehicle in config.vehicles:
		if not vehicle is Dictionary or not _exact_keys(vehicle, ["id", "capacity"]) or not _valid_id(vehicle.get("id")):
			return "invalid_vehicle"
		if vehicles.has(vehicle.id):
			return "duplicate_vehicle"
		if not vehicle.get("capacity") is int or vehicle.capacity < 1 or vehicle.capacity > 100000:
			return "invalid_capacity"
		vehicles[vehicle.id] = true
	var ids := {}
	var per_vehicle := {}
	for service in config.services:
		if not service is Dictionary or not _exact_keys(service, ["id", "vehicle", "from", "to", "period", "offset", "duration", "enabled"]) or not _valid_id(service.get("id")):
			return "invalid_service"
		if ids.has(service.id):
			return "duplicate_service"
		ids[service.id] = true
		if not _valid_id(service.get("from")) or not _valid_id(service.get("to")) or not stops.has(service["from"]) or not stops.has(service["to"]) or service["from"] == service["to"]:
			return "invalid_endpoint"
		if not _valid_id(service.get("vehicle")) or not vehicles.has(service.vehicle):
			return "unknown_vehicle"
		for field in ["period", "offset", "duration"]:
			if not service.get(field) is int:
				return "invalid_schedule"
		if service.period < 1 or service.period > MAX_TICK or service.offset < 0 or service.offset >= service.period or service.duration < 1 or service.duration > service.period or not service.get("enabled") is bool:
			return "invalid_schedule"
		if not per_vehicle.has(service.vehicle):
			per_vehicle[service.vehicle] = []
		var existing: Array = per_vehicle[service.vehicle]
		if existing.size() >= MAX_SERVICES_PER_VEHICLE:
			return "too_many_vehicle_services"
		for previous in existing:
			if _services_overlap(previous, service):
				return "vehicle_schedule_overlap"
		existing.append(service)
	return ""

static func create(config: Dictionary) -> Dictionary:
	var reason := validate(config)
	if not reason.is_empty():
		return {"ok": false, "error": reason}
	var graph = load("res://addons/transit_coordinator/core/transit_graph.gd").new()
	graph._config = config.duplicate(true)
	return {"ok": true, "graph": graph}

func export_config() -> Dictionary:
	return _config.duplicate(true)

func plan(origin: String, destination: String, start_tick: int) -> Dictionary:
	if not _config.stops.has(origin) or not _config.stops.has(destination) or start_tick < 0 or start_tick > MAX_TICK:
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
		for service in _config.services:
			if not service.enabled or service["from"] != current or settled.has(service["to"]):
				continue
			var departure: int = service.offset
			if best[current] > departure:
				departure += ceili(float(best[current] - departure) / float(service.period)) * service.period
			var arrival: int = departure + service.duration
			if arrival > MAX_TICK:
				continue
			var next: String = service["to"]
			var key: String = keys[current] + "/" + service.id
			if not best.has(next) or arrival < best[next] or (arrival == best[next] and key < keys[next]):
				best[next] = arrival
				keys[next] = key
				parent[next] = {"service": service.id, "vehicle": service.vehicle, "from": current, "to": next, "depart": departure, "arrive": arrival}
	return {"ok": false, "error": "no_route"}
