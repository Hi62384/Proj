extends SceneTree

# Logical demonstration only: no bodies or vehicles move in this example.
# A real game must verify physical boarding and exit before acknowledging.
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
var transit
var failed := false

func require(condition: bool, label: String) -> void:
	if not condition:
		failed = true
		printerr("Quickstart failed: ", label)

func on_transit_event(event: Dictionary) -> void:
	if event.type == "boarding_requested":
		print("Simulated boarding: ", event.agent)
		require(transit.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id),"boarding acknowledgment")
	elif event.type == "alighting_requested":
		print("Simulated alighting: ", event.agent)
		require(transit.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id),"alighting acknowledgment")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	transit = Transit.new()
	root.add_child(transit)
	transit.transit_event.connect(on_transit_event)
	var config := {"revision":"quickstart-v1", "tick_unit":"simulation_tick", "stops":["origin","destination"],
		"vehicles":[{"id":"bus","capacity":1}],
		"services":[{"id":"out","vehicle":"bus","from":"origin","to":"destination","period":3,"offset":0,"duration":1,"enabled":true}]}
	require(transit.configure(config,"quickstart"),"configure")
	require(transit.request_journey("passenger","origin","destination"),"request journey")
	for tick in range(2):
		require(transit.begin_tick(),"begin tick")
		require(transit.open_boarding(),"open boarding")
		require(transit.finish_tick(),"finish tick")
	require(transit.journey("passenger").state == "completed","journey completed")
	print("Quickstart: ", "FAIL" if failed else "PASS")
	transit.queue_free()
	await process_frame
	quit(1 if failed else 0)
