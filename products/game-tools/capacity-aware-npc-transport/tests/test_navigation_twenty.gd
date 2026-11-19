extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		if failures <= 20: printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var nav_map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(nav_map,true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-1,0,-1),Vector3(-1,0,1),Vector3(1,0,1),Vector3(1,0,-1)])
	mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var rids: Array = []
	for i in range(3):
		var region = NavigationServer3D.region_create()
		NavigationServer3D.region_set_navigation_mesh(region,mesh)
		NavigationServer3D.region_set_transform(region,Transform3D(Basis.IDENTITY,Vector3(i*6,0,0)))
		NavigationServer3D.region_set_map(region,nav_map)
		rids.append(region)
	for i in range(2):
		var link = NavigationServer3D.link_create()
		NavigationServer3D.link_set_start_position(link,Vector3(i*6+0.8,0,0))
		NavigationServer3D.link_set_end_position(link,Vector3((i+1)*6-0.8,0,0))
		NavigationServer3D.link_set_map(link,nav_map)
		rids.append(link)
	var cfg := {"revision":"nav20-v1","tick_unit":"simulation_tick","stops":["origin","hub","end"],"vehicles":[{"id":"a","capacity":3},{"id":"b","capacity":2}],"services":[{"id":"a-out","vehicle":"a","from":"origin","to":"hub","period":4,"offset":0,"duration":2,"enabled":true},{"id":"b-out","vehicle":"b","from":"hub","to":"end","period":5,"offset":3,"duration":2,"enabled":true}]}
	var core = Core.create(cfg,"nav20").coordinator
	var bodies := {}
	var agents := {}
	var moving := {}
	for i in range(20):
		var id := "npc%02d" % i
		var body := CharacterBody3D.new()
		world.add_child(body)
		var nav := NavigationAgent3D.new()
		body.add_child(nav)
		nav.set_navigation_map(nav_map)
		nav.path_desired_distance = 0.15
		nav.target_desired_distance = 0.2
		bodies[id] = body
		agents[id] = nav
		moving[id] = false
		check(core.request_journey(id,"origin","end").ok,"request " + id)
	core.drain_events()
	for i in range(60): await physics_frame
	var ticks := 0
	for t in range(120):
		check(core.begin_tick(),"begin")
		for event in core.drain_events():
			if event.type == "alighting_requested":
				var destination := Vector3(6,0,0) if event.details.stop == "hub" else Vector3(12,0,0)
				check(bodies[event.agent].global_position.distance_to(destination) < 0.35,"reached stop " + event.agent)
				check(core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id),"alight")
		core.drain_events()
		check(core.open_boarding(),"open")
		for event in core.drain_events():
			if event.type == "boarding_requested":
				var origin := Vector3.ZERO if event.details.service == "a-out" else Vector3(6,0,0)
				check(bodies[event.agent].global_position.distance_to(origin) < 0.35,"at boarding stop " + event.agent)
				check(core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id),"board")
		core.drain_events()
		check(core.finish_tick(),"finish")
		for event in core.drain_events():
			if event.type == "departed":
				agents[event.agent].target_position = Vector3(6,0,0) if event.details.service == "a-out" else Vector3(12,0,0)
				moving[event.agent] = true
		for f in range(12):
			await physics_frame
			for id in moving:
				if not moving[id]: continue
				var next: Vector3 = agents[id].get_next_path_position()
				if agents[id].is_navigation_finished():
					moving[id] = false
					continue
				var distance: float = bodies[id].global_position.distance_to(next)
				bodies[id].velocity = bodies[id].global_position.direction_to(next) * minf(100.0,distance*60.0)
				bodies[id].move_and_slide()
		ticks += 1
		var complete := 0
		for id in bodies:
			if core.journey(id).state == "completed": complete += 1
		if complete == 20: break
	for id in bodies:
		check(core.journey(id).state == "completed","complete " + id)
	print("20-agent navigation and transfer: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; ",ticks," ticks; no collision shapes)")
	for rid in rids: NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(nav_map)
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
