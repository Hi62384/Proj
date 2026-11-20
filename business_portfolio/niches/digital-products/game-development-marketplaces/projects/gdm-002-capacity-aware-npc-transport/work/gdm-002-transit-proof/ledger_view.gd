extends Node3D
# A deliberately bounded visualization of the ledger-backed callback schedule.
const Schedule = preload("res://callback_schedule.gd")
const Mover = preload("res://fixture_mover.gd")
const Recovery = preload("res://fixture_recovery_adapter.gd")
const BOARD_SECONDS := 1.0
const TRAVEL_SECONDS := 0.7
var schedule = Schedule.new()
var movers := {}
var adapters := {}
var platforms := {}
var initial_speed := {}
var phase := "boarding"
var elapsed := 0.0
var trace_cursor := 0
var status: Label
var automatic := true

func cube(size: Vector3, color: Color) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	var shape := BoxMesh.new()
	shape.size = size
	instance.mesh = shape
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	instance.material_override = material
	return instance

func stop_x(leg: String) -> float:
	return -6.0 if leg == "A" else 0.0

func queue_position(id: String, x: float) -> Vector3:
	var index := int(id.substr(3))
	return Vector3(x + float(index / 5) * 0.32 - 0.5, 0.55, float(index % 5) * 0.6 - 0.1)

func _ready() -> void:
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(0, 12, 17)
	camera.fov = 35
	camera.look_at(Vector3.ZERO)
	camera.current = true
	var light := DirectionalLight3D.new()
	add_child(light)
	light.rotation_degrees = Vector3(-60, -30, 0)
	var overlay := CanvasLayer.new()
	add_child(overlay)
	status = Label.new()
	status.position = Vector2(24, 20)
	status.add_theme_font_size_override("font_size", 20)
	overlay.add_child(status)
	for x in [-6, 0, 6]:
		var station = cube(Vector3(2, 0.2, 5), Color.SLATE_GRAY)
		add_child(station)
		station.position = Vector3(x, 0, 0)
	for vehicle in ["A", "B"]:
		var platform = cube(Vector3(1.6, 0.3, 1.6), Color.CORNFLOWER_BLUE if vehicle == "A" else Color.CORAL)
		add_child(platform)
		platform.position = Vector3(stop_x(vehicle), 0.3, -1.5)
		platforms[vehicle] = platform
	for id in schedule.passengers:
		var mover = Mover.new()
		add_child(mover)
		mover.agent_id = id
		mover.position = queue_position(id, -6.0)
		mover.speed = 8.0
		# One intentionally slow passenger misses the first departure.
		if id == "npc00":
			mover.speed = 0.3
		mover.add_child(cube(Vector3(0.35, 0.7, 0.35), Color.GOLD))
		movers[id] = mover
		adapters[id] = {"A": Recovery.new(mover, schedule, "A"), "B": Recovery.new(mover, schedule, "B")}
	begin_window()
	update_view()

func begin_window() -> void:
	schedule.begin_tick()
	# Arrival events place riders at a deterministic queue location on the destination platform.
	while trace_cursor < schedule.trace.size():
		var event: Array = schedule.trace[trace_cursor]
		trace_cursor += 1
		if event[1] == "arrive":
			var x := 0.0 if event[2] == "A" else 6.0
			movers[event[3]].position = queue_position(event[3], x)
	for vehicle in ["A", "B"]:
		platforms[vehicle].position = Vector3(stop_x(vehicle), 0.3, -1.5)
		if schedule.tick % Schedule.CONFIG[vehicle].period == Schedule.CONFIG[vehicle].offset:
			for id in schedule.ledgers[vehicle].reserved:
				adapters[id][vehicle].begin_boarding(Vector3(stop_x(vehicle), 0.7, -1.5))

func advance_demo(delta: float) -> void:
	for mover in movers.values():
		mover.advance(delta)
	elapsed += delta
	if phase == "boarding" and elapsed >= BOARD_SECONDS:
		schedule.finish_tick()
		for id in schedule.passengers:
			var p: Dictionary = schedule.passengers[id]
			if p.state == "waiting" and movers[id].moving:
				adapters[id][p.leg].recover_missed()
				movers[id].speed = 8.0
		phase = "travel"
		elapsed = 0.0
	elif phase == "travel" and elapsed >= TRAVEL_SECONDS:
		phase = "boarding"
		elapsed = 0.0
		begin_window()
	update_view()

