@tool
extends EditorPlugin
const StopGizmo = preload("res://addons/transit_coordinator/editor/stop_gizmo.gd")
var _gizmo: EditorNode3DGizmoPlugin

func _enter_tree() -> void:
	_gizmo = StopGizmo.new()
	add_node_3d_gizmo_plugin(_gizmo)

func _exit_tree() -> void:
	if _gizmo != null:
		remove_node_3d_gizmo_plugin(_gizmo)
		_gizmo = null
