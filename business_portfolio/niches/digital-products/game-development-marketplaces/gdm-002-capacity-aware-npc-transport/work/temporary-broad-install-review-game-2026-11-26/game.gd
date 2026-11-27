extends Node3D
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
const Npc = preload("res://npc.gd")
var transit: Node
var bridge: Node
var npc: CharacterBody3D
var platform: AnimatableBody3D
var label: Label
var requests := {}
var stage := "settling"
var frames := 0
var error := ""
@export_enum("normal", "disruption") var scenario := "normal"
var restore_data := {}

func box(size: Vector3, at: Vector3, moving: bool, color: Color) -> Node3D:
	var node: Node3D = AnimatableBody3D.new() if moving else StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var volume := BoxShape3D.new()
	volume.size = size
	shape.shape = volume
	node.add_child(shape)
	var mesh := MeshInstance3D.new()
	var cube := BoxMesh.new()
	cube.size = size
	mesh.mesh = cube
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	mesh.material_override = material
	node.add_child(mesh)
	node.position = at
	add_child(node)
	return node

func _ready() -> void:
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(2.0, 9.0, 12.0)
	camera.look_at(Vector3(1.5, 0, 0))
	camera.current = true
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -30, 0)
	add_child(light)
	box(Vector3(2.2, 0.4, 3), Vector3(-2.5, 0, 0), false, Color.DIM_GRAY)
	box(Vector3(4, 0.4, 3), Vector3(5.9, 0, 0), false, Color.DIM_GRAY)
	platform = box(Vector3(3, 0.4, 3), Vector3.ZERO, true, Color.CORNFLOWER_BLUE)
	npc = Npc.new()
	var collider := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.0
	collider.shape = capsule
	npc.add_child(collider)
	var model := MeshInstance3D.new()
	var capsule_mesh := CapsuleMesh.new()
	capsule_mesh.radius = 0.25
	capsule_mesh.height = 1.0
	model.mesh = capsule_mesh
	npc.add_child(model)
	npc.position = Vector3(-2.5, 0.75, 0)
	add_child(npc)
	var ui := CanvasLayer.new()
	add_child(ui)
	label = Label.new()
	label.position = Vector2(20, 20)
	label.add_theme_font_size_override("font_size", 24)
	ui.add_child(label)
	transit = Transit.new()
	bridge = Bridge.new()
	add_child(transit)
	add_child(bridge)
	var config := {"revision":"temporary-game-v1", "tick_unit":"simulation_tick", "stops":["dock", "station"], "vehicles":[{"id":"ferry", "capacity":1}], "services":[{"id":"route", "vehicle":"ferry", "from":"dock", "to":"station", "period":10, "offset":0, "duration":2, "enabled":true}]}
	if not transit.configure(config, "temporary-game") or not bridge.configure(transit):
		fail("configuration: " + transit.last_error)
		return
	bridge.movement_requested.connect(_request_motion)
	bridge.request_withdrawn.connect(func(_agent, id, _reason): npc.cancel_walk(id))
	npc.reached.connect(_reached)
	if restore_data.is_empty():
		if not transit.request_journey("visitor", "dock", "station"): fail("journey")
	else:
		platform.position = restore_data.platform
		npc.position = restore_data.position
		npc.velocity = restore_data.velocity
		if not transit.restore_snapshot(config, restore_data.core):
			fail("restore coordinator")
			return
		stage = "recovering"
		if not bridge.refresh_request("visitor"): fail("restore recovery request")

func recovery_checkpoint() -> Dictionary:
	if stage != "recovering": return {}
	var saved: Dictionary = transit.save_snapshot()
	if not saved.ok: return {}
	return {"core":saved.snapshot, "position":npc.position, "velocity":npc.velocity, "platform":platform.position}

func fail(reason: String) -> void:
	error = reason
	stage = "failed"
	if is_instance_valid(label): label.text = "Integration failed: " + reason

func _request_motion(event: Dictionary) -> void:
	requests[event.id] = event
	var x := 0.0 if event.type == "boarding_requested" else 5.0
	npc.walk_to(Vector3(x, 0.7, 0), event.id)

func _reached(id: String) -> void:
	var event: Dictionary = requests[id]
	var x := 0.0 if event.type == "boarding_requested" else 5.0
	var safe_stop := "station" if event.type == "recovery_requested" else ""
	if not bridge.complete_movement(event, func(_event): return npc.is_on_floor() and absf(npc.position.x - x) < 0.25, safe_stop):
		fail("movement acknowledgment")

func _physics_process(delta: float) -> void:
	if stage == "failed" or stage == "completed": return
	frames += 1
	if frames > 1500:
		fail("timeout")
		return
	if stage == "settling" and frames >= 30:
		if not transit.begin_tick() or not transit.open_boarding():
			fail("open boarding")
			return
		stage = "boarding"
	elif stage == "boarding" and transit.journey("visitor").state == "boarding_confirmed":
		if not transit.finish_tick():
			fail("depart")
			return
		stage = "sailing"
	elif stage == "sailing":
		platform.position.x = minf(platform.position.x + 1.2 * delta, 2.4)
		if platform.position.x >= 2.4:
			if not npc.is_on_floor() or absf(npc.position.x - platform.position.x) > 0.6:
				fail("passenger not aboard")
				return
			if scenario == "disruption":
				if not transit.set_service_enabled("route", false):
					fail("disable service")
					return
				stage = "recovering"
			else:
				if not transit.begin_tick() or not transit.open_boarding() or not transit.finish_tick() or not transit.begin_tick():
					fail("arrive")
					return
				stage = "alighting"
	elif stage == "alighting" and transit.journey("visitor").state == "completed":
		stage = "completed"
	elif stage == "recovering" and transit.journey("visitor").state == "completed":
		stage = "completed"
	label.text = "Temporary transit game: " + stage
