extends RefCounted

# A deliberately small, synchronous seat/queue proof, not a route planner.
var capacity: int
var waiting: Array[String] = []
var reserved: Array[String] = []
var aboard: Array[String] = []
var events: Array[String] = []

func _init(seats: int) -> void:
	assert(seats > 0)
	capacity = seats

func request(id: String) -> bool:
	if id.is_empty() or waiting.has(id) or reserved.has(id) or aboard.has(id):
		return false
	waiting.append(id)
	events.append("queued:" + id)
	return true

func allocate() -> void:
	while not waiting.is_empty() and reserved.size() + aboard.size() < capacity:
		var id: String = waiting.pop_front()
		reserved.append(id)
		events.append("reserved:" + id)

func board(id: String) -> bool:
	if not reserved.has(id):
		return false
	reserved.erase(id)
	aboard.append(id)
	events.append("boarded:" + id)
	return true

func cancel(id: String) -> bool:
	if waiting.has(id):
		waiting.erase(id)
	elif reserved.has(id):
		reserved.erase(id)
	else:
		return false
	events.append("cancelled:" + id)
	return true

func snapshot() -> Dictionary:
	return {"version": 1, "capacity": capacity, "waiting": waiting.duplicate(), "reserved": reserved.duplicate(), "aboard": aboard.duplicate(), "events": events.duplicate()}

static func restore(data: Dictionary):
	if data.get("version") != 1 or not data.get("capacity") is int or data.capacity <= 0:
		return null
	for key in ["waiting", "reserved", "aboard", "events"]:
		if not data.get(key) is Array:
			return null
	if data.reserved.size() + data.aboard.size() > data.capacity:
		return null
	var seen := {}
	for group in [data.waiting, data.reserved, data.aboard]:
		for id in group:
			if not id is String or id.is_empty() or seen.has(id):
				return null
			seen[id] = true
	for event in data.events:
		if not event is String:
			return null
	var result = load("res://transit.gd").new(data.capacity)
	result.waiting.assign(data.waiting)
	result.reserved.assign(data.reserved)
	result.aboard.assign(data.aboard)
	result.events.assign(data.events)
	return result

func disembark(id: String) -> bool:
	if not aboard.has(id):
		return false
	aboard.erase(id)
	events.append("disembarked:" + id)
	return true

func return_unboarded_to_queue() -> Array[String]:
	# Preserve FIFO order when a boarding window closes before acknowledgment.
	var missed: Array[String] = reserved.duplicate()
	reserved.clear()
	for id in missed:
		events.append("missed:" + id)
	waiting = missed + waiting
	return missed
