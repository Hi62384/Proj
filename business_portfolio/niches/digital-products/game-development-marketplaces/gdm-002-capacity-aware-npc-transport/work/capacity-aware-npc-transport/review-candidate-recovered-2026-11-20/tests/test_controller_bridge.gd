extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Bridge = preload("res://addons/transit_coordinator/controller_bridge.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node.new()
	root.add_child(world)
	var transit = Transit.new()
	var bridge = Bridge.new()
	world.add_child(transit)
	world.add_child(bridge)
	var cfg := {"revision":"bridge-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":3,"offset":0,"duration":1,"enabled":true}]}
	var requests := []
	var withdrawn := []
	var results := []
	bridge.movement_requested.connect(func(event): requests.append(event))
	bridge.request_withdrawn.connect(func(agent,id,reason): withdrawn.append([agent,id,reason]))
	bridge.movement_result.connect(func(agent,id,ok): results.append([agent,id,ok]))
	check(transit.configure(cfg,"bridge") and bridge.configure(transit),"configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(),"boarding")
	check(requests.size() == 1 and requests[0].type == "boarding_requested","forward request")
	var first: Dictionary = requests[0]
	check(not bridge.complete_movement(first,func(_event): return false),"false arrival does not acknowledge")
	check(not bridge.complete_movement(first,func(_event): return "truthy"),"nonboolean arrival rejected")
	var forged := first.duplicate(true)
	forged.details.token += 1
	check(not bridge.complete_movement(forged,func(_event): return true),"modified event rejected")
	check(transit.journey("rider").state == "boarding","seat still a claim")
	check(transit.finish_tick(),"miss departure")
	check(withdrawn.size() == 1 and withdrawn[0] == ["rider",first.id,"ended"],"expired request withdrawn")
	check(not bridge.complete_movement(first,func(_event): return true),"old event rejected")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"advance")
	check(transit.begin_tick() and transit.open_boarding() and transit.finish_tick(),"advance two")
	check(transit.begin_tick() and transit.open_boarding(),"next departure")
	var second: Dictionary = requests.back()
	check(second.id != first.id,"new request")
	check(bridge.complete_movement(second,func(_event): return true),"verified boarding")
	check(results.size() == 1 and results[0] == ["rider",second.id,true],"result signal")
	check(not bridge.complete_movement(second,func(_event): return true),"duplicate completion rejected")
	check(transit.finish_tick() and transit.begin_tick(),"arrive")
	var exit: Dictionary = requests.back()
	check(exit.type == "alighting_requested","alighting forwarded")
	var saved: Dictionary = transit.save_snapshot()
	var restored = Transit.new()
	var new_bridge = Bridge.new()
	world.add_child(restored)
	world.add_child(new_bridge)
	check(restored.restore_snapshot(cfg,saved.snapshot) and new_bridge.configure(restored),"restore")
	var revived := []
	new_bridge.movement_requested.connect(func(event): revived.append(event))
	check(new_bridge.refresh_request("rider") and revived.size() == 1 and revived[0].id == exit.id,"recover pending request")
	check(new_bridge.refresh_request("rider") and revived.size() == 1,"refresh deduplicates")
	check(new_bridge.complete_movement(revived[0],func(_event): return true),"complete restored exit")
	check(restored.journey("rider").state == "completed","completed")
	var changing = Transit.new()
	var changing_bridge = Bridge.new()
	world.add_child(changing)
	world.add_child(changing_bridge)
	check(changing.configure(cfg,"reentrant") and changing_bridge.configure(changing),"reentrant setup")
	var changing_requests := []
	changing_bridge.movement_requested.connect(func(event): changing_requests.append(event))
	check(changing.request_journey("other","a","b") and changing.begin_tick() and changing.open_boarding(),"reentrant boarding")
	check(not changing_bridge.complete_movement(changing_requests[0],func(_event):
		changing.cancel_journey("other")
		return true
	),"cancel during arrival callback cannot acknowledge")
	check(changing.journey("other").state == "cancelled","reentrant cancellation preserved")
	var disrupted = Transit.new()
	var disruption_bridge = Bridge.new()
	world.add_child(disrupted)
	world.add_child(disruption_bridge)
	check(disrupted.configure(cfg,"disrupted") and disruption_bridge.configure(disrupted),"disruption setup")
	var observed := []
	var stale := []
	disruption_bridge.movement_requested.connect(func(event): observed.append(event))
	disruption_bridge.request_withdrawn.connect(func(agent,id,reason): stale.append([agent,id,reason]))
	check(disrupted.request_journey("person","a","b") and disrupted.begin_tick() and disrupted.open_boarding(),"disruption boarding")
	check(disruption_bridge.complete_movement(observed.back(),func(_event): return true) and disrupted.finish_tick(),"disruption departure")
	check(disrupted.set_service_enabled("s",false),"service disabled")
	var old_recovery: Dictionary = observed.back()
	check(old_recovery.type == "recovery_requested","recovery forwarded")
	check(disrupted.set_service_enabled("s",true),"service re-enabled")
	var new_recovery: Dictionary = observed.back()
	check(new_recovery.id != old_recovery.id and stale.back() == ["person",old_recovery.id,"superseded"],"recovery superseded")
	check(not disruption_bridge.complete_movement(old_recovery,func(_event): return true,"a"),"stale recovery rejected")
	check(disruption_bridge.complete_movement(new_recovery,func(_event): return true,"a"),"current recovery acknowledged")
	check(disrupted.journey("person").state == "queued","recovered passenger replans")
	print("Game-owned controller bridge: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
