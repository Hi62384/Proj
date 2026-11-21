extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func _initialize() -> void:
	var cfg := {"revision":"measure-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":10}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	for size in [20,100,500]:
		var samples := []
		var worst := 0
		for repetition in range(6):
			var core = Core.create(cfg,"measure").coordinator
			for i in range(size): core.request_journey("n%d" % i,"a","b")
			core.drain_events()
			var start := Time.get_ticks_usec()
			var max_tick := 0
			var count := 0
			while count < size and core.tick() < 2*size:
				var tick_start := Time.get_ticks_usec()
				core.begin_tick()
				for event in core.drain_events():
					if event.type == "alighting_requested":
						if not core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id): failures += 1
						count += 1
				core.open_boarding()
				for event in core.drain_events():
					if event.type == "boarding_requested":
						if not core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id): failures += 1
				core.finish_tick()
				core.drain_events()
				max_tick = maxi(max_tick,Time.get_ticks_usec()-tick_start)
			if count != size: failures += 1
			if repetition > 0:
				samples.append(Time.get_ticks_usec()-start)
				worst = maxi(worst,max_tick)
		print("agents=",size," total_us_five=",samples," max_tick_us=",worst)
	print("Coordinator measurement: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	quit(0 if failures == 0 else 1)
