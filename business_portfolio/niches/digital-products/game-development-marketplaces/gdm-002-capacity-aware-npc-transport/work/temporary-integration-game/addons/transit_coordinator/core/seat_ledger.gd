extends RefCounted

# One authoritative simulation owner must serialize all calls to this ledger.
# Tokens are monotonic within a ledger and survive snapshots; they are not secrets.
const MAX_CAPACITY := 100000
const MAX_ENTRIES := 100000
const MAX_TOKEN := 9000000000000000000
var _capacity := 0
var _waiting: Array[String] = []
var _claims: Array[Dictionary] = []
var _aboard: Array[Dictionary] = []
var _next_token := 1

static func create(capacity: int):
	if capacity < 1 or capacity > MAX_CAPACITY:
		return null
	var ledger = load("res://addons/transit_coordinator/core/seat_ledger.gd").new()
	ledger._capacity = capacity
	return ledger

static func _valid_agent(id) -> bool:
	return id is String and not id.is_empty() and id.length() <= 128

func _contains(id: String) -> bool:
	if _waiting.has(id):
		return true
	for group in [_claims, _aboard]:
		for record in group:
			if record.agent == id:
				return true
	return false

func request(id: String) -> bool:
	if not _valid_agent(id) or _contains(id) or _waiting.size() + _claims.size() + _aboard.size() >= MAX_ENTRIES:
		return false
	_waiting.append(id)
	return true

func allocate() -> Array:
	return allocate_matching(_waiting.duplicate())

func allocate_matching(eligible: Array) -> Array:
	# FIFO among eligible waiters; other stops/services retain their queue position.
	var allowed := {}
	for id in eligible:
		if _valid_agent(id):
			allowed[id] = true
	var allocated: Array = []
	var index := 0
	while index < _waiting.size() and _claims.size() + _aboard.size() < _capacity and _next_token < MAX_TOKEN:
		if not allowed.has(_waiting[index]):
			index += 1
			continue
		var id: String = _waiting.pop_at(index)
		var record = {"agent": id, "token": _next_token}
		_next_token += 1
		_claims.append(record)
		allocated.append(record.duplicate())
	return allocated

func board(id: String, token: int) -> bool:
	for i in range(_claims.size()):
		if _claims[i].agent == id and _claims[i].token == token:
			_aboard.append(_claims.pop_at(i))
			return true
	return false

func cancel(id: String) -> bool:
	if _waiting.has(id):
		_waiting.erase(id)
		return true
	for i in range(_claims.size()):
		if _claims[i].agent == id:
			_claims.remove_at(i)
			return true
	return false

func release(id: String, token: int) -> bool:
	for i in range(_aboard.size()):
		if _aboard[i].agent == id and _aboard[i].token == token:
			_aboard.remove_at(i)
			return true
	return false

func expire_claims() -> Array:
	# Returned claims keep their original FIFO order ahead of later requests.
	var expired: Array = _claims.duplicate(true)
	var prefix: Array[String] = []
	for record in _claims:
		prefix.append(record.agent)
	prefix.append_array(_waiting)
	_waiting = prefix
	_claims.clear()
	return expired

func snapshot() -> Dictionary:
	return {"version": 1, "capacity": _capacity, "waiting": _waiting.duplicate(), "claims": _claims.duplicate(true), "aboard": _aboard.duplicate(true), "next_token": _next_token}

static func restore(data: Dictionary):
	if data.get("version") != 1 or not data.get("capacity") is int or data.capacity < 1 or data.capacity > MAX_CAPACITY or not data.get("next_token") is int or data.next_token < 1 or data.next_token > MAX_TOKEN:
		return null
	for key in ["waiting", "claims", "aboard"]:
		if not data.get(key) is Array:
			return null
	if data.claims.size() + data.aboard.size() > data.capacity or data.waiting.size() + data.claims.size() + data.aboard.size() > MAX_ENTRIES:
		return null
	var agents := {}
	var tokens := {}
	for id in data.waiting:
		if not _valid_agent(id) or agents.has(id):
			return null
		agents[id] = true
	for group in [data.claims, data.aboard]:
		for record in group:
			if not record is Dictionary or not _valid_agent(record.get("agent")) or not record.get("token") is int:
				return null
			if agents.has(record.agent) or record.token < 1 or record.token >= data.next_token or tokens.has(record.token):
				return null
			agents[record.agent] = true
			tokens[record.token] = true
	var ledger = create(data.capacity)
	ledger._waiting.assign(data.waiting)
	ledger._claims.assign(data.claims.duplicate(true))
	ledger._aboard.assign(data.aboard.duplicate(true))
	ledger._next_token = data.next_token
	return ledger
