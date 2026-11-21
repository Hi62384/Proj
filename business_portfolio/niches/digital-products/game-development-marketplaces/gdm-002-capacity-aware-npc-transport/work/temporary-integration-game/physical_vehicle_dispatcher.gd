extends Node

signal vehicle_arrived(vehicle_id: String)
signal vehicle_recovered(vehicle_id: String, safe_stop: Vector3)

var junctions: Array[Vector3] = [Vector3.ZERO]
var reservation_radius := 3.0
var _vehicles := {}
var _junction_owners := {}

# Advisory only; callers supply conservative planar bounding-circle radii.
func endpoint_clearance_issues() -> Array[String]:
	var issues: Array[String] = []
	if not is_finite(reservation_radius) or reservation_radius <= 0.0:
		issues.append("Reservation radius must be finite and positive")
		return issues
	for id in _vehicles:
		var route: Array[Vector3] = _vehicles[id].route
		for index in range(junctions.size()):
			if not junctions[index].is_finite():
				issues.append("Junction %d is not finite" % index)
			elif _planar_distance(route[-1], junctions[index]) <= reservation_radius + 0.5:
				issues.append("Vehicle %s ends inside junction %d release boundary" % [id, index])
	return issues

func footprint_clearance_issues(footprints: Dictionary) -> Array[String]:
	var issues := endpoint_clearance_issues()
	if not is_finite(reservation_radius) or reservation_radius <= 0.0:
		return issues
	for id in _vehicles:
		var footprint = footprints.get(id)
		if not (footprint is float or footprint is int) or not is_finite(float(footprint)) or float(footprint) <= 0.0:
			issues.append("Vehicle %s needs a finite positive footprint radius" % id)
			continue
		var route: Array[Vector3] = _vehicles[id].route
		for index in range(junctions.size()):
			if junctions[index].is_finite() and _planar_distance(route[-1], junctions[index]) <= reservation_radius + 0.5 + float(footprint):
				issues.append("Vehicle %s footprint ends inside junction %d clearance" % [id, index])
	return issues

func register_vehicle(id: String, body: AnimatableBody3D, route: Array[Vector3], speed: float, priority: int) -> bool:
	if id.is_empty() or not is_instance_valid(body) or _vehicles.has(id) or route.size() < 2 or not is_finite(speed) or speed <= 0.0:
		return false
	for point in route:
		if not point.is_finite():
			return false
	_vehicles[id] = {"body":body, "route":route.duplicate(), "speed":speed, "priority":priority, "active":false, "recovering":false, "index":1, "wait_count":0}
	return true

func dispatch(id: String) -> bool:
	if not _vehicles.has(id) or _vehicles[id].active:
		return false
	_vehicles[id].active = true
	return true

func interrupt_to_safe_stop(id: String, safe_stop: Vector3) -> bool:
	if not _vehicles.has(id) or not _vehicles[id].active or not safe_stop.is_finite():
		return false
	for junction_position in junctions:
		if _planar_distance(safe_stop, junction_position) <= reservation_radius + 0.5:
			return false
	var body: AnimatableBody3D = _vehicles[id].body
	var recovery_route: Array[Vector3] = [body.position, safe_stop]
	_vehicles[id].route = recovery_route
	_vehicles[id].index = 1
	_vehicles[id].recovering = true
	return true

func waiting_frames(id: String) -> int:
	return int(_vehicles.get(id, {}).get("wait_count", 0))

func save_snapshot() -> Dictionary:
	var saved_vehicles := {}
	for id in _vehicles:
		var vehicle: Dictionary = _vehicles[id]
		var route: Array[Vector3] = vehicle.route
		saved_vehicles[id] = {"route":route.duplicate(), "speed":vehicle.speed, "priority":vehicle.priority, "active":vehicle.active, "recovering":vehicle.recovering, "index":vehicle.index, "wait_count":vehicle.wait_count}
	var saved_junctions: Array[Vector3] = junctions.duplicate()
	return {"version":2, "junctions":saved_junctions, "reservation_radius":reservation_radius, "vehicles":saved_vehicles}

