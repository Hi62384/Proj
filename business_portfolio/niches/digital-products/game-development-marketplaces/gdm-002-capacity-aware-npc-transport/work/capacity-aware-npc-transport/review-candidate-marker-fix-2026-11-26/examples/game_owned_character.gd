extends CharacterBody3D

# Example of movement owned entirely by the game, independent of transit.
# A production controller would add obstacle handling, animation and tuning.
signal motion_finished(request_id: String)
var _target := Vector3.ZERO
var _request_id := ""
var _moving := false
var speed := 3.0

func start_motion(target: Vector3, request_id: String) -> void:
	_target = target
	_request_id = request_id
	_moving = true

func stop_motion(request_id: String) -> void:
	if _moving and request_id == _request_id:
		_moving = false
		velocity.x = 0.0
		velocity.z = 0.0

func _physics_process(delta: float) -> void:
	if _moving:
		var horizontal := Vector2(_target.x - global_position.x, _target.z - global_position.z)
		var direction := horizontal.normalized() if horizontal.length() >= 0.15 else Vector2.ZERO
		velocity.x = direction.x * speed
		velocity.z = direction.y * speed
	else:
		velocity.x = 0.0
		velocity.z = 0.0
	velocity.y -= 9.8 * delta
	move_and_slide()
	if _moving and is_on_floor() and Vector2(_target.x - global_position.x, _target.z - global_position.z).length() < 0.15:
		_moving = false
		velocity.x = 0.0
		velocity.z = 0.0
		motion_finished.emit(_request_id)
