extends Node

func _ready():
	print("GDM-003 loaded: ", GDExtensionManager.is_extension_loaded("res://addons/fixture/fixture.gdextension"))
	get_tree().quit()
