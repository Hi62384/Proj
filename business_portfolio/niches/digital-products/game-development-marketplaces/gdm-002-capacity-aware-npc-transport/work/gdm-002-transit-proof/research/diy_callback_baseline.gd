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
			for id in riders[v]:
				trace.append([tick, "arrive", v, id])
				if v == "A":
					people[id].leg = "B"
					people[id].state = "waiting"
					queues.B.append(id)
				else:
					people[id].state = "completed"
			riders[v].clear()
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
	# Trusted fixture only; this baseline deliberately does not validate corrupt saves.
	var result = load("res://research/diy_callback_baseline.gd").new(0)
	result.tick = data.tick
	result.phase = data.phase
	result.people = data.people.duplicate(true)
	result.queues = data.queues.duplicate(true)
	result.claims = data.claims.duplicate(true)
	result.riders = data.riders.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result
