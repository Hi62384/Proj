extends SceneTree
const Fixture = preload("res://scheduled_fixture.gd")
var failures := 0
func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", message)
func _initialize() -> void:
	var original = Fixture.new()
	var checkpoints: Array = []
	for i in range(103):
		# Capture states both at departures and while passengers wait at the transfer.
		if i in [0, 1, 2, 3, 7, 20, 50]:
			checkpoints.append(original.snapshot())
		original.step()
		var occupied := {}
		for vehicle_id in original.vehicles:
			var vehicle: Dictionary = original.vehicles[vehicle_id]
			check(vehicle.aboard.size() <= vehicle.capacity, "capacity invariant")
			for id in vehicle.aboard:
				check(not occupied.has(id), "one vehicle per passenger")
				occupied[id] = vehicle_id
				check(original.passengers[id].state == "onboard" and original.passengers[id].vehicle == vehicle_id, "occupancy matches journey")
	for p in original.passengers.values():
		check(p.state == "completed", "all passengers complete transfer")
	check(original.journal.size() == 80, "each passenger boards and arrives twice")
	for snapshot in checkpoints:
		var resumed = Fixture.restore(snapshot)
		check(resumed != null, "checkpoint restores")
		if resumed != null:
			while resumed.tick < original.tick:
				resumed.step()
			check(resumed.snapshot() == original.snapshot(), "identical continuation and event trace")
	var snapshot: Dictionary = checkpoints[3]
	var file = FileAccess.open("user://gdm002-fixture-snapshot.dat", FileAccess.WRITE)
	check(file != null, "open snapshot for write")
	if file == null:
		quit(1)
		return
	file.store_var(snapshot)
	file.close()
	file = FileAccess.open("user://gdm002-fixture-snapshot.dat", FileAccess.READ)
	var restored = Fixture.restore(file.get_var())
	file.close()
	check(restored != null and restored.snapshot() == snapshot, "disk snapshot restore")
	var invalid: Dictionary = snapshot.duplicate(true)
	invalid.vehicles.A.aboard.append("npc19")
	check(Fixture.restore(invalid) == null, "invalid occupancy rejected")
	invalid = snapshot.duplicate(true)
	invalid.version = 2
	check(Fixture.restore(invalid) == null, "unsupported version rejected")
	invalid = snapshot.duplicate(true)
	invalid.vehicles.B.capacity = 99
	check(Fixture.restore(invalid) == null, "changed configuration rejected")
	print("Scheduled fixture: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", original.journal.size(), " events; ", checkpoints.size(), " replay checkpoints)")
	quit(0 if failures == 0 else 1)
