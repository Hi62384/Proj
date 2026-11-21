extends Node

# Signal bridge for game-owned movement. The bridge never moves or owns bodies.
# The game must physically validate every boarding, alighting and recovery.
signal movement_requested(event: Dictionary)
signal request_withdrawn(agent: String, request_id: String, reason: String)
signal movement_result(agent: String, request_id: String, accepted: bool)

var _transit: Node
var _pending := {}
var _exiting := false
var _detaching := false

func _enter_tree() -> void:
	_exiting = false

func _exit_tree() -> void:
	_exiting = true
	detach()

func configure(transit: Node) -> bool:
	if _exiting or _detaching or not _pending.is_empty() or not is_instance_valid(transit) or not transit.has_signal("transit_event"):
		return false
	for method in ["pending_request", "acknowledge_boarding", "acknowledge_alighting", "acknowledge_recovery"]:
		if not transit.has_method(method):
			return false
	var callback := Callable(self, "_on_transit_event")
	if is_instance_valid(_transit):
		if _transit.is_connected("transit_event", callback):
			_transit.disconnect("transit_event", callback)
		if _transit.is_connected("tree_exiting", Callable(self, "_on_transit_exiting")):
			_transit.disconnect("tree_exiting", Callable(self, "_on_transit_exiting"))
	_transit = transit
	_transit.connect("transit_event", callback)
	_transit.connect("tree_exiting", Callable(self, "_on_transit_exiting"))
	return true

func detach() -> void:
	# Withdrawal is synchronous; the game must stop its own movement.
	if _detaching:
		return
	_detaching = true
	var old = _transit
	_transit = null
	if is_instance_valid(old):
		if old.is_connected("transit_event", Callable(self, "_on_transit_event")):
			old.disconnect("transit_event", Callable(self, "_on_transit_event"))
		if old.is_connected("tree_exiting", Callable(self, "_on_transit_exiting")):
			old.disconnect("tree_exiting", Callable(self, "_on_transit_exiting"))
	for agent in _pending.keys().duplicate():
		_withdraw(agent, "detached")
	_detaching = false

func _on_transit_exiting() -> void:
	detach()

func _on_transit_event(event: Dictionary) -> void:
	var id = event.get("agent")
	if not id is String or id.is_empty():
		return
	var kind = event.get("type")
	if kind in ["boarding_requested", "alighting_requested", "recovery_requested"]:
		_publish(event)
	elif kind in ["boarding_missed", "journey_cancelled", "journey_failed", "journey_completed", "agent_removed"]:
		_withdraw(id, "ended")

func _withdraw(agent: String, reason: String) -> void:
	if not _pending.has(agent):
		return
	var old_id: String = _pending[agent].id
	_pending.erase(agent)
	request_withdrawn.emit(agent, old_id, reason)

func _publish(event: Dictionary) -> bool:
	if not is_instance_valid(_transit) or not event.get("agent") is String or not event.get("id") is String:
		return false
	var agent: String = event.agent
	var source = _transit
	var current: Dictionary = _transit.pending_request(agent)
	if current.get("id") != event.id or current.get("type") != event.get("type") or current.get("details") != event.get("details"):
		return false
	if _pending.has(agent):
		if _pending[agent].id == event.id:
			return true
		_withdraw(agent, "superseded")
		# Game callbacks can change the coordinator during withdrawal.
		if not is_instance_valid(_transit) or not is_same(_transit, source) or _transit.pending_request(agent).get("id") != event.id:
			return false
		if _pending.has(agent):
			return _pending[agent].id == event.id
	_pending[agent] = event.duplicate(true)
	movement_requested.emit(event.duplicate(true))
	return true

func refresh_request(agent: String) -> bool:
	# Re-announce an outstanding request after restoring the game and coordinator.
	if not is_instance_valid(_transit):
		return false
	var current: Dictionary = _transit.pending_request(agent)
	if current.is_empty():
		_withdraw(agent, "not_pending")
		return false
	return _publish(current)

func complete_movement(event: Dictionary, arrival_check: Callable, safe_stop := "") -> bool:
	if not is_instance_valid(_transit) or not event.get("agent") is String or not event.get("id") is String or not arrival_check.is_valid():
		return false
	var agent: String = event.agent
	var source = _transit
	if not _pending.has(agent) or _pending[agent] != event:
		return false
	var current: Dictionary = _transit.pending_request(agent)
	if current.get("id") != event.id or current.get("type") != event.get("type") or current.get("details") != event.get("details"):
		return false
	if event.type == "recovery_requested" and (not event.details.get("safe_stops") is Array or safe_stop not in event.details.safe_stops):
		return false
	var verified = arrival_check.call(event.duplicate(true))
	# User callbacks may cancel, supersede, restore or free the coordinator.
	if not verified is bool or not verified or not is_instance_valid(_transit) or not is_same(_transit, source) or not _pending.has(agent) or _pending[agent] != event:
		return false
	current = _transit.pending_request(agent)
	if current.get("id") != event.id or current.get("type") != event.type or current.get("details") != event.details:
		return false
	_pending.erase(agent)
	var accepted := false
	if event.type == "boarding_requested":
		accepted = _transit.acknowledge_boarding(agent, event.details.vehicle, event.details.token, event.id)
	elif event.type == "alighting_requested":
		accepted = _transit.acknowledge_alighting(agent, event.details.vehicle, event.details.token, event.id)
	elif event.type == "recovery_requested":
		accepted = _transit.acknowledge_recovery(agent, event.details.vehicle, event.details.token, event.id, safe_stop)
	movement_result.emit(agent, event.id, accepted)
	return accepted