func restore_snapshot(snapshot: Dictionary) -> bool:
	if snapshot.get("version") != 2 or not snapshot.get("junctions") is Array or not snapshot.get("vehicles") is Dictionary:
		return false
	var saved_radius = snapshot.get("reservation_radius")
	if not (saved_radius is float or saved_radius is int) or not is_finite(float(saved_radius)) or float(saved_radius) <= 0.0 or float(saved_radius) != reservation_radius:
		return false
	var saved_junctions: Array = snapshot.junctions
	if saved_junctions.size() != junctions.size():
		return false
	for index in range(junctions.size()):
		if not saved_junctions[index] is Vector3 or not saved_junctions[index].is_finite() or saved_junctions[index] != junctions[index]:
			return false
	var saved_vehicles: Dictionary = snapshot.vehicles
	if saved_vehicles.size() != _vehicles.size():
		return false
	var validated := {}
	for id in _vehicles:
		if not saved_vehicles.has(id) or not saved_vehicles[id] is Dictionary:
			return false
		var entry: Dictionary = saved_vehicles[id]
		var speed_value = entry.get("speed")
		if not entry.get("route") is Array or not (speed_value is float or speed_value is int) or not entry.get("priority") is int or not entry.get("active") is bool or not entry.get("recovering") is bool or not entry.get("index") is int or not entry.get("wait_count") is int:
			return false
		var route: Array[Vector3] = []
		for point in entry.route:
			if not point is Vector3 or not point.is_finite():
				return false
			route.append(point)
		if route.size() < 2 or not is_finite(float(entry.speed)) or float(entry.speed) <= 0.0 or int(entry.index) < 1 or int(entry.index) > route.size() or int(entry.wait_count) < 0:
			return false
		if entry.active and int(entry.index) >= route.size():
			return false
		if entry.recovering and not entry.active:
			return false
		var body: Object = _vehicles[id].get("body")
		if body == null or not is_instance_valid(body):
			return false
		validated[id] = {"route":route, "speed":float(entry.speed), "priority":int(entry.priority), "active":entry.active, "recovering":entry.recovering, "index":int(entry.index), "wait_count":int(entry.wait_count)}
	for id in _vehicles:
		var entry: Dictionary = validated[id]
		_vehicles[id].route = entry.route.duplicate()
		_vehicles[id].speed = entry.speed
		_vehicles[id].priority = entry.priority
		_vehicles[id].active = entry.active
		_vehicles[id].recovering = entry.recovering
		_vehicles[id].index = entry.index
		_vehicles[id].wait_count = entry.wait_count
	_junction_owners.clear()
	return true

func _physics_process(delta: float) -> void:
	for junction_index in _junction_owners.keys().duplicate():
		var owner_id: String = _junction_owners[junction_index]
		var owner: Dictionary = _vehicles.get(owner_id, {})
		var owner_body: Object = owner.get("body")
		if owner_body == null or not is_instance_valid(owner_body) or _planar_distance(owner_body.position, junctions[junction_index]) > reservation_radius + 0.5:
			_junction_owners.erase(junction_index)
	var ids: Array = _vehicles.keys()
	ids.sort_custom(func(a: String, b: String) -> bool:
		var left_priority: int = _vehicles[a].priority
		var right_priority: int = _vehicles[b].priority
		return left_priority < right_priority if left_priority != right_priority else a < b
	)
	for id in ids:
		var vehicle: Dictionary = _vehicles[id]
		if not vehicle.active:
			continue
		var body: AnimatableBody3D = vehicle.body
		if vehicle.index >= vehicle.route.size():
			continue
		var target: Vector3 = vehicle.route[vehicle.index]
		var next_position: Vector3 = body.position.move_toward(target, float(vehicle.speed) * delta)
		var blocked := false
		var entering: Array[int] = []
		for junction_index in range(junctions.size()):
			var next_distance := _planar_distance(next_position, junctions[junction_index])
			var current_owner: String = _junction_owners.get(junction_index, "")
			if current_owner != "" and current_owner != id and next_distance <= reservation_radius + 0.5:
				blocked = true
				break
			if current_owner == "" and next_distance <= reservation_radius:
				entering.append(junction_index)
		if blocked:
			vehicle.wait_count += 1
			continue
		for junction_index in entering:
			_junction_owners[junction_index] = id
		body.position = next_position
		if body.position.distance_to(target) <= 0.02:
			vehicle.index += 1
			if vehicle.index >= vehicle.route.size():
				vehicle.active = false
				if vehicle.recovering:
					vehicle.recovering = false
					vehicle_recovered.emit(id, target)
				else:
					vehicle_arrived.emit(id)

func _planar_distance(left: Vector3, right: Vector3) -> float:
	return Vector2(left.x - right.x, left.z - right.z).length()
