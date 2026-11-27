@tool
extends EditorNode3DGizmoPlugin
const Marker = preload("res://addons/transit_coordinator/editor/stop_marker.gd")

func _init() -> void:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color(0.2, 0.8, 1.0, 1.0)
	add_material("stop", material)

func _get_gizmo_name() -> String:
	return "Transit stop marker"

func _has_gizmo(node: Node3D) -> bool:
	return node.get_script() == Marker

func _redraw(gizmo: EditorNode3DGizmo) -> void:
	gizmo.clear()
	var lines := PackedVector3Array([
		Vector3(-0.5,0,0),Vector3(0.5,0,0),
		Vector3(0,0,-0.5),Vector3(0,0,0.5),
		Vector3(0,0,0),Vector3(0,0.8,0),
		Vector3(-0.5,0,0),Vector3(0,0,0.5),
		Vector3(0,0,0.5),Vector3(0.5,0,0),
		Vector3(0.5,0,0),Vector3(0,0,-0.5),
		Vector3(0,0,-0.5),Vector3(-0.5,0,0)])
	gizmo.add_lines(lines,get_material("stop"))
