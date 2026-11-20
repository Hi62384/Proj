extends CharacterBody3D
signal reached(request_id: String)
var destination := Vector3.ZERO
var active_id := ""
var walking := false
var cooperative_avoidance := false
var yielding := false
var yield_count := 0
var extended_avoidance := false
var avoidance_priority := 0
var _resume_after_yield := false
var _resume_destination := Vector3.ZERO
var _resume_active_id := ""
var _yielded_for: WeakRef
var _resume_wait := 0.0

func walk_to(point: Vector3, request_id: String) -> void:
	destination = point
	active_id = request_id
	walking = true
	yielding = false
	_resume_after_yield = false
	_resume_wait = 0.0
	_yielded_for = null

func cancel_walk(request_id: String) -> void:
	if request_id == active_id or (_resume_after_yield and request_id == _resume_active_id):
		walking = false
		yielding = false
		_resume_after_yield = false
		_resume_wait = 0.0
		_yielded_for = null

func yield_to(other: CharacterBody3D) -> void:
	if not cooperative_avoidance or yielding:
		return
	var pause_route := false
	if walking:
		var other_priority: int = other.get("avoidance_priority")
		if avoidance_priority > other_priority or (avoidance_priority == other_priority and get_instance_id() > other.get_instance_id()):
			return
		pause_route = true
	# Try both sides; remain still if the immediate path is obstructed.
	var side := 1.0 if global_position.z >= other.global_position.z else -1.0
	var options := [Vector3(0, 0, side * 1.2), Vector3(0, 0, -side * 1.2)]
	if extended_avoidance:
		options.append_array([Vector3(1.2, 0, 0), Vector3(-1.2, 0, 0), Vector3(0.85, 0, 0.85), Vector3(0.85, 0, -0.85), Vector3(-0.85, 0, 0.85), Vector3(-0.85, 0, -0.85)])
	for offset in options:
		if _can_yield(offset):
			if pause_route:
				_resume_after_yield = true
				_resume_destination = destination
				_resume_active_id = active_id
				_resume_wait = 0.0
				walking = false
			destination = global_position + offset
			yielding = true
			_yielded_for = weakref(other)
			yield_count += 1
			return

func _can_yield(offset: Vector3) -> bool:
	if test_move(global_transform, offset): return false
	for i in range(1, 5):
		var start := global_position + offset * (float(i) / 4.0) + Vector3(0, 0.2, 0)
		var query := PhysicsRayQueryParameters3D.create(start, start + Vector3(0, -1.5, 0), 1)
		if get_world_3d().direct_space_state.intersect_ray(query).is_empty(): return false
	return true

func _physics_process(delta: float) -> void:
	var difference := Vector2(destination.x - global_position.x, destination.z - global_position.z)
	var direction := difference.normalized() if (walking or yielding) and difference.length() > 0.14 else Vector2.ZERO
	if yielding and difference.length() > 0.14 and not _can_yield(Vector3(direction.x, 0, direction.y) * minf(difference.length(), 0.3)):
		yielding = false
		direction = Vector2.ZERO
	velocity.x = direction.x * 3.0
	velocity.z = direction.y * 3.0
	velocity.y -= 9.8 * delta
	move_and_slide()
	if cooperative_avoidance and walking:
		for i in range(get_slide_collision_count()):
			var other = get_slide_collision(i).get_collider()
			if other != null and other.has_method("yield_to"):
				other.yield_to(self)
	if yielding and is_on_floor() and difference.length() <= 0.14:
		yielding = false
	if _resume_after_yield and not yielding:
		_resume_wait += delta
		var other: Object = _yielded_for.get_ref() if _yielded_for != null else null
		if other == null or not is_instance_valid(other) or global_position.distance_to(other.global_position) > 1.0 or _resume_wait >= 0.75:
			destination = _resume_destination
			active_id = _resume_active_id
			walking = true
			_resume_after_yield = false
			_yielded_for = null
			_resume_wait = 0.0
	var remaining := Vector2(destination.x - global_position.x, destination.z - global_position.z)
	if walking and is_on_floor() and remaining.length() <= 0.14:
		walking = false
		reached.emit(active_id)
