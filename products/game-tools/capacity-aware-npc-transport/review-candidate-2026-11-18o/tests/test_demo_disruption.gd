extends SceneTree
var failures := 0
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	var disabled := false
	var recovered := [0]
	demo.transit.transit_event.connect(func(e):
		if e.type == "recovered":
			recovered[0] += 1
	)
	for i in range(1800):
		demo.advance(0.1)
		if not disabled and demo.phase == "travel":
			for ride in demo.rides.values():
				if ride.service == "b-fast":
					disabled = demo.transit.set_service_enabled("b-fast",false)
					break
	check(disabled,"disable while vehicle is in use")
	check(recovered[0] > 0,"recover onboard passenger")
	for id in demo.people:
		check(demo.transit.journey(id).state == "completed", "complete " + id)
	print("3D demo disruption: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; ",recovered[0]," recovered)")
	demo.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
