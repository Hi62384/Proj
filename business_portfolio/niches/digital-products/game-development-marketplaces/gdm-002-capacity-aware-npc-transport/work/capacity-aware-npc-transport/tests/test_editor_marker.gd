extends SceneTree
const Marker = preload("res://addons/transit_coordinator/editor/stop_marker.gd")
func _initialize() -> void:
	var marker = Marker.new()
	marker.stop_id = "hub"
	var ok: bool = marker.stop_id == "hub" and marker is Node3D
	marker.free()
	print("Editor marker data: ","PASS" if ok else "FAIL")
	quit(0 if ok else 1)
