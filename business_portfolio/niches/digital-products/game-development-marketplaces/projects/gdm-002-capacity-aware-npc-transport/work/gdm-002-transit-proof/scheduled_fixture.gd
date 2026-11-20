extends RefCounted

# A bounded experimental timetable, not a general-purpose transit system.
# Each vehicle travels outbound on its departure tick and returns empty one tick later.
var tick := 0
var passengers := {}
var vehicles := {
	"A": {"capacity": 3, "period": 4, "offset": 0, "origin": "start", "destination": "transfer", "aboard": []},
	"B": {"capacity": 2, "period": 5, "offset": 2, "origin": "transfer", "destination": "end", "aboard": []}
}
var journal: Array = []

func _init(count := 20) -> void:
	for i in range(count):
		passengers["npc%02d" % i] = {"state": "waiting", "stop": "start", "vehicle": "", "ticket": i}

func step() -> void:
	# Arrivals precede departures at the same tick, making the transfer rule explicit.
	for vehicle_id in ["A", "B"]:
		var v: Dictionary = vehicles[vehicle_id]
		if tick % v.period == (v.offset + 1) % v.period:
			for id in v.aboard:
				var p: Dictionary = passengers[id]
				p.stop = v.destination
				p.vehicle = ""
				p.state = "completed" if p.stop == "end" else "waiting"
				p.ticket = tick * 100 + int(id.substr(3))
				journal.append([tick, "arrive", vehicle_id, id])
			v.aboard.clear()
	for vehicle_id in ["A", "B"]:
		var v: Dictionary = vehicles[vehicle_id]
		if tick % v.period != v.offset:
			continue
		var eligible: Array = []
		for id in passengers:
			var p: Dictionary = passengers[id]
			if p.state == "waiting" and p.stop == v.origin:
				eligible.append(id)
		eligible.sort_custom(func(a, b): return passengers[a].ticket < passengers[b].ticket)
		for id in eligible.slice(0, v.capacity):
			var p: Dictionary = passengers[id]
			p.state = "onboard"
			p.vehicle = vehicle_id
			v.aboard.append(id)
			journal.append([tick, "board", vehicle_id, id])
	tick += 1

func snapshot() -> Dictionary:
	return {"version": 1, "tick": tick, "passengers": passengers.duplicate(true), "vehicles": vehicles.duplicate(true), "journal": journal.duplicate(true)}

static func restore(data: Dictionary):
	if data.get("version") != 1 or not data.get("tick") is int or data.tick < 0:
		return null
	if not data.get("passengers") is Dictionary or not data.get("vehicles") is Dictionary or not data.get("journal") is Array:
		return null
	# Only the fixed fixture's configuration is supported; reject changes rather than invent a migration.
	var expected = load("res://scheduled_fixture.gd").new(0)
	if data.vehicles.keys().size() != 2:
		return null
	var seen := {}
	for id in ["A", "B"]:
		if not data.vehicles.has(id) or not data.vehicles[id] is Dictionary:
			return null
		var v: Dictionary = data.vehicles[id]
		for key in ["capacity", "period", "offset", "origin", "destination"]:
			if v.get(key) != expected.vehicles[id][key]:
				return null
		if not v.get("aboard") is Array or v.aboard.size() > v.capacity:
			return null
		for passenger_id in v.aboard:
			if not passenger_id is String or seen.has(passenger_id) or not data.passengers.has(passenger_id):
				return null
			seen[passenger_id] = id
	for id in data.passengers:
		var p = data.passengers[id]
		if not id is String or not p is Dictionary or not p.get("ticket") is int:
			return null
		if p.get("state") == "onboard":
			if not seen.has(id) or p.get("vehicle") != seen[id] or p.get("stop") != data.vehicles[seen[id]].origin:
				return null
		elif p.get("state") == "waiting":
			if seen.has(id) or p.get("vehicle") != "" or p.get("stop") not in ["start", "transfer"]:
				return null
		elif p.get("state") == "completed":
			if seen.has(id) or p.get("vehicle") != "" or p.get("stop") != "end":
				return null
		else:
			return null
	expected.tick = data.tick
	expected.passengers = data.passengers.duplicate(true)
	expected.vehicles = data.vehicles.duplicate(true)
	expected.journal = data.journal.duplicate(true)
	return expected
