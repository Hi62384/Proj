extends SceneTree
const Candidate = preload("res://route_planner.gd")
const DIY = preload("res://research/diy_route_baseline.gd")
var failures := 0
var equal_arrival_different_routes := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func valid_route(result: Dictionary, services: Array, start: int) -> bool:
	if not result.ok:
		return result.error == "no_route"
	var stop := "a"
	var now := start
	for leg in result.legs:
		var found := false
		for service in services:
			if service.id != leg.service:
				continue
			if not service.enabled or leg["from"] != stop or leg["to"] != service["to"] or service["from"] != stop:
				return false
			if leg.depart < now or leg.depart < service.offset or (leg.depart - service.offset) % service.period != 0 or leg.arrive != leg.depart + service.duration:
				return false
			found = true
		if not found:
			return false
		stop = leg["to"]
		now = leg.arrive
	return stop == "e" and now == result.arrival

func _initialize() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 52483
	var stops = ["a", "b", "c", "d", "e"]
	for case_id in range(500):
		var services := []
		for edge in range(10):
			var from: int = rng.randi_range(0,4)
			var to: int = (from + rng.randi_range(1,4)) % 5
			var period: int = rng.randi_range(1,8)
			services.append({"id":"s%02d" % edge, "from":stops[from], "to":stops[to], "period":period, "offset":rng.randi_range(0,period-1), "duration":rng.randi_range(1,6), "capacity":rng.randi_range(1,4), "enabled":rng.randi_range(0,3) != 0})
		var start: int = rng.randi_range(0,15)
		var a = Candidate.plan(stops, services, "a", "e", start)
		var b = DIY.plan(stops, services, "a", "e", start)
		check(a.ok == b.ok, "matching reachability %d" % case_id)
		check(valid_route(a, services, start) and valid_route(b, services, start), "valid itineraries %d" % case_id)
		if a.ok and b.ok:
			check(a.arrival == b.arrival, "same earliest arrival %d" % case_id)
			if a.legs != b.legs:
				equal_arrival_different_routes += 1
		check(a == Candidate.plan(stops, services, "a", "e", start), "candidate deterministic %d" % case_id)
		services.reverse()
		check(a == Candidate.plan(stops, services, "a", "e", start), "candidate independent of service order %d" % case_id)
	print("Route planner comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 500 seeded graphs; ", equal_arrival_different_routes, " equal-arrival route differences)")
	quit(0 if failures == 0 else 1)
