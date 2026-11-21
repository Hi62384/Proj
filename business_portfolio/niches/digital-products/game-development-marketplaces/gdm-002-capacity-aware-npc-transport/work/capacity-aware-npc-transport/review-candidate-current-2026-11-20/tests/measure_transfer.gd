extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0

func _initialize() -> void:
	var cfg := {"revision":"transfer-measure-v1", "tick_unit":"simulation_tick", "stops":["origin","hub","end"], "vehicles":[{"id":"a","capacity":3},{"id":"b","capacity":2}], "services":[{"id":"a-out","vehicle":"a","from":"origin","to":"hub","period":4,"offset":0,"duration":2,"enabled":true},{"id":"b-out","vehicle":"b","from":"hub","to":"end","period":5,"offset":3,"duration":2,"enabled":true}]}
	var create_samples := []
	var tick_samples := []
	var max_tick := 0
	var tick_counts := []
	for repetition in range(6):
		var made = Core.create(cfg,"transfer-measure")
		if not made.ok:
			failures += 1
			continue
		var core = made.coordinator
		var start := Time.get_ticks_usec()
		for index in range(20):
			if not core.request_journey("npc%02d" % index,"origin","end").ok:
				failures += 1
		var request_time := Time.get_ticks_usec() - start
		core.drain_events()
		start = Time.get_ticks_usec()
		var ticks := 0
		var peak := 0
		while ticks < 160:
			var tick_start := Time.get_ticks_usec()
			if not core.begin_tick(): failures += 1
			var arrivals: Array = core.drain_events().filter(func(e): return e.type == "alighting_requested")
			arrivals.reverse()
			for event in arrivals:
				if not core.acknowledge_alighting(event.agent,event.details.vehicle,event.details.token,event.id): failures += 1
			core.drain_events()
			if not core.open_boarding(): failures += 1
			var boarding: Array = core.drain_events().filter(func(e): return e.type == "boarding_requested")
			boarding.reverse()
			for event in boarding:
				if not core.acknowledge_boarding(event.agent,event.details.vehicle,event.details.token,event.id): failures += 1
			core.drain_events()
			if not core.finish_tick(): failures += 1
			core.drain_events()
			ticks += 1
			peak = maxi(peak, Time.get_ticks_usec() - tick_start)
			var complete := 0
			for index in range(20):
				if core.journey("npc%02d" % index).state == "completed": complete += 1
			if complete == 20: break
		for index in range(20):
			if core.journey("npc%02d" % index).state != "completed": failures += 1
		if repetition > 0:
			create_samples.append(request_time)
			tick_samples.append(Time.get_ticks_usec() - start)
			tick_counts.append(ticks)
			max_tick = maxi(max_tick,peak)
	print("Transfer timing: request_us=",create_samples," sequence_us=",tick_samples," ticks=",tick_counts," max_tick_us=",max_tick)
	print("Transfer measurement: ", "PASS" if failures == 0 else "FAIL", " (",failures," failures)")
	quit(0 if failures == 0 else 1)
