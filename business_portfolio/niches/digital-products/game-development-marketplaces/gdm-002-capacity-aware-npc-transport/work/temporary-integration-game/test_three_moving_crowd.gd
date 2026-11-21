extends SceneTree
const Npc = preload("res://npc.gd")
var failures := 0
var arrived := {}
var routes := {
	"west": [Vector3(-2, 0.5, 0), Vector3(2, 0.5, 0)],
	"east": [Vector3(2, 0.5, 0), Vector3(-2, 0.5, 0)],
	"south": [Vector3(0, 0.5, -2), Vector3(0, 0.5, 2)]
}
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ", label)
func record_arrival(request_id: String, npc: CharacterBody3D) -> void:
	arrived[request_id] = npc.global_position
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var ground := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(8, 0.4, 8)
	floor_shape.shape = floor_box
	ground.add_child(floor_shape)
	ground.position.y = -0.2
	world.add_child(ground)
	var walkers := {}
	var order := ["west", "east", "south"]
	for i in range(order.size()):
		var id: String = order[i]
		var npc: CharacterBody3D = Npc.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.28
		capsule.height = 1.0
		var collision := CollisionShape3D.new()
		collision.shape = capsule
		npc.add_child(collision)
		npc.position = routes[id][0]
		npc.collision_layer = 2
		npc.collision_mask = 3
		npc.cooperative_avoidance = true
		npc.extended_avoidance = true
		npc.avoidance_priority = i + 1
		npc.reached.connect(record_arrival.bind(npc))
		world.add_child(npc)
		walkers[id] = npc
	for id in order:
		walkers[id].walk_to(routes[id][1], id + "-trip")
	for _frame in range(1200):
		await physics_frame
		if arrived.size() == 3:
			break
	check(arrived.size() == 3, "three intersecting moving walkers complete their original requests")
	for id in order:
		check(arrived.has(id + "-trip"), id + " emits its own arrival")
		check(walkers[id].is_on_floor(), id + " remains grounded")
		check(arrived.get(id + "-trip", Vector3(INF, INF, INF)).distance_to(routes[id][1]) < 0.3, id + " reports arrival at its intended endpoint")
	print("Temporary game three-moving-passenger crowd avoidance: ", "PASS" if failures == 0 else "FAIL", " (", failures, " failures; three intersecting routes)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
