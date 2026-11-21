extends SceneTree
const Original = preload("res://scheduled_fixture.gd")
const Candidate = preload("res://callback_schedule.gd")
const DIY = preload("res://research/diy_validated_baseline.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func state_for(model, mode: String) -> Dictionary:
	return model.passengers if mode == "ledger" else model.people
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-1,0,-1), Vector3(-1,0,1), Vector3(1,0,1), Vector3(1,0,-1)])
	mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var rids: Array = []
	for i in range(3):
		var region = NavigationServer3D.region_create()
		NavigationServer3D.region_set_navigation_mesh(region, mesh)
		NavigationServer3D.region_set_transform(region, Transform3D(Basis.IDENTITY, Vector3(i*6,0,0)))
		NavigationServer3D.region_set_map(region, map)
		rids.append(region)
	for i in range(2):
		var link = NavigationServer3D.link_create()
		NavigationServer3D.link_set_start_position(link, Vector3(i*6+0.8,0,0))
		NavigationServer3D.link_set_end_position(link, Vector3((i+1)*6-0.8,0,0))
		NavigationServer3D.link_set_map(link, map)
		rids.append(link)
	for i in range(60):
		await physics_frame
	var first_trace: Array = []
	for mode in ["ledger", "diy"]:
		var model = Candidate.new() if mode == "ledger" else DIY.new()
		var bodies := {}
		var agents := {}
		var moving := {}
		for id in state_for(model, mode):
			var body := CharacterBody3D.new()
			var agent := NavigationAgent3D.new()
			body.add_child(agent)
			world.add_child(body)
			agent.set_navigation_map(map)
			agent.path_desired_distance = 0.15
			agent.target_desired_distance = 0.2
			bodies[id] = body
			agents[id] = agent
			moving[id] = false
		var start_us := Time.get_ticks_usec()
		var ticks := 0
		var restored_checkpoint := false
		for t in range(100):
			# Arriving riders must physically reach the stop before the model releases them.
			for id in state_for(model, mode):
				var p: Dictionary = state_for(model, mode)[id]
				if p.state == "onboard":
					var destination := Vector3(6,0,0) if p.leg == "A" else Vector3(12,0,0)
					check(bodies[id].global_position.distance_to(destination) < 0.35, "body reached stop before model arrival " + id + " " + mode)
			check(model.begin_tick(), "begin tick " + mode)
			for vehicle in ["A", "B"]:
				var waiting: Array = model.ledgers[vehicle].reserved.duplicate() if mode == "ledger" else model.claims[vehicle].duplicate()
				for id in waiting:
					check(model.acknowledge_board(vehicle, id, state_for(model, mode)[id].token), "boarding " + id + " " + mode)
					agents[id].target_position = Vector3(6,0,0) if vehicle == "A" else Vector3(12,0,0)
					moving[id] = true
			check(model.finish_tick(), "finish tick " + mode)
			for f in range(12):
				await physics_frame
				for id in moving:
					if not moving[id]:
						continue
					var target: Vector3 = agents[id].get_next_path_position()
					if agents[id].is_navigation_finished():
						moving[id] = false
						continue
					var distance: float = bodies[id].global_position.distance_to(target)
					bodies[id].velocity = bodies[id].global_position.direction_to(target) * minf(100.0, distance * 60.0)
					bodies[id].move_and_slide()
				if t == 2 and f == 1:
					# Persist explicit controller inputs, then reconstruct bodies and navigation agents.
					var actors := {}
					var active_count := 0
					for id in bodies:
						actors[id] = {"position": bodies[id].global_position, "target": agents[id].target_position, "moving": moving[id]}
						if moving[id]:
							active_count += 1
							check(bodies[id].global_position.x > 6.1 and bodies[id].global_position.x < 11.9, "moving body is between stops " + mode)
					check(active_count > 0, "save occurs during movement " + mode)
					var saved = {"model": model.snapshot(), "actors": actors}
					var file = FileAccess.open("user://twenty-" + mode + ".dat", FileAccess.WRITE)
					file.store_var(saved)
					file.close()
					file = FileAccess.open("user://twenty-" + mode + ".dat", FileAccess.READ)
					var disk: Dictionary = file.get_var()
					file.close()
					var restored = Candidate.restore(disk.model) if mode == "ledger" else DIY.restore(disk.model)
					check(restored != null, "schedule restored " + mode)
					if restored == null:
						quit(1)
						return
					model = restored
					for body in bodies.values():
						body.queue_free()
					await process_frame
					for id in actors:
						var body := CharacterBody3D.new()
						var agent := NavigationAgent3D.new()
						body.add_child(agent)
						world.add_child(body)
						body.global_position = disk.actors[id].position
						agent.set_navigation_map(map)
						agent.path_desired_distance = 0.15
						agent.target_desired_distance = 0.2
						if disk.actors[id].moving:
							agent.target_position = disk.actors[id].target
						bodies[id] = body
						agents[id] = agent
						moving[id] = disk.actors[id].moving
					restored_checkpoint = true
			ticks += 1
			var completed := 0
			for p in state_for(model, mode).values():
				if p.state == "completed":
					completed += 1
			if completed == 20:
				break
		var final_count := 0
		for p in state_for(model, mode).values():
			if p.state == "completed":
				final_count += 1
		check(restored_checkpoint, "mid-movement reconstruction exercised " + mode)
		check(final_count == 20, "20 completed " + mode)
		check(model.trace.size() == 80, "80 events " + mode)
		var reference = Original.new()
		for i in range(103):
			reference.step()
		check(model.trace == reference.journal, "matches unrestored reference trace " + mode)
		if mode == "ledger":
			first_trace = model.trace.duplicate(true)
		else:
			check(model.trace == first_trace, "identical 20-agent trace")
		print(mode, " 20-agent navigation: ", ticks, " ticks, ", model.trace.size(), " events, ", (Time.get_ticks_usec()-start_us)/1000000.0, " seconds elapsed")
		for body in bodies.values():
			body.queue_free()
		await process_frame
	for rid in rids:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	world.queue_free()
	await process_frame
	print("20-agent navigation restore comparison: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)

