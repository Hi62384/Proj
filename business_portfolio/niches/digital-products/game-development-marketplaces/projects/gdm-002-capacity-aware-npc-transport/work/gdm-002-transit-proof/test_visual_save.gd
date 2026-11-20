extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var original = load("res://ledger_view.tscn").instantiate()
	original.automatic = false
	root.add_child(original)
	for i in range(5):
		original.advance_demo(0.1)
	var saved = original.demo_snapshot()
	var file = FileAccess.open("user://demo-state.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://demo-state.dat", FileAccess.READ)
	var loaded = file.get_var()
	file.close()
	var resumed = load("res://ledger_view.tscn").instantiate()
	resumed.automatic = false
	root.add_child(resumed)
	check(resumed.restore_demo(loaded), "restore while actors moving")
	check(resumed.demo_snapshot() == saved, "snapshot equality after restore")
	var invalid = saved.duplicate(true)
	invalid.actors.npc00.speed = -1.0
	var before = resumed.demo_snapshot()
	check(not resumed.restore_demo(invalid) and resumed.demo_snapshot() == before, "invalid actor data rejected without mutation")
	for i in range(1500):
		original.advance_demo(0.1)
		resumed.advance_demo(0.1)
	check(original.demo_snapshot() == resumed.demo_snapshot(), "identical complete replay")
	var complete := 0
	for passenger in resumed.schedule.passengers.values():
		if passenger.state == "completed":
			complete += 1
	check(complete == 20, "all complete after restore")
	print("Visual save and replay: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; completed ", complete, ")")
	original.queue_free()
	resumed.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
