extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	var cfg := {"revision":"cancel-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":3,"offset":0,"duration":1,"enabled":true}]}
	var core = Core.create(cfg,"cancel").coordinator
	check(core.request_journey("rider","a","b").ok and core.begin_tick() and core.open_boarding(),"start")
	var boarding: Dictionary = core.pending_request("rider")
	check(core.acknowledge_boarding("rider","v",boarding.details.token,boarding.id),"board")
	check(not core.cancel_journey("rider"),"confirmed boarding cannot cancel mid-phase")
	check(core.finish_tick(),"depart")
	check(core.cancel_journey("rider"),"request onboard cancellation")
	var rescue: Dictionary = core.pending_request("rider")
	check(rescue.type == "recovery_requested" and core.journey("rider").reason == "waiting_for_cancel_recovery","safe recovery requested")
	check(not core.cancel_journey("rider") and not core.change_destination("rider","a"),"pending cancellation is stable")
	check(not core.acknowledge_recovery("rider","v",rescue.details.token,rescue.id,"invalid"),"invalid stop does not release")
	var saved: Dictionary = core.snapshot()
	check(saved.ledgers.v.aboard.size() == 1,"seat retained")
	var invalid_old = saved.duplicate(true)
	invalid_old.version = 4
	check(not Core.restore(cfg,invalid_old).ok,"version 4 cannot contain version 5 cancellation reason")
	var restored_result = Core.restore(cfg,saved)
	check(restored_result.ok,"restore cancellation")
	if restored_result.ok:
		var restored = restored_result.coordinator
		check(restored.pending_request("rider") == rescue,"restore recovery request")
		check(restored.acknowledge_recovery("rider","v",rescue.details.token,rescue.id,"a"),"safe exit")
		check(restored.journey("rider").state == "cancelled" and restored.snapshot().ledgers.v.aboard.is_empty(),"cancel after exit and release")
		check(not restored.acknowledge_recovery("rider","v",rescue.details.token,rescue.id,"a"),"duplicate rejected")
		check(Core.restore(cfg,restored.snapshot()).ok,"cancelled state restores")
	check(core.set_stop_enabled("b",false),"stop change")
	var renewed: Dictionary = core.pending_request("rider")
	check(renewed.id != rescue.id and core.journey("rider").reason == "waiting_for_cancel_recovery","cancellation survives changed availability")
	check(not core.acknowledge_recovery("rider","v",rescue.details.token,rescue.id,"a"),"superseded request rejected")
	check(core.acknowledge_recovery("rider","v",renewed.details.token,renewed.id,"a") and core.journey("rider").state == "cancelled","cancel after refreshed recovery")
	print("Onboard cancellation: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	quit(0 if failures == 0 else 1)
