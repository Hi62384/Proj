extends SceneTree
const Transit = preload("res://addons/transit_coordinator/transit_coordinator.gd")
const Adapter = preload("res://addons/transit_coordinator/navigation_adapter.gd")
class IncompleteCoordinator extends Node:
	signal transit_event(event)
	func pending_request(_id): return {}
	func acknowledge_boarding(_agent, _vehicle, _token, _event): return true
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var body := CharacterBody3D.new()
	world.add_child(body)
	var navigation := NavigationAgent3D.new()
	body.add_child(navigation)
	var transit = Transit.new()
	world.add_child(transit)
	var adapter = Adapter.new()
	world.add_child(adapter)
	var incomplete := IncompleteCoordinator.new()
	world.add_child(incomplete)
	check(not adapter.configure(incomplete), "reject incomplete coordinator")
	adapter.set_physics_process(false)
	var cfg := {"revision":"adapter-safety-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	var events := []
	var failures_seen := []
	transit.transit_event.connect(func(e): events.append(e))
	adapter.movement_failed.connect(func(_agent,_id,reason): failures_seen.append(reason))
	check(transit.configure(cfg,"adapter") and adapter.configure(transit) and adapter.register_agent("rider",body,navigation),"configure")
	check(transit.request_journey("rider","a","b") and transit.begin_tick() and transit.open_boarding(),"boarding window")
	var event: Dictionary = {}
	for item in events:
		if item.type == "boarding_requested": event = item
	check(not event.is_empty(),"request received")
	check(adapter.move_for_request(event,Vector3.ZERO,func(_body,_event): return false,"",2.0,0.4,0.1),"start unverified move")
	adapter._physics_process(0.2)
	check(failures_seen == ["timeout"],"timeout reported")
	check(transit.journey("rider").state == "boarding","unverified arrival did not acknowledge")
	check(not adapter.move_for_request(event,Vector3(NAN,0,0),func(_body,_event): return true),"nonfinite target rejected")
	check(adapter.move_for_request(event,Vector3.ZERO,func(_body,_event):
		adapter.cancel_movement("rider")
		return true
	),"start reentrant cancellation")
	adapter._physics_process(0.01)
	check(transit.journey("rider").state == "boarding","cancelled callback did not acknowledge")
	check(transit.finish_tick(),"close boarding")
	check(transit.journey("rider").state == "queued","claim expired")
	check(not adapter.move_for_request(event,Vector3.ZERO,func(_body,_event): return true),"stale request rejected before movement")
	check(failures_seen == ["timeout"],"no movement started for stale request")
	check(transit.journey("rider").state == "queued","stale request leaves journey queued")
	var fresh = Transit.new()
	var fresh_adapter = Adapter.new()
	world.add_child(fresh)
	world.add_child(fresh_adapter)
	fresh_adapter.set_physics_process(false)
	var fresh_events := []
	var fresh_failures := []
	fresh.transit_event.connect(func(e): fresh_events.append(e))
	fresh_adapter.movement_failed.connect(func(_agent,_id,reason): fresh_failures.append(reason))
	check(fresh.configure(cfg,"fresh") and fresh_adapter.configure(fresh) and fresh_adapter.register_agent("other",body,navigation), "configure callback lifecycle test")
	check(fresh.request_journey("other","a","b") and fresh.begin_tick() and fresh.open_boarding(), "fresh boarding request")
	var fresh_event: Dictionary = fresh_events.back()
	check(fresh_adapter.move_for_request(fresh_event,Vector3.ZERO,func(_body,_event): return 1,"",2.0,0.4,0.1), "start nonboolean arrival check")
	fresh_adapter._physics_process(0.2)
	check(fresh_failures == ["timeout"] and fresh.journey("other").state == "boarding", "truthy nonboolean does not acknowledge")
	check(fresh_adapter.move_for_request(fresh_event,Vector3.ZERO,func(_body,_event):
		fresh.free()
		return true
	), "start removal callback")
	body.velocity.x = 1.0
	fresh_adapter._physics_process(0.01)
	check(fresh_failures == ["timeout", "agent_or_coordinator_missing"], "coordinator removal reports failure")
	check(body.velocity.x == 0.0, "coordinator removal stops movement")
	print("Navigation adapter safety: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	world.queue_free()
	await process_frame
	quit(0 if failures == 0 else 1)
