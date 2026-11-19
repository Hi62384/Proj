extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Overlay = preload("res://addons/transit_coordinator/debug_overlay.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var parent := Node.new()
	root.add_child(parent)
	var overlay = Overlay.new()
	parent.add_child(overlay)
	overlay.refresh_debug()
	check(overlay._label.text.contains("not connected"),"missing coordinator handled")
	var transit = Transit.new()
	transit.name = "Transit"
	parent.add_child(transit)
	var cfg := {"revision":"overlay-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":2}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":3,"offset":0,"duration":1,"enabled":true}]}
	check(transit.configure(cfg,"overlay") and transit.request_journey("rider","a","b"),"setup")
	overlay.coordinator_path = NodePath("../Transit")
	overlay.vehicle_ids = PackedStringArray(["v","missing"])
	overlay.agent_id = "rider"
	overlay.refresh_debug()
	check(overlay._label.text.contains("seats 0/2") and overlay._label.text.contains("queue [rider]"),"vehicle diagnostic")
	check(overlay._label.text.contains("waiting_for_service") and overlay._label.text.contains("missing: unavailable"),"agent and invalid vehicle")
	check(transit.journey("rider").state == "queued","overlay is read-only")
	print("Runtime diagnostic overlay: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	parent.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
