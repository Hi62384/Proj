extends SceneTree
const Adapter = preload("res://research/adapter_diy.gd")
func _initialize() -> void:
	var a = Adapter.new()
	var ok = a.begin()
	var request: Array = a.requests("A")[0]
	ok = a.board("A", request[0], request[1]) and ok
	ok = a.depart() and a.disrupt() and ok
	var token = a.token("npc00")
	var saved = a.save()
	ok = a.restore(saved) and ok
	ok = a.state("npc00") == "stranded" and a.rescue("npc00", token) and ok
	ok = a.state("npc00") == "failed" and a.trace().size() == 3 and ok
	print("DIY adapter contract: ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
