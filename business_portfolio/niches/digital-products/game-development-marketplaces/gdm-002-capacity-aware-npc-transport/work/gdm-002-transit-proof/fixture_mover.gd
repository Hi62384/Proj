extends Node3D

# Minimal independently driven controller used only by the callback proof.
signal reached(agent_id: String, command_id: int)
var agent_id := ""
var target := Vector3.ZERO
var speed := 1.0
var command_id := 0
var moving := false

func move_to(destination: Vector3, new_command_id: int) -> void:
	target = destination
	command_id = new_command_id
	moving = true

func advance(delta: float) -> void:
	if not moving:
		return
	position = position.move_toward(target, speed * delta)
	if position == target:
		moving = false
		reached.emit(agent_id, command_id)
