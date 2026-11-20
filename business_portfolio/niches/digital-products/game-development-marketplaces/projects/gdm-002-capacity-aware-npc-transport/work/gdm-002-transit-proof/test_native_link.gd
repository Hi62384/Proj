extends SceneTree
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var map = NavigationServer3D.map_create()
	NavigationServer3D.map_set_active(map, true)
	var mesh := NavigationMesh.new()
	mesh.vertices = PackedVector3Array([Vector3(-1,0,-1), Vector3(-1,0,1), Vector3(1,0,1), Vector3(1,0,-1)])
	mesh.add_polygon(PackedInt32Array([0,1,2,3]))
	var first = NavigationServer3D.region_create()
	var second = NavigationServer3D.region_create()
	NavigationServer3D.region_set_navigation_mesh(first, mesh)
	NavigationServer3D.region_set_navigation_mesh(second, mesh)
	NavigationServer3D.region_set_transform(second, Transform3D(Basis.IDENTITY, Vector3(6,0,0)))
	NavigationServer3D.region_set_map(first, map)
	NavigationServer3D.region_set_map(second, map)
	var link = NavigationServer3D.link_create()
	NavigationServer3D.link_set_start_position(link, Vector3(0.8,0,0))
	NavigationServer3D.link_set_end_position(link, Vector3(5.2,0,0))
	NavigationServer3D.link_set_map(link, map)
	for i in range(60):
		await physics_frame
	var path = NavigationServer3D.map_get_path(map, Vector3.ZERO, Vector3(6,0,0), true)
	print("enabled path: ", path, " iteration: ", NavigationServer3D.map_get_iteration_id(map)); check(path.size() >= 2 and path[path.size()-1].distance_to(Vector3(6,0,0)) < 0.1, "native link connects separated regions")
	NavigationServer3D.link_set_enabled(link, false)
	for i in range(60):
		await physics_frame
	var disconnected = NavigationServer3D.map_get_path(map, Vector3.ZERO, Vector3(6,0,0), true)
	check(disconnected.is_empty() or disconnected[disconnected.size()-1].distance_to(Vector3(6,0,0)) > 1.0, "disabled link removes route")
	NavigationServer3D.free_rid(link)
	NavigationServer3D.free_rid(first)
	NavigationServer3D.free_rid(second)
	NavigationServer3D.free_rid(map)
	print("Native NavigationLink primitive: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures)")
	quit(0 if failures == 0 else 1)


