extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
var failures := 0
var movement_failures := []
var boarding_event := {}

func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var map := NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-6, 0, -3), Vector3(-6, 0, 3), Vector3(-1, 0, 3), Vector3(-1, 0, -3)])
	mesh.add_polygon(PackedInt32Array([0, 1, 2, 3]))
	var region := NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(region, mesh)
	NavigationServer3D.region_set_map(region, map)
	var floor := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(24, 0.4, 8)
	floor_shape.shape = floor_box
	floor.add_child(floor_shape)
	floor.position = Vector3.ZERO
	world.add_child(floor)
	var platform := AnimatableBody3D.new()
	var platform_shape := CollisionShape3D.new()
	var platform_box := BoxShape3D.new()
	platform_box.size = Vector3(3, 0.4, 3)
	platform_shape.shape = platform_box
	platform.add_child(platform_shape)
	platform.position = Vector3(5, 0, 0)
	world.add_child(platform)
	var body := CharacterBody3D.new()
	var body_shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	body_shape.shape = capsule
	body.add_child(body_shape)
	body.collision_layer = 2
	body.collision_mask = 1
	body.position = Vector3(-4, 0.75, 0)
	world.add_child(body)
	var navigation := NavigationAgent3D.new()
	body.add_child(navigation)
	navigation.set_navigation_map(map)
	navigation.path_desired_distance = 0.3
	navigation.target_desired_distance = 0.3
	var transit = Transit.new()
	world.add_child(transit)
	var config := {"revision":"unreachable-navigation-v1", "tick_unit":"simulation_tick", "stops":["west", "east"], "vehicles":[{"id":"lift", "capacity":1}], "services":[{"id":"out", "vehicle":"lift", "from":"west", "to":"east", "period":8, "offset":0, "duration":2, "enabled":true}]}
	check(transit.configure(config, "unreachable-navigation"), "configure coordinator")
	transit.transit_event.connect(func(event):
		if event.type == "boarding_requested":
			boarding_event = event.duplicate(true)
	)
	var adapter = Adapter.new()
	world.add_child(adapter)
	check(adapter.configure(transit) and adapter.register_agent("rider", body, navigation), "configure adapter")
	adapter.movement_failed.connect(func(_agent: String, _request_id: String, reason: String): movement_failures.append(reason))
	check(transit.request_journey("rider", "west", "east"), "request journey")
	for _frame in range(40):
		await physics_frame
	check(transit.begin_tick() and transit.open_boarding(), "open boarding")
	check(not boarding_event.is_empty(), "receive boarding request")
	if not boarding_event.is_empty():
		check(adapter.move_for_request(boarding_event, Vector3(5, 0.7, 0), func(candidate, _event): return candidate.is_on_floor() and candidate.global_position.distance_to(Vector3(5, 0.7, 0)) < 0.35, "", 1.5, 0.25, 0.6), "start navigation toward disconnected platform")
	for _frame in range(120):
		await physics_frame
		if not movement_failures.is_empty():
			break
	check(movement_failures == ["timeout"], "unreachable navigation request times out")
	check(transit.journey("rider").state == "boarding", "timeout does not acknowledge physical boarding")
	var ledger: Dictionary = transit.inspect_vehicle("lift").ledger
	check(ledger.claims.size() == 1 and ledger.aboard.is_empty(), "seat claim remains held and passenger is not aboard")
	check(Vector2(body.global_position.x - 5.0, body.global_position.z).length() > 0.5, "unreachable passenger never reaches the platform")
	check(transit.finish_tick(), "expire unconfirmed claim at departure")
	check(transit.journey("rider").state == "queued", "expired boarding request returns passenger to queue")
	print("Disconnected navigation boarding integration: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; no false boarding acknowledgment)")
	NavigationServer3D.free_rid(region)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
