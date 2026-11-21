extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var packed = load("res://demo/transit_demo.tscn")
	var original = packed.instantiate()
	original.automatic = false
	root.add_child(original)
	original.transit.transit_event.connect(func(event):
		if event.type == "boarding_requested":
			var expected_x: float = -6.0 if event.details.service == "a-out" else 0.0
			check(absf(original.platforms[event.details.vehicle].position.x - expected_x) < 0.01, "vehicle at boarding stop: " + event.id)
	)
	for i in range(7):
		original.advance(0.1)
	check(original.phase == "boarding" and not original.actions.is_empty(), "save during visible boarding")
	var saved = original.demo_snapshot()
	check(saved.ok, "save scene")
	var file = FileAccess.open("user://demo-replay-test.dat",FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://demo-replay-test.dat",FileAccess.READ)
	var disk = file.get_var(false)
	file.close()
	var restored = packed.instantiate()
	restored.automatic = false
	root.add_child(restored)
	check(restored.restore_demo(disk), "load scene")
	check(original.demo_snapshot() == restored.demo_snapshot(), "exact scene restore")
	for i in range(1400):
		original.advance(0.1)
		restored.advance(0.1)
	check(original.demo_snapshot() == restored.demo_snapshot(), "identical scene replay")
	for id in original.people:
		check(original.transit.journey(id).state == "completed", "passenger completed " + id)
	print("3D demo replay: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; 20 passengers)")
	original.queue_free()
	restored.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
