extends SceneTree
const Original = preload("res://scheduled_fixture.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func initial_state() -> Dictionary:
	var queue: Array = []
	for i in range(20):
		queue.append("npc%02d" % i)
	return {"tick": 0, "queues": {"A": queue, "B": []}, "aboard": {"A": [], "B": []}, "completed": [], "trace": []}
func step(s: Dictionary) -> void:
	var t: int = s.tick
	# This intentionally independent minimal FIFO baseline models only the fixed trace.
	for v in ["A", "B"]:
		var period := 4 if v == "A" else 5
		var offset := 0 if v == "A" else 2
		if t % period == (offset + 1) % period:
			for id in s.aboard[v]:
				s.trace.append([t, "arrive", v, id])
				if v == "A":
					s.queues.B.append(id)
				else:
					s.completed.append(id)
			s.aboard[v].clear()
	for v in ["A", "B"]:
		var period := 4 if v == "A" else 5
		var offset := 0 if v == "A" else 2
		var capacity := 3 if v == "A" else 2
		if t % period == offset:
			while not s.queues[v].is_empty() and s.aboard[v].size() < capacity:
				var id = s.queues[v].pop_front()
				s.aboard[v].append(id)
				s.trace.append([t, "board", v, id])
	s.tick += 1
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-1,0,-1), Vector3(-1,0,1), Vector3(1,0,1), Vector3(1,0,-1)])
	mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var regions: Array = []
	var links: Array = []
	for i in range(3):
		var region = NavigationServer3D.region_create()
		NavigationServer3D.region_set_navigation_mesh(region, mesh)
		NavigationServer3D.region_set_transform(region, Transform3D(Basis.IDENTITY, Vector3(i*6,0,0)))
		NavigationServer3D.region_set_map(region, map)
		regions.append(region)
	for i in range(2):
		var link = NavigationServer3D.link_create()
		NavigationServer3D.link_set_start_position(link, Vector3(i*6+0.8,0,0))
		NavigationServer3D.link_set_end_position(link, Vector3((i+1)*6-0.8,0,0))
		NavigationServer3D.link_set_map(link, map)
		links.append(link)
	for i in range(60):
		await physics_frame
	var path = NavigationServer3D.map_get_path(map, Vector3.ZERO, Vector3(12,0,0), true)
	check(not path.is_empty() and path[path.size()-1].distance_to(Vector3(12,0,0)) < 0.1, "native path reaches third stop")
	var baseline = initial_state()
	for i in range(3):
		step(baseline)
	var saved = baseline.duplicate(true)
	var file = FileAccess.open("user://native-baseline.dat", FileAccess.WRITE)
	file.store_var(saved)
	file.close()
	file = FileAccess.open("user://native-baseline.dat", FileAccess.READ)
	var restored: Dictionary = file.get_var()
	file.close()
	for i in range(100):
		step(baseline)
		step(restored)
	var original = Original.new()
	for i in range(103):
		original.step()
	check(baseline.trace == original.journal, "same 80-event trace")
	check(restored == baseline, "mid-ride disk restore continuation")
	check(baseline.completed.size() == 20, "twenty completed")
	for rid in links + regions:
		NavigationServer3D.free_rid(rid)
	NavigationServer3D.free_rid(map)
	print("Native FIFO baseline: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; ", baseline.trace.size(), " events)")
	quit(0 if failures == 0 else 1)
