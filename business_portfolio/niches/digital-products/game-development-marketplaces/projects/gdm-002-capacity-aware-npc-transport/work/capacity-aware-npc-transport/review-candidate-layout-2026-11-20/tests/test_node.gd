extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var node
var ids: Array = []
var dispatch_save_blocked := false
var dispatch_transition_blocked := false
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func on_event(event: Dictionary) -> void:
	ids.append(event.id)
	if event.type == "boarding_requested":
		dispatch_save_blocked = not node.save_snapshot().ok
		dispatch_transition_blocked = not node.finish_tick()
		check(node.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id), "synchronous board")
	elif event.type == "alighting_requested":
		check(node.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id), "synchronous alight")
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	node = Transit.new()
	root.add_child(node)
	node.transit_event.connect(on_event)
	var config = {"revision":"node-v1", "tick_unit":"simulation_tick", "stops":["one","two"],
		"vehicles":[{"id":"v","capacity":1}],
		"services":[{"id":"s","vehicle":"v","from":"one","to":"two","period":3,"offset":0,"duration":1,"enabled":true}]}
	check(node.configure(config,"node-run"), "configure")
	check(node.request_journey("person","one","two"), "request")
	var view: Dictionary = node.inspect_vehicle("v")
	check(view.ok and view.ledger.waiting == ["person"] and view.ledger.capacity == 1,"inspect FIFO queue")
	view.ledger.waiting.clear()
	check(node.inspect_vehicle("v").ledger.waiting == ["person"],"inspection cannot mutate ledger")
	check(not node.inspect_vehicle("missing").ok,"unknown vehicle handled")
	for i in range(3):
		check(node.begin_tick(), "begin")
		check(node.open_boarding(), "open")
		check(node.finish_tick(), "finish")
	check(node.journey("person").state == "completed", "node completes journey")
	check(dispatch_save_blocked and dispatch_transition_blocked, "no partial save or phase change during signals")
	for i in range(ids.size()):
		check(ids[i] == "node-run|" + str(i+1), "event ordering")
	var snapshot = node.save_snapshot()
	check(snapshot.ok, "save outside dispatch")
	var bad = snapshot.snapshot.duplicate(true)
	bad.graph_fingerprint = "wrong"
	check(not node.restore_snapshot(config,bad) and node.journey("person").state == "completed", "failed restore preserves live state")
	check(node.restore_snapshot(config,snapshot.snapshot), "node restore")
	print("Godot node interface: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", ids.size(), " events)")
	node.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
