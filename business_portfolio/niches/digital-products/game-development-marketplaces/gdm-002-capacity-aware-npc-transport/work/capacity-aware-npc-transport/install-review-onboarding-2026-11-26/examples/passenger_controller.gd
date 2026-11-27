extends CharacterBody3D
signal motion_finished(request_id: String)
var target := Vector3.ZERO
var request_id := ""
var moving := false
var speed := 3.0
func start_motion(destination: Vector3, id: String) -> void:
	target = destination
	request_id = id
	moving = true
func stop_motion(id: String) -> void:
	if moving and id == request_id:
		moving = false
		velocity.x = 0.0
		velocity.z = 0.0
func _physics_process(delta: float) -> void:
	var difference := Vector2(target.x - global_position.x, target.z - global_position.z)
	var direction := difference.normalized() if moving and difference.length() >= 0.15 else Vector2.ZERO
	velocity.x = direction.x * speed
	velocity.z = direction.y * speed
	velocity.y -= 9.8 * delta
	move_and_slide()
	if moving and is_on_floor() and Vector2(target.x - global_position.x, target.z - global_position.z).length() < 0.15:
		moving = false
		velocity.x = 0.0
		velocity.z = 0.0
		motion_finished.emit(request_id)
