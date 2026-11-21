extends RefCounted
# Integration harness for the DIY proof; a prospective controller adapter, not a public API.
const Core = preload("res://research/diy_validated_baseline.gd")
var core = Core.new(1)
func begin() -> bool:
	return core.begin_tick()
func requests(vehicle: String) -> Array:
	var result := []
	for id in core.claims[vehicle]:
		result.append([id, core.people[id].token])
	return result
func board(vehicle: String, id: String, token: int) -> bool:
	return core.acknowledge_board(vehicle, id, token)
func depart() -> bool:
	return core.finish_tick()
func disrupt() -> bool:
	return core.disrupt_final_leg()
func rescue(id: String, token: int) -> bool:
	return core.acknowledge_rescue(id, token)
func token(id: String) -> int:
	return core.people[id].token
func state(id: String) -> String:
	return core.people[id].state
func trace() -> Array:
	return core.trace.duplicate(true)
func save() -> Dictionary:
	return core.snapshot()
func restore(data: Dictionary) -> bool:
	var loaded = Core.restore(data)
	if loaded == null:
		return false
	core = loaded
	return true
