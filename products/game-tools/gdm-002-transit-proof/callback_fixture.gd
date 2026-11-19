extends RefCounted

# Adapter-bound feasibility experiment for one scheduled vehicle.
# Calls from a controller are explicit and stale callbacks are rejected.
const Ledger = preload("res://transit.gd")
var ledger = Ledger.new(2)
var state := {}
var generation := {}
var requests: Array = []

func request(agent: String) -> bool:
	if state.has(agent) or not ledger.request(agent):
		return false
	state[agent] = "queued"
	generation[agent] = 0
	return true

func open_boarding() -> void:
	ledger.allocate()
	for agent in ledger.reserved:
		if state[agent] == "queued":
			state[agent] = "boarding"
			generation[agent] += 1
			requests.append({"agent": agent, "token": generation[agent]})

func acknowledge_board(agent: String, token: int) -> bool:
	if state.get(agent) != "boarding" or generation.get(agent) != token:
		return false
	if not ledger.board(agent):
		return false
	state[agent] = "onboard"
	return true

func cancel(agent: String) -> bool:
	if state.get(agent) not in ["queued", "boarding"] or not ledger.cancel(agent):
		return false
	state[agent] = "cancelled"
	generation[agent] += 1
	return true

func acknowledge_exit(agent: String) -> bool:
	if state.get(agent) != "onboard" or not ledger.disembark(agent):
		return false
	state[agent] = "completed"
	return true
