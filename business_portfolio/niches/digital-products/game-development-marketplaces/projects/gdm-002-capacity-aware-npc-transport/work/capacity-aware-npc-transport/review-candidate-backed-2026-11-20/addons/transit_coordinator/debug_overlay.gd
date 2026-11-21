extends CanvasLayer

# Optional local diagnostic display. It does not mutate coordinator state.
@export var coordinator_path: NodePath
@export var vehicle_ids: PackedStringArray = []
@export var agent_id := ""
@export_range(0.1, 10.0, 0.1) var refresh_seconds := 0.5
var _label: Label
var _elapsed := 0.0

func _ready() -> void:
	_label = Label.new()
	_label.position = Vector2(16,16)
	add_child(_label)
	refresh_debug()

func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= maxf(refresh_seconds,0.1):
		_elapsed = 0.0
		refresh_debug()

func refresh_debug() -> void:
	if not is_instance_valid(_label):
		return
	var coordinator := get_node_or_null(coordinator_path)
	if coordinator == null or not coordinator.has_method("inspect_vehicle") or not coordinator.has_method("diagnose") or not coordinator.has_method("current_tick"):
		_label.text = "Transit diagnostics: not connected"
		return
	var lines := PackedStringArray(["Transit diagnostics  |  tick %d" % coordinator.current_tick()])
	for vehicle in vehicle_ids:
		var result: Dictionary = coordinator.inspect_vehicle(vehicle)
		if not result.get("ok",false):
			lines.append("%s: unavailable" % vehicle)
			continue
		var ledger: Dictionary = result.ledger
		var queue := PackedStringArray()
		for i in range(mini(10,ledger.waiting.size())):
			queue.append(ledger.waiting[i])
		var suffix := " (+%d more)" % (ledger.waiting.size()-10) if ledger.waiting.size() > 10 else ""
		lines.append("%s: seats %d/%d  queue [%s]%s" % [vehicle,ledger.claims.size()+ledger.aboard.size(),ledger.capacity,", ".join(queue),suffix])
	if not agent_id.is_empty():
		var info: Dictionary = coordinator.diagnose(agent_id)
		if info.get("ok",false):
			lines.append("%s: %s (%s), service %s" % [agent_id,info.state,info.reason,info.service])
		else:
			lines.append("%s: unknown agent" % agent_id)
	_label.text = "\n".join(lines)
