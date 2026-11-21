extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var failures := 0
var events: Array = []
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var body := CharacterBody3D.new()
	world.add_child(body)
	body.position = Vector3(-1,0,0)
	var platform := AnimatableBody3D.new()
	world.add_child(platform)
	var transit = Transit.new()
	world.add_child(transit)
	transit.transit_event.connect(func(e): events.append(e))
	var config := {"revision":"physics-adapter-v1","tick_unit":"simulation_tick","stops":["origin","end"],"vehicles":[{"id":"lift","capacity":1}],"services":[{"id":"out","vehicle":"lift","from":"origin","to":"end","period":10,"offset":0,"duration":2,"enabled":true}]}
	check(transit.configure(config,"physics"),"configure")
	check(transit.request_journey("rider","origin","end"),"request")
	check(transit.begin_tick() and transit.open_boarding(),"open boarding")
	var boarding: Dictionary = {}
	for e in events:
		if e.type == "boarding_requested": boarding = e
	check(not boarding.is_empty(),"boarding requested")
	if boarding.is_empty():
		quit(1)
		return
	# This adapter drives a real CharacterBody3D using physics-frame movement.
	# Acknowledge only once the body has reached the actual platform position.
	for i in range(60):
		await physics_frame
		var delta := platform.global_position - body.global_position
		body.velocity = (delta * 6.0).limit_length(6.0)
		body.move_and_slide()
	check(body.global_position.distance_to(platform.global_position) < 0.1,"physical boarding reached platform")
	check(transit.acknowledge_boarding("rider","lift",boarding.details.token,boarding.id),"acknowledge boarding")
	check(transit.finish_tick(),"depart")
	# A moving platform adapter carries the passenger as the platform translates.
	# This tests explicit carry logic; it does not claim collision-based parenting.
	for i in range(60):
		await physics_frame
		var next := Vector3(5.0 * float(i+1)/60.0,0,0)
		var shift := next - platform.global_position
		platform.global_position = next
		body.velocity = shift / (1.0/60.0)
		body.move_and_slide()
	check(body.global_position.distance_to(platform.global_position) < 0.15,"body carried with platform")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"advance travel tick")
	check(transit.begin_tick(),"arrive")
	var alighting: Dictionary = {}
	for e in events:
		if e.type == "alighting_requested": alighting = e
	check(not alighting.is_empty(),"alighting requested")
	if not alighting.is_empty():
		for i in range(60):
			await physics_frame
			body.velocity = ((Vector3(6,0,0) - body.global_position) * 6.0).limit_length(6.0)
			body.move_and_slide()
		check(body.global_position.distance_to(Vector3(6,0,0)) < 0.1,"body reached end stop")
		check(transit.acknowledge_alighting("rider","lift",alighting.details.token,alighting.id),"acknowledge alighting")
	check(transit.journey("rider").state == "completed","journey completed")
	print("CharacterBody3D integration: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; explicit moving-platform carry)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)

