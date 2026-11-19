extends Node3D

# Original synthetic visual demonstration. Vehicle motion and recovery are
# illustrative; a game supplies its own navigation and movement controllers.
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const ARRIVAL_WINDOW := 0.5
const BOARD_WINDOW := 0.7
const TRAVEL_WINDOW := 0.6
const ACTION_TIME := 0.3
var automatic := true
var paused := false
var transit
var people := {}
var platforms := {}
var actions := {}
var rides := {}
var returns := {}
var phase := "arrivals"
var elapsed := 0.0
var visual_tick := 0
var status: Label
var message: Label
var _config := {}

func config() -> Dictionary:
	return {"revision":"demo-v1", "tick_unit":"simulation_tick", "stops":["origin","hub","end"],
		"vehicles":[{"id":"a","capacity":3},{"id":"b","capacity":2}],
		"services":[
			{"id":"a-out","vehicle":"a","from":"origin","to":"hub","period":4,"offset":0,"duration":2,"enabled":true},
			{"id":"b-fast","vehicle":"b","from":"hub","to":"end","period":8,"offset":3,"duration":2,"enabled":true},
			{"id":"b-backup","vehicle":"b","from":"hub","to":"end","period":8,"offset":7,"duration":2,"enabled":true}]}

func stop_x(stop: String) -> float:
	return -6.0 if stop == "origin" else (0.0 if stop == "hub" else 6.0)

func queue_position(id: String, stop: String) -> Vector3:
	var index := int(id.substr(3))
	return Vector3(stop_x(stop) + float(index / 5) * 0.36 - 0.55, 0.55, float(index % 5) * 0.62 - 0.2)

func make_box(size: Vector3, color: Color) -> MeshInstance3D:
	var box := BoxMesh.new()
	box.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	var mesh := MeshInstance3D.new()
	mesh.mesh = box
	mesh.material_override = material
	return mesh

func add_button(bar: HBoxContainer, title: String, callback: Callable) -> void:
	var button := Button.new()
	button.text = title
	button.pressed.connect(callback)
	bar.add_child(button)

func _ready() -> void:
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(0, 12, 18)
	camera.fov = 36
	camera.look_at(Vector3.ZERO)
	camera.current = true
	var light := DirectionalLight3D.new()
	add_child(light)
	light.rotation_degrees = Vector3(-60,-30,0)
	for stop in ["origin","hub","end"]:
		var station := make_box(Vector3(2.2,0.2,5.0), Color.SLATE_GRAY)
		add_child(station)
		station.position = Vector3(stop_x(stop),0,0)
	for id in ["a","b"]:
		var platform := make_box(Vector3(1.7,0.3,1.5), Color.CORNFLOWER_BLUE if id == "a" else Color.CORAL)
		add_child(platform)
		platform.position = Vector3(-6 if id == "a" else 0,0.25,-1.4)
		platforms[id] = platform
	for i in range(20):
		var id := "npc%02d" % i
		var marker := Node3D.new()
		marker.add_child(make_box(Vector3(0.3,0.65,0.3), Color.from_hsv(0.12 + float(i % 5) * 0.025,0.85,1.0)))
		add_child(marker)
		marker.position = queue_position(id,"origin")
		people[id] = marker
	var overlay := CanvasLayer.new()
	add_child(overlay)
	var panel := VBoxContainer.new()
	panel.position = Vector2(20,14)
	overlay.add_child(panel)
	status = Label.new()
	status.add_theme_font_size_override("font_size",20)
	panel.add_child(status)
	var bar := HBoxContainer.new()
	panel.add_child(bar)
	add_button(bar,"Pause / resume",toggle_pause)
	add_button(bar,"Disable B-fast",disable_service)
	add_button(bar,"Enable B-fast",enable_service)
	add_button(bar,"Save",save_to_disk)
	add_button(bar,"Load",load_from_disk)
	message = Label.new()
	message.text = "Synthetic local demo: movement is illustrative, not vehicle physics."
	panel.add_child(message)
	transit = Transit.new()
	add_child(transit)
	transit.transit_event.connect(on_transit_event)
	_config = config()
	if not transit.configure(_config,"demo"):
		message.text = "Configuration error: " + transit.last_error
		set_process(false)
		return
	for id in people:
		transit.request_journey(id,"origin","end")
	transit.begin_tick()
	update_visuals()

