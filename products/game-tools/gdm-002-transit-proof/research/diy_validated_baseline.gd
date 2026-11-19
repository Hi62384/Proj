extends RefCounted
# Independent fixed-route baseline. Navigation remains the game controller's responsibility.
const SERVICES = {"A": [4, 0, 3], "B": [5, 2, 2]}
var tick := 0
var phase := "ready"
var people := {}
var queues := {"A": [], "B": []}
var claims := {"A": [], "B": []}
var riders := {"A": [], "B": []}
var trace := []

func _init(count := 20) -> void:
	for n in range(count):
		var id := "npc%02d" % n
		people[id] = {"state": "waiting", "leg": "A", "token": 0}
		queues.A.append(id)

func begin_tick() -> bool:
	if phase != "ready":
		return false
	for v in ["A", "B"]:
		var route: Array = SERVICES[v]
		if tick % route[0] == (route[1] + 1) % route[0]:
			for id in riders[v].duplicate():
				if people[id].state == "stranded":
					continue
				riders[v].erase(id)
				trace.append([tick, "arrive", v, id])
				if v == "A":
					people[id].leg = "B"
					people[id].state = "waiting"
					queues.B.append(id)
				else:
					people[id].state = "completed"
		if tick % route[0] == route[1]:
			while not queues[v].is_empty() and riders[v].size() + claims[v].size() < route[2]:
				var id = queues[v].pop_front()
				claims[v].append(id)
				people[id].state = "boarding"
				people[id].token += 1
	phase = "boarding"
	return true

func acknowledge_board(v: String, id: String, token: int) -> bool:
	if phase != "boarding" or not SERVICES.has(v) or not people.has(id):
		return false
	if tick % SERVICES[v][0] != SERVICES[v][1] or not claims[v].has(id) or people[id].token != token:
		return false
	claims[v].erase(id)
	riders[v].append(id)
	people[id].state = "onboard"
	trace.append([tick, "board", v, id])
	return true

func cancel(id: String) -> bool:
	if not people.has(id) or people[id].state not in ["waiting", "boarding"]:
		return false
	var v: String = people[id].leg
	if people[id].state == "waiting":
		queues[v].erase(id)
	else:
		claims[v].erase(id)
	people[id].state = "cancelled"
	people[id].token += 1
	trace.append([tick, "cancel", v, id])
	return true

func disrupt_final_leg() -> bool:
	var affected := false
	for id in people:
		var p: Dictionary = people[id]
		if p.state in ["completed", "cancelled", "failed", "stranded"]:
			continue
		var v: String = p.leg
		affected = true
		p.token += 1
		p["reason"] = "no_route_final_service_disabled"
		if p.state == "onboard":
			p.state = "stranded"
			trace.append([tick, "stranded", v, id])
		else:
			queues[v].erase(id)
			claims[v].erase(id)
			p.state = "failed"
			trace.append([tick, "failed", v, id])
	return affected

func acknowledge_rescue(id: String, token: int) -> bool:
	if not people.has(id) or people[id].state != "stranded" or people[id].token != token:
		return false
	var v: String = people[id].leg
	if not riders[v].has(id):
		return false
	riders[v].erase(id)
	people[id].state = "failed"
	trace.append([tick, "rescued", v, id])
	return true

func finish_tick() -> bool:
	if phase != "boarding":
		return false
	for v in ["A", "B"]:
		for id in claims[v]:
			people[id].state = "waiting"
			trace.append([tick, "missed", v, id])
		queues[v] = claims[v] + queues[v]
		claims[v] = []
	tick += 1
	phase = "ready"
	return true

func snapshot() -> Dictionary:
	return {"tick": tick, "phase": phase, "people": people.duplicate(true), "queues": queues.duplicate(true), "claims": claims.duplicate(true), "riders": riders.duplicate(true), "trace": trace.duplicate(true)}

static func restore(data: Dictionary):
	if not data.get("tick") is int or data.tick < 0 or data.get("phase") not in ["ready", "boarding"]:
		return null
	for key in ["people", "queues", "claims", "riders"]:
		if not data.get(key) is Dictionary:
			return null
	if not data.get("trace") is Array:
		return null
	var seen := {}
	for v in ["A", "B"]:
		for collection in ["queues", "claims", "riders"]:
			if not data[collection].get(v) is Array:
				return null
		if data.claims[v].size() + data.riders[v].size() > SERVICES[v][2]:
			return null
		for entry in [["queues", "waiting"], ["claims", "boarding"], ["riders", "onboard"]]:
			for id in data[entry[0]][v]:
				if not id is String or seen.has(id) or not data.people.has(id):
					return null
				var p = data.people[id]
				if not p is Dictionary or (p.get("state") != entry[1] and not (entry[0] == "riders" and p.get("state") == "stranded")) or p.get("leg") != v:
					return null
				seen[id] = true
	for id in data.people:
		var p = data.people[id]
		if not id is String or not p is Dictionary or p.get("leg") not in ["A", "B"] or not p.get("token") is int or p.token < 0:
			return null
		if p.get("state") == "stranded" and p.get("reason") != "no_route_final_service_disabled":
			return null
		if p.get("state") in ["cancelled", "completed", "failed"]:
			if seen.has(id) or (p.state == "completed" and p.leg != "B") or (p.state == "failed" and p.get("reason") != "no_route_final_service_disabled"):
				return null
		elif not seen.has(id):
			return null
	var result = load("res://research/diy_validated_baseline.gd").new(0)
	result.tick = data.tick
	result.phase = data.phase
	result.people = data.people.duplicate(true)
	result.queues = data.queues.duplicate(true)
	result.claims = data.claims.duplicate(true)
	result.riders = data.riders.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result
