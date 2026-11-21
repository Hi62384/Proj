extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
func _initialize() -> void:
	var dispatcher = Dispatcher.new()
	var first := AnimatableBody3D.new()
	var second := AnimatableBody3D.new()
	var near_route: Array[Vector3] = [Vector3(-8, 0, 0), Vector3(5, 0, 0)]
	var far_route: Array[Vector3] = [Vector3(0, 0, -8), Vector3(0, 0, 7)]
	dispatcher.reservation_radius = 4.0
	var ok: bool = dispatcher.register_vehicle("near", first, near_route, 2.0, 1)
	ok = dispatcher.register_vehicle("far", second, far_route, 2.0, 2) and ok
	var issues: Array[String] = dispatcher.footprint_clearance_issues({"near": 1.0, "far": 1.0})
	ok = ok and issues.size() == 1 and "near" in issues[0]
	ok = ok and dispatcher.footprint_clearance_issues({"near": 0.25, "far": 1.0}).is_empty()
	ok = ok and dispatcher.footprint_clearance_issues({"near": 0.25}).size() == 1
	ok = ok and dispatcher.footprint_clearance_issues({"near": -1.0, "far": 1.0}).size() == 1
	dispatcher.free()
	first.free()
	second.free()
	print("Temporary game footprint clearance: ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
