extends RefCounted
# Small demo adapter; the caller must invoke recover_missed after the window closes.
var mover: Node3D
var schedule
var vehicle := ""
var origin := Vector3.ZERO
var recovering := false

func _init(node: Node3D, service, vehicle_id: String) -> void:
	mover = node
	schedule = service
	vehicle = vehicle_id
	mover.reached.connect(_on_reached)

func begin_boarding(target: Vector3) -> void:
	origin = mover.position
	recovering = false
	mover.move_to(target, schedule.passengers[mover.agent_id].token)

func recover_missed() -> bool:
	if schedule.passengers[mover.agent_id].state != "waiting":
		return false
	recovering = true
	mover.move_to(origin, -1)
	return true

func _on_reached(id: String, token: int) -> void:
	if recovering:
		recovering = false
		return
	if not schedule.acknowledge_board(vehicle, id, token):
		# A late callback cannot board. The caller must select a safe recovery target.
		pass
