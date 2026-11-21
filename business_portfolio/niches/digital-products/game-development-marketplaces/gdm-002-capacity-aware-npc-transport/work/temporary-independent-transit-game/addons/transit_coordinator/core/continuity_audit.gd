extends RefCounted

# Advisory finite-horizon timetable audit. This does not move vehicles or
# verify actual positions; the game supplies conservative reposition times.
const Graph = preload("res://addons/transit_coordinator/core/transit_graph.gd")
const MAX_HORIZON := 10000
const MAX_EVENTS := 100000

static func audit(config: Dictionary, reposition: Dictionary, horizon: int) -> Dictionary:
	var validation: String = Graph.validate(config)
	if not validation.is_empty():
		return {"ok":false,"error":validation}
	if horizon < 1 or horizon > MAX_HORIZON:
		return {"ok":false,"error":"invalid_horizon"}
	var events := {}
	var count := 0
	for vehicle in config.vehicles:
		events[vehicle.id] = []
	for service in config.services:
		if not service.enabled:
			continue
		var tick: int = service.offset
		while tick < horizon:
			count += 1
			if count > MAX_EVENTS:
				return {"ok":false,"error":"too_many_events"}
			events[service.vehicle].append({"departure":tick,"arrival":tick+service.duration,"service":service.id,"from":service["from"],"to":service["to"]})
			tick += service.period
	var conflicts := []
	for vehicle in events:
		var schedule: Array = events[vehicle]
		schedule.sort_custom(func(a,b): return a.departure < b.departure if a.departure != b.departure else a.service < b.service)
		for index in range(1,schedule.size()):
			var previous: Dictionary = schedule[index-1]
			var following: Dictionary = schedule[index]
			var travel := 0
			if previous.to != following.from:
				var destinations = reposition.get(previous.to)
				if not destinations is Dictionary or not destinations.get(following.from) is int or destinations[following.from] < 0 or destinations[following.from] > Graph.MAX_TICK:
					return {"ok":false,"error":"missing_or_invalid_reposition_time","from":previous.to,"to":following.from}
				travel = destinations[following.from]
			if previous.arrival + travel > following.departure:
				conflicts.append({"vehicle":vehicle,"previous":previous.service,"next":following.service,"previous_arrival":previous.arrival,"next_departure":following.departure,"required_reposition":travel})
	return {"ok":true,"feasible":conflicts.is_empty(),"horizon":horizon,"events_checked":count,"conflicts":conflicts}
