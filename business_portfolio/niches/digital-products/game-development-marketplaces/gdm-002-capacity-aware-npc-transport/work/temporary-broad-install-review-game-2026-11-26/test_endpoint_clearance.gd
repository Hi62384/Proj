extends SceneTree
const Dispatcher = preload("res://physical_vehicle_dispatcher.gd")
func _initialize() -> void:
	var dispatcher = Dispatcher.new()
	var body := AnimatableBody3D.new()
	var inside: Array[Vector3] = [Vector3(-6, 0, 0), Vector3(4, 0, 0)]
	var outside: Array[Vector3] = [Vector3(-6, 0, 0), Vector3(5, 0, 0)]
	dispatcher.reservation_radius = 4.0
	var ok: bool = dispatcher.register_vehicle("short", body, inside, 2.0, 1)
	ok = ok and dispatcher.endpoint_clearance_issues().size() == 1
	dispatcher._vehicles.short.route = outside
	ok = ok and dispatcher.endpoint_clearance_issues().is_empty()
	dispatcher.reservation_radius = 0.0
	ok = ok and dispatcher.endpoint_clearance_issues().size() == 1
	dispatcher.free()
	body.free()
	print("Temporary game endpoint clearance: ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