func on_transit_event(event: Dictionary) -> void:
	if event.type in ["boarding_requested","alighting_requested","recovery_requested"]:
		var target := Vector3.ZERO
		if event.type == "boarding_requested":
			var index := int(event.agent.substr(3))
			target = platforms[event.details.vehicle].position + Vector3(float(index % 3) * 0.35 - 0.35,0.7,0)
		elif event.type == "alighting_requested":
			target = queue_position(event.agent,event.details.stop)
		else:
			if event.details.safe_stops.is_empty():
				message.text = "No safe stop available for " + event.agent
				return
			target = queue_position(event.agent,event.details.safe_stops[0])
		actions[event.agent] = {"event":event.duplicate(true), "start":people[event.agent].position, "target":target, "elapsed":0.0}
	elif event.type == "departed":
		returns.erase(event.details.vehicle)
		var service: String = event.details.service
		var from_stop := "origin" if service == "a-out" else "hub"
		var to_stop := "hub" if service == "a-out" else "end"
		rides[event.agent] = {"vehicle":event.details.vehicle, "service":service, "from":from_stop, "to":to_stop, "start":event.tick, "due":event.details.arrival_tick}
	elif event.type in ["alighted","recovered","journey_failed","journey_cancelled"]:
		var old_ride: Dictionary = rides.get(event.agent, {})
		rides.erase(event.agent)
		if not old_ride.is_empty():
			var vehicle: String = old_ride.vehicle
			var occupied := false
			for remaining in rides.values():
				if remaining.vehicle == vehicle:
					occupied = true
			if not occupied:
				returns[vehicle] = {"start":platforms[vehicle].position, "target":Vector3(stop_x(old_ride.from),0.25,-1.4), "elapsed":0.0}

func advance(delta: float) -> void:
	# Return empty vehicles visibly between outbound services; this animation is
	# supplied by the demo, not a routing or physics feature of the coordinator.
	for vehicle in returns.keys().duplicate():
		var trip: Dictionary = returns[vehicle]
		trip.elapsed += delta
		platforms[vehicle].position = trip.start.lerp(trip.target, minf(trip.elapsed,1.0))
		if trip.elapsed >= 1.0:
			returns.erase(vehicle)
	for id in actions.keys().duplicate():
		var action: Dictionary = actions[id]
		action.elapsed += delta
		people[id].position = action.start.lerp(action.target, minf(action.elapsed / ACTION_TIME,1.0))
		if action.elapsed >= ACTION_TIME:
			actions.erase(id)
			var e: Dictionary = action.event
			var accepted := false
			if e.type == "boarding_requested":
				accepted = transit.acknowledge_boarding(id,e.details.vehicle,e.details.token,e.id)
			elif e.type == "alighting_requested":
				accepted = transit.acknowledge_alighting(id,e.details.vehicle,e.details.token,e.id)
			else:
				accepted = transit.acknowledge_recovery(id,e.details.vehicle,e.details.token,e.id,e.details.safe_stops[0])
			if not accepted:
				message.text = "Movement acknowledgment rejected for " + id
	elapsed += delta
	if phase == "arrivals" and elapsed >= ARRIVAL_WINDOW:
		elapsed = 0.0
		phase = "boarding"
		transit.open_boarding()
	elif phase == "boarding" and elapsed >= BOARD_WINDOW:
		elapsed = 0.0
		phase = "travel"
		transit.finish_tick()
	elif phase == "travel" and elapsed >= TRAVEL_WINDOW:
		elapsed = 0.0
		visual_tick += 1
		phase = "arrivals"
		transit.begin_tick()
	update_visuals()

func _process(delta: float) -> void:
	if automatic and not paused:
		advance(minf(delta,0.1))

