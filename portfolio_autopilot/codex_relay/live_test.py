"""Optional real inference smoke test. Never imported by the offline test suite."""
import argparse
import json
import threading

from .__main__ import InstanceLock
from .codex import Codex
from .config import Config
from .workspace import Workspace


def main():
    parser = argparse.ArgumentParser(description="Opt-in real Codex two-turn test using your ChatGPT plan")
    parser.add_argument("--approve-chatgpt-usage", action="store_true")
    parser.add_argument("--data-dir")
    args = parser.parse_args()
    if not args.approve_chatgpt_usage:
        parser.error("Explicit --approve-chatgpt-usage is required; this test consumes Codex plan usage")
    config = Config.load(args.data_dir)
    name = "codex_relay_demo.txt"
    path = config.workspace / name
    if path.exists():
        raise SystemExit("Remove or rename codex_relay_demo.txt yourself before running this optional test")
    with InstanceLock(config.data_dir):
        client = Codex(config)
        events = []
        task = {}
        def save(thread_id):
            task["thread_id"] = thread_id
            (config.data_dir / "live-test-session.json").write_text(json.dumps(task), encoding="utf-8")
        workspace = Workspace(config.workspace, [name], lambda: True, lambda *x: events.append(x), config.data_dir / "live-test-backup")
        original_thread = None
        for content in ("Hello from Codex Relay\n", "Hello again from Codex Relay\n"):
            result = client.run(task, f"Owner-approved harmless test. Use relay_workspace to write exactly {content!r} to {name}. Read existing file before changing it. Finish with kind=result.",
                                workspace, threading.Event(), lambda *x: events.append(x), save)
            if result["kind"] != "result" or not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit("Live check did not pass; inspect local files and live-test-session.json")
            if original_thread is None:
                original_thread = task['thread_id']
            elif original_thread != task['thread_id']:
                raise SystemExit('Live check failed: follow-up did not retain the original thread')
        print("PASS: real Codex wrote and corrected one test file using the same saved thread.")
        print("GitHub/ChatGPT end-to-end communication was NOT tested by this command.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print('Live test BLOCKED or FAILED; no success is claimed: ' + str(exc))
        raise SystemExit(1)
