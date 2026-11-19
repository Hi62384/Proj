extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
const Overlay = preload("res://addons/transit_coordinator/debug_overlay.gd")
const Audit = preload("res://addons/transit_coordinator/core/continuity_audit.gd")
func _initialize() -> void:
	var transit = Transit.new()
	var adapter = Adapter.new()
	var overlay = Overlay.new()
	var cfg := {"revision":"install-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":3,"offset":0,"duration":1,"enabled":true}]}
	var ok: bool = Audit.audit(cfg,{"b":{"a":1}},6).ok and adapter.configure(transit) and transit.configure(cfg,"install") and transit.request_journey("npc","a","b") and transit.begin_tick() and transit.open_boarding()
	print("Standalone copied add-on: ","PASS" if ok else "FAIL")
	overlay.free()
	adapter.free()
	transit.free()
	quit(0 if ok else 1)