func update_visuals() -> void:
	var fraction: float = elapsed / TRAVEL_WINDOW if phase == "travel" else 0.0
	for id in rides:
		var ride: Dictionary = rides[id]
		var progress := clampf((float(visual_tick) + fraction - float(ride.start)) / float(ride.due - ride.start),0.0,1.0)
		platforms[ride.vehicle].position = Vector3(lerpf(stop_x(ride.from),stop_x(ride.to),progress),0.25,-1.4)
	for id in rides:
		if not actions.has(id):
			var ride: Dictionary = rides[id]
			var index := int(id.substr(3))
			people[id].position = platforms[ride.vehicle].position + Vector3(float(index % 3) * 0.35 - 0.35,0.7,0)
	var counts := {"queued":0,"onboard":0,"completed":0,"stranded":0,"failed":0}
	for id in people:
		var p: Dictionary = transit.journey(id)
		if counts.has(p.get("state")):
			counts[p.state] += 1
	status.text = "PASSENGER TRANSIT  |  tick %d  |  waiting %d  |  riding %d  |  complete %d  |  recovery %d  |  failed %d\nBlue: origin → hub   •   Coral: hub → destination   •   20 passengers" % [transit.current_tick(),counts.queued,counts.onboard,counts.completed,counts.stranded,counts.failed]

	status.text += "\n" + vehicle_status("a") + "   |   " + vehicle_status("b")

func vehicle_status(id: String) -> String:
	var result: Dictionary = transit.inspect_vehicle(id)
	if not result.ok:
		return id.to_upper() + ": unavailable"
	var ledger: Dictionary = result.ledger
	var waiting := PackedStringArray()
	for i in range(mini(4,ledger.waiting.size())):
		waiting.append(ledger.waiting[i])
	var suffix := " …" if ledger.waiting.size() > 4 else ""
	return "%s seats %d/%d, queue [%s%s]" % [id.to_upper(),ledger.claims.size()+ledger.aboard.size(),ledger.capacity,", ".join(waiting),suffix]

func toggle_pause() -> void:
	paused = not paused
	message.text = "Paused." if paused else "Running."

func disable_service() -> void:
	message.text = "B-fast disabled; recovery and rerouting requested." if transit.set_service_enabled("b-fast",false) else "Disable is available between ticks."

func enable_service() -> void:
	message.text = "B-fast enabled." if transit.set_service_enabled("b-fast",true) else "Enable is available between ticks."

func demo_snapshot() -> Dictionary:
	var saved: Dictionary = transit.save_snapshot()
	if not saved.ok:
		return saved
	var positions := {}
	var platform_positions := {}
	for id in people:
		positions[id] = people[id].position
	for id in platforms:
		platform_positions[id] = platforms[id].position
	return {"ok":true,"version":1,"core":saved.snapshot,"phase":phase,"elapsed":elapsed,"visual_tick":visual_tick,"actions":actions.duplicate(true),"rides":rides.duplicate(true),"returns":returns.duplicate(true),"positions":positions,"platform_positions":platform_positions,"paused":paused}

func restore_demo(data: Dictionary) -> bool:
	# This example accepts only snapshots created by this trusted local demo.
	if data.get("version") != 1 or not data.get("core") is Dictionary or data.get("phase") not in ["arrivals","boarding","travel"] or not data.get("elapsed") is float or not data.get("visual_tick") is int or not data.get("actions") is Dictionary or not data.get("rides") is Dictionary or not data.get("returns") is Dictionary or not data.get("positions") is Dictionary or not data.get("platform_positions") is Dictionary or not data.get("paused") is bool:
		return false
	if data.positions.size() != people.size() or data.platform_positions.size() != platforms.size():
		return false
	for id in people:
		if not data.positions.get(id) is Vector3:
			return false
	for id in platforms:
		if not data.platform_positions.get(id) is Vector3:
			return false
	if not transit.restore_snapshot(_config,data.core):
		return false
	phase = data.phase
	elapsed = data.elapsed
	visual_tick = data.visual_tick
	actions = data.actions.duplicate(true)
	rides = data.rides.duplicate(true)
	returns = data.returns.duplicate(true)
	paused = data.paused
	for id in people:
		people[id].position = data.positions[id]
	for id in platforms:
		platforms[id].position = data.platform_positions[id]
	update_visuals()
	return true

func save_to_disk() -> void:
	var saved := demo_snapshot()
	if not saved.ok:
		message.text = "Save unavailable during event dispatch."
		return
	var file := FileAccess.open("user://transit-demo.dat", FileAccess.WRITE)
	if file == null:
		message.text = "Could not write local demo save."
		return
	file.store_var(saved)
	file.close()
	message.text = "Saved locally."

func load_from_disk() -> void:
	var file := FileAccess.open("user://transit-demo.dat", FileAccess.READ)
	if file == null:
		message.text = "No local demo save found."
		return
	var saved = file.get_var(false)
	file.close()
	message.text = "Loaded local save." if saved is Dictionary and restore_demo(saved) else "Local save could not be restored."

