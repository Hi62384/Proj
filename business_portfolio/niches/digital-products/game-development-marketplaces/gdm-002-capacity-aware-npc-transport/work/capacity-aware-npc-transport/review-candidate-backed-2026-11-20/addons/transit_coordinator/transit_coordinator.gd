extends Node

# All public calls belong to the scene's owning thread. Movement controllers
# acknowledge each request after the associated action completes.
signal transit_event(event: Dictionary)
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var _core
var _dispatching := false
var last_error := ""

func configure(config: Dictionary, run_id: String) -> bool:
	if _dispatching:
		last_error = "dispatch_in_progress"
		return false
	var result := Core.create(config, run_id)
	if not result.ok:
		last_error = result.error
		return false
	_core = result.coordinator
	last_error = ""
	return true

func request_journey(agent: String, origin: String, destination: String) -> bool:
	if _core == null:
		last_error = "not_configured"
		return false
	var result = _core.request_journey(agent, origin, destination)
	last_error = "" if result.ok else result.error
	_flush()
	return result.ok

func change_destination(agent: String, destination: String) -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.change_destination(agent, destination)
	_flush()
	return result

func cancel_journey(agent: String) -> bool:
	if _core == null:
		return false
	var result: bool = _core.cancel_journey(agent)
	_flush()
	return result

func remove_destroyed_agent(agent: String) -> bool:
	if _core == null:
		return false
	var result: bool = _core.remove_destroyed_agent(agent)
	_flush()
	return result

func begin_tick() -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.begin_tick()
	_flush()
	return result

func open_boarding() -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.open_boarding()
	_flush()
	return result

func finish_tick() -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.finish_tick()
	_flush()
	return result

func acknowledge_boarding(agent: String, vehicle: String, token: int, request_id: String) -> bool:
	if _core == null:
		return false
	var result: bool = _core.acknowledge_boarding(agent, vehicle, token, request_id)
	_flush()
	return result

func acknowledge_alighting(agent: String, vehicle: String, token: int, request_id: String) -> bool:
	if _core == null:
		return false
	var result: bool = _core.acknowledge_alighting(agent, vehicle, token, request_id)
	_flush()
	return result

func acknowledge_recovery(agent: String, vehicle: String, token: int, request_id: String, safe_stop: String) -> bool:
	if _core == null:
		return false
	var result: bool = _core.acknowledge_recovery(agent, vehicle, token, request_id, safe_stop)
	_flush()
	return result

func set_service_enabled(service: String, enabled: bool) -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.set_service_enabled(service, enabled)
	_flush()
	return result

func set_stop_enabled(stop: String, enabled: bool) -> bool:
	if _core == null or _dispatching:
		return false
	var result: bool = _core.set_stop_enabled(stop, enabled)
	_flush()
	return result

func current_tick() -> int:
	return -1 if _core == null else _core.tick()

func journey(agent: String) -> Dictionary:
	return {} if _core == null else _core.journey(agent)

func pending_request(agent: String) -> Dictionary:
	return {} if _core == null else _core.pending_request(agent)

func inspect_vehicle(vehicle: String) -> Dictionary:
	return {"ok":false,"reason":"not_configured"} if _core == null else _core.inspect_vehicle(vehicle)

func diagnose(agent: String) -> Dictionary:
	return {"ok": false, "reason": "not_configured"} if _core == null else _core.diagnose(agent)

func save_snapshot() -> Dictionary:
	# A signal callback can run while an event batch is in flight; prevent partial saves.
	if _core == null or _dispatching:
		return {"ok": false, "error": "not_configured" if _core == null else "dispatch_in_progress"}
	return {"ok": true, "snapshot": _core.snapshot()}

func restore_snapshot(config: Dictionary, data: Dictionary) -> bool:
	if _dispatching:
		last_error = "dispatch_in_progress"
		return false
	var result := Core.restore(config, data)
	if not result.ok:
		last_error = result.error
		return false
	_core = result.coordinator
	last_error = ""
	_flush()
	return true

func _flush() -> void:
	if _dispatching or _core == null:
		return
	_dispatching = true
	while true:
		var batch: Array = _core.drain_events()
		if batch.is_empty():
			break
		for event in batch:
			transit_event.emit(event.duplicate(true))
	_dispatching = false
