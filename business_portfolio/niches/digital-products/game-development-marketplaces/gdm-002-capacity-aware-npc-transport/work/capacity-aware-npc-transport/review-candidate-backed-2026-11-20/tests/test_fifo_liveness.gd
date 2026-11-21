extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		if failures <= 20: printerr("FAIL: ",label)
func _initialize() -> void:
	var cfg := {"revision":"fifo-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":3}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var core = Core.create(cfg,"fifo").coordinator
	var expected := []
	for i in range(101):
		var id := "npc%03d" % i
		expected.append(id)
		check(core.request_journey(id,"a","b").ok,"request " + id)
	core.drain_events()
	var boarding := []
	for t in range(100):
		check(core.begin_tick(),"begin")
		for event in core.drain_events():
			if event.type == "alighting_requested":
				check(core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id),"alight")
		core.drain_events()
		check(core.open_boarding(),"open")
		for event in core.drain_events():
			if event.type == "boarding_requested":
				boarding.append(event.agent)
				check(core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id),"board")
		core.drain_events()
		check(core.finish_tick(),"finish")
		core.drain_events()
	check(boarding == expected,"FIFO preserved across departures")
	for id in expected: check(core.journey(id).state == "completed","completed " + id)
	print("Finite FIFO liveness: ","PASS" if failures == 0 else "FAIL"," (",failures," failures; 101 agents; no disruptions)")
	quit(0 if failures == 0 else 1)
