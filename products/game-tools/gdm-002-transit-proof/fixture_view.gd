extends Node3D

# Visualization of the fixed synthetic fixture; movement is illustrative, not a controller adapter.
const Fixture = preload("res://scheduled_fixture.gd")
var model = Fixture.new()
var markers := {}
var vehicles := {}
var elapsed := 0.0
var status: Label
const TICK_SECONDS := 0.6

func cube(size: Vector3, color: Color) -> MeshInstance3D:
	var result := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	result.mesh = mesh
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	result.material_override = material
	add_child(result)
	return result

func _ready() -> void:
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(0, 12, 17)
	camera.fov = 35.0
	camera.look_at(Vector3(0, 0, 0))
	camera.current = true
	var overlay := CanvasLayer.new()
	add_child(overlay)
	status = Label.new()
	status.position = Vector2(24, 20)
	status.add_theme_font_size_override("font_size", 22)
	overlay.add_child(status)
	var light := DirectionalLight3D.new()
	add_child(light)
	light.rotation_degrees = Vector3(-60, -30, 0)
	for x in [-6, 0, 6]:
		var station = cube(Vector3(2, 0.2, 5), Color.SLATE_GRAY)
		station.position = Vector3(x, 0, 0)
	vehicles.A = cube(Vector3(1.6, 0.3, 1.6), Color.CORNFLOWER_BLUE)
	vehicles.B = cube(Vector3(1.6, 0.3, 1.6), Color.CORAL)
	for id in model.passengers:
		markers[id] = cube(Vector3(0.35, 0.7, 0.35), Color.GOLD)
	update_view()

func _process(delta: float) -> void:
	elapsed += delta
	while elapsed >= TICK_SECONDS:
		elapsed -= TICK_SECONDS
		model.step()
	update_view()

func update_view() -> void:
	var completed := 0
	for p in model.passengers.values():
		if p.state == "completed":
			completed += 1
	status.text = "SYNTHETIC TRANSIT FIXTURE  |  tick %d  |  completed %d / 20\nBlue: A → transfer    Coral: transfer → destination    Gold: passengers" % [model.tick, completed]
	for id in ["A", "B"]:
		var v: Dictionary = model.vehicles[id]
		var start_x: float = -6.0 if id == "A" else 0.0
		# Vehicles are at their destination during the tick after departure.
		var moving: bool = not v.aboard.is_empty()
		vehicles[id].position = Vector3(start_x + (3.0 if moving else 0.0), 0.3, -1.5)
	for id in model.passengers:
		var p: Dictionary = model.passengers[id]
		var index := int(id.substr(3))
		var x := -6.0 if p.stop == "start" else (0.0 if p.stop == "transfer" else 6.0)
		var z := float(index % 5) * 0.65 - 0.5
		if p.state == "onboard":
			markers[id].position = vehicles[p.vehicle].position + Vector3(float(index % 3) * 0.4 - 0.4, 0.6, 0)
		else:
			markers[id].position = Vector3(x + float(index / 5) * 0.4 - 0.6, 0.55, z)

