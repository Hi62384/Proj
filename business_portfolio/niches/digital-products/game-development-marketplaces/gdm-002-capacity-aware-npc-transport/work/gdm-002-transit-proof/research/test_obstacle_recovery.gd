extends SceneTree
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var barrier := StaticBody3D.new()
	var barrier_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(1, 2, 1)
	barrier_shape.shape = box
	barrier.add_child(barrier_shape)
	world.add_child(barrier)
	var map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var nav := NavigationMesh.new()
	var coords := [-4.0, -0.8, 0.8, 4.0]
	var vertices := PackedVector3Array()
	for z in coords:
		for x in coords:
			vertices.append(Vector3(x,0,z))
	nav.vertices = vertices
	for z in range(3):
		for x in range(3):
			if x == 1 and z == 1:
				continue
			var i := z * 4 + x
			nav.add_polygon(PackedInt32Array([i, i+4, i+5, i+1]))
	var region = NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(region, nav)
	NavigationServer3D.region_set_map(region, map)
	for i in range(60):
		await physics_frame
	var first_trace: Array = []
	for mode in ["ledger", "diy"]:
		var model = Candidate.new(1) if mode == "ledger" else DIY.new(1)
		check(model.begin_tick(), "open " + mode)
		var people: Dictionary = model.passengers if mode == "ledger" else model.people
		check(model.acknowledge_board("A", "npc00", people.npc00.token), "board " + mode)
		check(model.finish_tick() and model.disrupt_final_leg(), "disrupt " + mode)
		var body := CharacterBody3D.new()
		var collider := CollisionShape3D.new()
		var sphere := SphereShape3D.new()
		sphere.radius = 0.15
		collider.shape = sphere
		body.add_child(collider)
		var agent := NavigationAgent3D.new()
		agent.path_desired_distance = 0.12
		agent.target_desired_distance = 0.2
		body.add_child(agent)
		world.add_child(body)
		body.global_position = Vector3(3,0,0)
		agent.set_navigation_map(map)
		# Control check: a direct approach must be physically stopped by the barrier.
		for i in range(60):
			await physics_frame
			body.velocity = Vector3.LEFT * 4.0
			body.move_and_slide()
		check(body.global_position.x > 0.6, "solid barrier blocks straight route " + mode)
		body.global_position = Vector3(3,0,0)
		agent.target_position = Vector3(-3,0,0)
		var max_z := 0.0
		var frames := 0
		while frames < 600:
			await physics_frame
			var next := agent.get_next_path_position()
			if agent.is_navigation_finished():
				break
			body.velocity = body.global_position.direction_to(next) * 4.0
			body.move_and_slide()
			max_z = maxf(max_z, absf(body.global_position.z))
			frames += 1
		check(body.global_position.distance_to(Vector3(-3,0,0)) < 0.35, "reached safe point " + mode)
		check(max_z > 0.7, "took a route around the obstacle " + mode)
		check(people.npc00.state == "stranded", "seat held until safe point " + mode)
		check(model.acknowledge_rescue("npc00", people.npc00.token), "rescue acknowledgment " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "matching event trace")
		print(mode, " obstacle recovery: ", frames, " frames; max lateral offset ", max_z)
		body.queue_free()
		await process_frame
	NavigationServer3D.free_rid(region)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	print("Obstacle recovery comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)
