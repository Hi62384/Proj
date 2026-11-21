extends SceneTree
const Core = preload("res://addons/transit_coordinator/core/journey_coordinator.gd")
var failures := 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ",label)
func _initialize() -> void:
	var cfg := {"revision":"destroyed-v1","tick_unit":"simulation_tick","stops":["a","b"],"vehicles":[{"id":"v","capacity":1}],"services":[{"id":"s","vehicle":"v","from":"a","to":"b","period":2,"offset":0,"duration":1,"enabled":true}]}
	for stage in ["queued","boarding","boarding_confirmed","onboard","stranded"]:
		var core = Core.create(cfg,"destroyed").coordinator
		check(core.request_journey("rider","a","b").ok,"request " + stage)
		var stale: Dictionary = {}
		if stage != "queued":
			check(core.begin_tick() and core.open_boarding(),"board window " + stage)
			stale = core.pending_request("rider")
		if stage in ["boarding_confirmed","onboard","stranded"]:
			check(core.acknowledge_boarding("rider","v",stale.details.token,stale.id),"board " + stage)
		if stage in ["onboard","stranded"]:
			check(core.finish_tick(),"depart " + stage)
		if stage == "stranded":
			check(core.set_service_enabled("s",false),"disable")
			stale = core.pending_request("rider")
		check(core.remove_destroyed_agent("rider"),"remove " + stage)
		check(core.journey("rider").state == "cancelled","cancelled " + stage)
		var ledger: Dictionary = core.snapshot().ledgers.v
		check(ledger.waiting.is_empty() and ledger.claims.is_empty() and ledger.aboard.is_empty(),"seat released " + stage)
		check(not core.remove_destroyed_agent("rider"),"duplicate rejected " + stage)
		check(Core.restore(cfg,core.snapshot()).ok,"snapshot restores " + stage)
		if not stale.is_empty():
			check(not core.acknowledge_boarding("rider","v",stale.details.token,stale.id),"stale board rejected " + stage)
	print("Explicit destroyed-agent cleanup: ","PASS" if failures == 0 else "FAIL"," (",failures," failures)")
	quit(0 if failures == 0 else 1)
