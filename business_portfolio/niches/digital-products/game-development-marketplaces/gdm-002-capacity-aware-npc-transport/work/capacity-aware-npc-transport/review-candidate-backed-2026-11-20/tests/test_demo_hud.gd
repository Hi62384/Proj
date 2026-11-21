extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		if failures <= 10: printerr("FAIL: ",label)
func shown(text: String, label: String) -> int:
	var regex := RegEx.new()
	regex.compile(label + " ([0-9]+)")
	var match_result := regex.search(text)
	return -1 if match_result == null else int(match_result.get_string(1))
func check_counts(demo) -> void:
	var expected := {"waiting":0,"riding":0,"complete":0,"recovery":0,"failed":0,"cancelled":0}
	for id in demo.people:
		var state: String = demo.transit.journey(id).state
		if state in ["queued","boarding","boarding_confirmed"]:
			expected.waiting += 1
		elif state in ["onboard","alighting"]:
			expected.riding += 1
		elif state == "completed": expected.complete += 1
		elif state == "stranded": expected.recovery += 1
		elif state == "failed": expected.failed += 1
		elif state == "cancelled": expected.cancelled += 1
		else: check(false,"unexpected visible state " + state)
	for label in expected:
		check(shown(demo.status.text,label) == expected[label],"HUD count " + label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var demo = load("res://demo/transit_demo.tscn").instantiate()
	demo.automatic = false
	root.add_child(demo)
	check(demo.transit.cancel_journey("npc19"),"cancel one waiting passenger")
	demo.update_visuals()
	check_counts(demo)
	var saw_boarding := false
	var saw_confirmed := false
	var saw_alighting := false
	for i in range(180):
		demo.advance(0.1)
		for id in demo.people:
			var state: String = demo.transit.journey(id).state
			saw_boarding = saw_boarding or state == "boarding"
			saw_confirmed = saw_confirmed or state == "boarding_confirmed"
			saw_alighting = saw_alighting or state == "alighting"
		check_counts(demo)
	check(saw_boarding and saw_confirmed and saw_alighting,"exercised boarding, confirmation and alighting")
	print("Demo HUD state counts: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	demo.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
