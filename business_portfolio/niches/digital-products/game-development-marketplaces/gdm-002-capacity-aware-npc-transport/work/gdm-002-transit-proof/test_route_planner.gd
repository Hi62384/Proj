extends SceneTree
const Planner = preload("res://route_planner.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	var stops = ["origin", "hub", "end"]
	var services = [
		{"id":"a", "from":"origin", "to":"hub", "period":4, "offset":0, "duration":2, "capacity":2, "enabled":true},
		{"id":"b", "from":"hub", "to":"end", "period":5, "offset":3, "duration":2, "capacity":2, "enabled":true},
		{"id":"direct", "from":"origin", "to":"end", "period":10, "offset":0, "duration":9, "capacity":1, "enabled":true}
	]
	var route = Planner.plan(stops, services, "origin", "end", 0)
	check(route.ok and route.arrival == 5 and route.legs.size() == 2, "earliest transfer")
	services[1].enabled = false
	route = Planner.plan(stops, services, "origin", "end", 0)
	check(route.ok and route.arrival == 9 and route.legs[0].service == "direct", "reroute after disruption")
	services[2].enabled = false
	route = Planner.plan(stops, services, "origin", "end", 0)
	check(not route.ok and route.error == "no_route", "unreachable route terminates")
	services[1].enabled = true
	route = Planner.plan(stops, services, "origin", "end", 1)
	check(route.ok and route.arrival == 10, "missed departure waits for next service")
	var invalid = services.duplicate(true)
	invalid[0].duration = 0
	check(Planner.plan(stops, invalid, "origin", "end", 0).error == "invalid_schedule", "zero travel time rejected")
	invalid = services.duplicate(true)
	invalid.append(invalid[0].duplicate(true))
	check(Planner.plan(stops, invalid, "origin", "end", 0).error == "invalid_service_id", "duplicate identifiers rejected")
	var ties = [
		{"id":"z", "from":"origin", "to":"end", "period":1, "offset":0, "duration":1, "capacity":1, "enabled":true},
		{"id":"a", "from":"origin", "to":"end", "period":1, "offset":0, "duration":1, "capacity":1, "enabled":true}
	]
	check(Planner.plan(stops, ties, "origin", "end", 0).legs[0].service == "a", "stable tie-break")
	ties.reverse()
	check(Planner.plan(stops, ties, "origin", "end", 0).legs[0].service == "a", "tie independent of input order")
	ties[0].id = "bad/id"
	check(Planner.plan(stops, ties, "origin", "end", 0).error == "invalid_service_id", "reserved separator rejected")
	var same = Planner.plan(stops, services, "origin", "origin", 2)
	check(same.ok and same.arrival == 2 and same.legs.is_empty(), "already at destination")
	print("Time-dependent route planner: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
