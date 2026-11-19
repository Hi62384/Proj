extends RefCounted
# Fixed two-leg experiment with explicit boarding callbacks; not a general scheduler.
const Ledger = preload("res://transit.gd")
const CONFIG = {"A": {"period": 4, "offset": 0, "capacity": 3}, "B": {"period": 5, "offset": 2, "capacity": 2}}
var tick := 0
var phase := "ready"
var passengers := {}
var ledgers := {"A": Ledger.new(3), "B": Ledger.new(2)}
var trace: Array = []

func _init(count := 20) -> void:
	for i in range(count):
		var id := "npc%02d" % i
		passengers[id] = {"state": "waiting", "leg": "A", "token": 0}
		ledgers.A.request(id)

func begin_tick() -> bool:
	if phase != "ready":
		return false
	for vehicle in ["A", "B"]:
		var config: Dictionary = CONFIG[vehicle]
		var ledger = ledgers[vehicle]
		if tick % config.period == (config.offset + 1) % config.period:
			for id in ledger.aboard.duplicate():
				if passengers[id].state == "stranded":
					continue
				ledger.disembark(id)
				trace.append([tick, "arrive", vehicle, id])
				if vehicle == "A":
					passengers[id] = {"state": "waiting", "leg": "B", "token": passengers[id].token}
					ledgers.B.request(id)
				else:
					passengers[id] = {"state": "completed", "leg": "B", "token": passengers[id].token}
		if tick % config.period == config.offset:
			ledger.allocate()
			for id in ledger.reserved:
				passengers[id].state = "boarding"
				passengers[id].token += 1
	phase = "boarding"
	return true

func acknowledge_board(vehicle: String, id: String, token: int) -> bool:
	if phase != "boarding" or not ledgers.has(vehicle) or not passengers.has(id):
		return false
	if tick % CONFIG[vehicle].period != CONFIG[vehicle].offset:
		return false
	if passengers[id].state != "boarding" or passengers[id].leg != vehicle or passengers[id].token != token:
		return false
	if not ledgers[vehicle].board(id):
		return false
	passengers[id].state = "onboard"
	trace.append([tick, "board", vehicle, id])
	return true

func cancel(id: String) -> bool:
	if not passengers.has(id) or passengers[id].state not in ["waiting", "boarding"]:
		return false
	var vehicle: String = passengers[id].leg
	if not ledgers[vehicle].cancel(id):
		return false
	passengers[id].state = "cancelled"
	passengers[id].token += 1
	trace.append([tick, "cancel", vehicle, id])
	return true

func disrupt_final_leg() -> bool:
	# No alternate service in this fixed graph. Riders await explicit rescue.
	var affected := false
	for id in passengers:
		var p: Dictionary = passengers[id]
		if p.state in ["completed", "cancelled", "failed", "stranded"]:
			continue
		var vehicle: String = p.leg
		affected = true
		p.token += 1
		p["reason"] = "no_route_final_service_disabled"
		if p.state == "onboard":
			p.state = "stranded"
			trace.append([tick, "stranded", vehicle, id])
		else:
			ledgers[vehicle].cancel(id)
			p.state = "failed"
			trace.append([tick, "failed", vehicle, id])
	return affected

func acknowledge_rescue(id: String, token: int) -> bool:
	if not passengers.has(id) or passengers[id].state != "stranded" or passengers[id].token != token:
		return false
	var vehicle: String = passengers[id].leg
	if not ledgers[vehicle].disembark(id):
		return false
	passengers[id].state = "failed"
	trace.append([tick, "rescued", vehicle, id])
	return true

func finish_tick() -> bool:
	if phase != "boarding":
		return false
	# Unacknowledged reservations return to the front in their existing order.
	for vehicle in ["A", "B"]:
		if tick % CONFIG[vehicle].period == CONFIG[vehicle].offset:
			for id in ledgers[vehicle].return_unboarded_to_queue():
				passengers[id].state = "waiting"
				trace.append([tick, "missed", vehicle, id])
	phase = "ready"
	tick += 1
	return true

func snapshot() -> Dictionary:
	return {"version": 3, "tick": tick, "phase": phase, "passengers": passengers.duplicate(true), "ledgers": {"A": ledgers.A.snapshot(), "B": ledgers.B.snapshot()}, "trace": trace.duplicate(true)}

static func restore(data: Dictionary):
	if data.get("version") != 3 or not data.get("tick") is int or data.tick < 0 or data.get("phase") not in ["ready", "boarding"]:
		return null
	if not data.get("passengers") is Dictionary or not data.get("ledgers") is Dictionary or not data.get("trace") is Array:
		return null
	if data.ledgers.keys().size() != 2 or not data.ledgers.has("A") or not data.ledgers.has("B"):
		return null
	var result = load("res://callback_schedule.gd").new(0)
	var owners := {}
	for vehicle in ["A", "B"]:
		if not data.ledgers[vehicle] is Dictionary:
			return null
		var ledger = Ledger.restore(data.ledgers[vehicle])
		if ledger == null or ledger.capacity != CONFIG[vehicle].capacity:
			return null
		result.ledgers[vehicle] = ledger
		for group in ["waiting", "reserved", "aboard"]:
			for id in ledger.get(group):
				if owners.has(id):
					return null
				owners[id] = [vehicle, group]
	for id in data.passengers:
		var p = data.passengers[id]
		if not id is String or not p is Dictionary or p.get("leg") not in ["A", "B"] or not p.get("token") is int or p.token < 0:
			return null
		if p.get("state") in ["completed", "cancelled", "failed"]:
			if owners.has(id) or (p.state == "completed" and p.leg != "B") or (p.state == "failed" and p.get("reason") != "no_route_final_service_disabled"):
				return null
		else:
			if p.get("state") == "stranded" and p.get("reason") != "no_route_final_service_disabled":
				return null
			var expected = {"waiting": "waiting", "boarding": "reserved", "onboard": "aboard", "stranded": "aboard"}.get(p.get("state"), "invalid")
			if not owners.has(id) or owners[id] != [p.leg, expected]:
				return null
	for id in owners:
		if not data.passengers.has(id):
			return null
	result.tick = data.tick
	result.phase = data.phase
	result.passengers = data.passengers.duplicate(true)
	result.trace = data.trace.duplicate(true)
	return result
