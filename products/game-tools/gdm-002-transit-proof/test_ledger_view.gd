extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene = load("res://ledger_view.tscn").instantiate()
	scene.automatic = false
	root.add_child(scene)
	for i in range(1500):
		scene.advance_demo(0.1)
	var completed := 0
	var missed := 0
	for p in scene.schedule.passengers.values():
		if p.state == "completed":
			completed += 1
	for event in scene.schedule.trace:
		if event[1] == "missed":
			missed += 1
	check(completed == 20, "all passengers completed")
	check(missed >= 1, "slow mover missed and recovered")
	print("Ledger visual simulation: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; completed ", completed, "; missed ", missed, ")")
	scene.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
