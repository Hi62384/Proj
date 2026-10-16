"""Strict versioned wire format. Markdown surrounding JSON is rejected."""
import hashlib
import json
import re

PREFIX = "CODEX_RELAY_V1\n"
STATUSES = ("Proposed", "Approved", "Running", "Needs ChatGPT", "Needs Owner",
            "Awaiting Review", "Completed", "Failed", "Cancelled")
TYPES = {"CODEX_PROGRESS", "CODEX_QUESTION", "CODEX_ERROR", "CODEX_RESULT",
         "CHATGPT_REPLY", "OWNER_DECISION"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def unpack(body):
    if not isinstance(body, str) or len(body) > 24000 or not body.startswith(PREFIX):
        raise ValueError("Expected CODEX_RELAY_V1 followed by JSON")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("Duplicate JSON key")
            result[k] = v
        return result
    value = json.loads(body[len(PREFIX):], object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def text(value, limit=8000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError("Invalid text field")
    return value


def task(body):
    value = unpack(body)
    keys = {"type", "task_id", "description", "priority", "requirements", "paths",
            "dependencies", "acceptance_criteria"}
    if set(value) != keys or value["type"] != "TASK":
        raise ValueError("Invalid task schema")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,63}", value["task_id"]):
        raise ValueError("Invalid task ID")
    text(value["description"])
    if value["priority"] not in ("low", "normal", "high"):
        raise ValueError("Invalid priority")
    for key in ("requirements", "paths", "dependencies", "acceptance_criteria"):
        if not isinstance(value[key], list) or len(value[key]) > 40:
            raise ValueError("Invalid list field")
        for item in value[key]:
            text(item, 1000)
    if not value["paths"] or not value["acceptance_criteria"]:
        raise ValueError("Paths and acceptance criteria are required")
    return value


def message(body):
    value = unpack(body)
    common = {"type", "task_id", "message_id", "reply_to", "scope", "action", "text"}
    if set(value) != common or value["type"] not in TYPES:
        raise ValueError("Invalid message schema")
    for key in ("task_id", "message_id", "reply_to", "scope"):
        text(value[key], 128)
    text(value["text"])
    if value["action"] not in ("continue", "pause", "cancel", "report", "decision"):
        raise ValueError("Invalid action")
    return value


def encode(value):
    return PREFIX + json.dumps(value, ensure_ascii=False, indent=2)
