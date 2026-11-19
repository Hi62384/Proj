extends Node

# Optional example adapter. A game supplies navigation, destination coordinates,
# and an arrival predicate that verifies physical contact/safety. All calls must
# happen on the scene's owning thread. Never auto-acknowledge an unverified move.
signal movement_finished(agent: String, request_id: String)
signal movement_failed(agent: String, request_id: String, reason: String)

var _transit: Node
var _agents := {}
var _moves := {}

func configure(transit: Node) -> bool:
	if not _moves.is_empty() or not is_instance_valid(transit) or not transit.has_method("acknowledge_boarding") or not transit.has_method("pending_request") or not transit.has_signal("transit_event"):
		return false
	var callback := Callable(self,"_on_transit_event")
	if is_instance_valid(_transit) and _transit.is_connected("transit_event",callback):
		_transit.disconnect("transit_event",callback)
	_transit = transit
	_transit.connect("transit_event",callback)
	return true

func _on_transit_event(event: Dictionary) -> void:
	var id = event.get("agent")
	if not id is String or not _moves.has(id):
		return
	var kind = event.get("type")
	var old_id: String = _moves[id].event.id
	var replaced: bool = kind in ["boarding_requested","alighting_requested","recovery_requested"] and event.get("id") != old_id
	var ended: bool = kind in ["boarding_missed","journey_cancelled","journey_failed","journey_completed","agent_removed"]
	if replaced or ended:
		cancel_movement(id)
		movement_failed.emit(id,old_id,"superseded")

func register_agent(id: String, body: CharacterBody3D, navigation: NavigationAgent3D) -> bool:
	if id.is_empty() or not is_instance_valid(body) or not is_instance_valid(navigation) or _agents.has(id):
		return false
	_agents[id] = {"body":body,"navigation":navigation}
	return true

func unregister_agent(id: String) -> void:
	cancel_movement(id)
	_agents.erase(id)

func cancel_movement(id: String) -> void:
	# This stops only this adapter's movement. It does not cancel the journey or
	# release a claimed/occupied seat, which require coordinator/game handling.
	if _moves.has(id):
		var body = _agents.get(id,{}).get("body")
		if is_instance_valid(body):
			body.velocity.x = 0
			body.velocity.z = 0
		_moves.erase(id)

func move_for_request(event: Dictionary, target: Vector3, arrival_check: Callable, safe_stop := "", speed := 2.0, tolerance := 0.4, timeout := 10.0) -> bool:
	if not is_instance_valid(_transit) or event.get("type") not in ["boarding_requested","alighting_requested","recovery_requested"] or not event.get("agent") is String or not event.get("id") is String or not event.get("details") is Dictionary:
		return false
	var id: String = event.agent
	var details: Dictionary = event.details
	if not _agents.has(id) or not is_instance_valid(_agents[id].body) or not is_instance_valid(_agents[id].navigation) or not details.get("vehicle") is String or not details.get("token") is int or not arrival_check.is_valid() or not target.is_finite() or not is_finite(speed) or not is_finite(tolerance) or not is_finite(timeout) or speed <= 0.0 or tolerance <= 0.0 or timeout <= 0.0:
		return false
	if event.type == "recovery_requested" and (not details.get("safe_stops") is Array or safe_stop not in details.safe_stops):
		return false
	var current: Dictionary = _transit.pending_request(id)
	if current.get("id") != event.id or current.get("type") != event.type or current.get("details") != details:
		return false
	cancel_movement(id)
	_agents[id].navigation.target_position = target
	_moves[id] = {"event":event.duplicate(true),"target":target,"check":arrival_check,"safe_stop":safe_stop,"speed":speed,"tolerance":tolerance,"timeout":timeout,"elapsed":0.0}
	return true

func _physics_process(delta: float) -> void:
	for id in _moves.keys().duplicate():
		if not _moves.has(id):
			continue
		var move: Dictionary = _moves[id]
		var agent: Dictionary = _agents.get(id,{})
		var body = agent.get("body")
		var navigation = agent.get("navigation")
		if not is_instance_valid(body) or not is_instance_valid(navigation) or not is_instance_valid(_transit):
			_moves.erase(id)
			movement_failed.emit(id,move.event.id,"agent_or_coordinator_missing")
			continue
		move.elapsed += delta
		var planar := Vector2(body.global_position.x-move.target.x,body.global_position.z-move.target.z)
		var arrived := false
		if planar.length() <= move.tolerance and move.check.is_valid():
			arrived = bool(move.check.call(body,move.event.duplicate(true)))
		# The callback belongs to game code and can replace or cancel the task.
		if not _moves.has(id) or not is_same(_moves[id],move):
			continue
		if arrived:
			cancel_movement(id)
			var event: Dictionary = move.event
			var accepted := false
			if event.type == "boarding_requested":
				accepted = _transit.acknowledge_boarding(id,event.details.vehicle,event.details.token,event.id)
			elif event.type == "alighting_requested":
				accepted = _transit.acknowledge_alighting(id,event.details.vehicle,event.details.token,event.id)
			else:
				accepted = _transit.acknowledge_recovery(id,event.details.vehicle,event.details.token,event.id,move.safe_stop)
			if accepted:
				movement_finished.emit(id,event.id)
			else:
				movement_failed.emit(id,event.id,"stale_or_rejected")
			continue
		if move.elapsed >= move.timeout:
			cancel_movement(id)
			movement_failed.emit(id,move.event.id,"timeout")
			continue
		var point: Vector3 = navigation.get_next_path_position()
		var direction := Vector2(point.x-body.global_position.x,point.z-body.global_position.z).normalized()
		body.velocity.x = direction.x * move.speed
		body.velocity.z = direction.y * move.speed
		body.velocity.y -= 9.8 * delta
		body.move_and_slide()