func _process(delta: float) -> void:
	if automatic:
		advance_demo(delta)

func update_view() -> void:
	var completed := 0
	var missed := 0
	for p in schedule.passengers.values():
		if p.state == "completed":
			completed += 1
	for event in schedule.trace:
		if event[1] == "missed":
			missed += 1
	status.text = "LEDGER TRANSFER PROOF  |  tick %d  |  completed %d / 20  |  missed %d\nBlue: first leg     Coral: second leg     Gold: passengers" % [schedule.tick, completed, missed]
	for vehicle in ["A", "B"]:
		var moving: bool = phase == "travel" and not schedule.ledgers[vehicle].aboard.is_empty()
		var fraction: float = minf(elapsed / TRAVEL_SECONDS, 1.0) if moving else 0.0
		platforms[vehicle].position = Vector3(stop_x(vehicle) + 6.0 * fraction, 0.3, -1.5)
		for id in schedule.ledgers[vehicle].aboard:
			var seat: int = schedule.ledgers[vehicle].aboard.find(id)
			movers[id].position = platforms[vehicle].position + Vector3(float(seat - 1) * 0.42, 0.7, 0)

func demo_snapshot() -> Dictionary:
	var actors := {}
	for id in movers:
		var m = movers[id]
		actors[id] = {"position": m.position, "target": m.target, "speed": m.speed, "command_id": m.command_id, "moving": m.moving,
			"origins": {"A": adapters[id].A.origin, "B": adapters[id].B.origin},
			"recovering": {"A": adapters[id].A.recovering, "B": adapters[id].B.recovering}}
	return {"version": 1, "schedule": schedule.snapshot(), "phase": phase, "elapsed": elapsed, "trace_cursor": trace_cursor, "actors": actors}

func restore_demo(data: Dictionary) -> bool:
	if data.get("version") != 1 or not data.get("schedule") is Dictionary or not data.get("actors") is Dictionary:
		return false
	if data.get("phase") not in ["boarding", "travel"] or not (data.get("elapsed") is float or data.get("elapsed") is int):
		return false
	if data.elapsed < 0 or data.elapsed >= (BOARD_SECONDS if data.phase == "boarding" else TRAVEL_SECONDS):
		return false
	var restored = Schedule.restore(data.schedule)
	if restored == null or (data.phase == "boarding" and restored.phase != "boarding") or (data.phase == "travel" and restored.phase != "ready"):
		return false
	if not data.get("trace_cursor") is int or data.trace_cursor < 0 or data.trace_cursor > restored.trace.size():
		return false
	if data.actors.size() != movers.size() or restored.passengers.size() != movers.size():
		return false
	for id in movers:
		if not data.actors.has(id) or not restored.passengers.has(id) or not data.actors[id] is Dictionary:
			return false
		var a: Dictionary = data.actors[id]
		if not a.get("position") is Vector3 or not a.get("target") is Vector3 or not a.get("speed") is float or a.speed <= 0.0 or not a.get("command_id") is int or not a.get("moving") is bool:
			return false
		if not a.get("origins") is Dictionary or not a.get("recovering") is Dictionary:
			return false
		for vehicle in ["A", "B"]:
			if not a.origins.get(vehicle) is Vector3 or not a.recovering.get(vehicle) is bool:
				return false
	# No state changes occur until the entire trusted local snapshot has been checked.
	schedule = restored
	phase = data.phase
	elapsed = data.elapsed
	trace_cursor = data.trace_cursor
	for id in movers:
		var mover = movers[id]
		var a: Dictionary = data.actors[id]
		for vehicle in ["A", "B"]:
			mover.reached.disconnect(Callable(adapters[id][vehicle], "_on_reached"))
		mover.position = a.position
		mover.target = a.target
		mover.speed = a.speed
		mover.command_id = a.command_id
		mover.moving = a.moving
		adapters[id] = {"A": Recovery.new(mover, schedule, "A"), "B": Recovery.new(mover, schedule, "B")}
		for vehicle in ["A", "B"]:
			adapters[id][vehicle].origin = a.origins[vehicle]
			adapters[id][vehicle].recovering = a.recovering[vehicle]
	update_view()
	return true
