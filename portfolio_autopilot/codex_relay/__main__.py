import argparse
import json
import os
import threading
import webbrowser

from .codex import Codex
from .config import Config
from .dashboard import make_server
from .github import GitHub
from .scheduler import Relay
from .store import Store


class InstanceLock:
    def __init__(self, directory):
        self.path = directory / "instance.lock"
        self.file = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a+b")
        self.file.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                self.file.close()
                raise RuntimeError("Codex Relay is already running. Use its existing dashboard.") from None
        else:
            import fcntl
            try:
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.file.close()
                raise RuntimeError("Codex Relay is already running") from None
        return self

    def __exit__(self, *args):
        self.file.close()


def main():
    parser = argparse.ArgumentParser(description="Codex Relay — local owner-approved GitHub inbox")
    parser.add_argument("command", choices=("serve", "doctor"), nargs="?", default="serve")
    parser.add_argument("--data-dir", help="Runtime directory outside the repository")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    config = Config.load(args.data_dir)
    config.save()
    with InstanceLock(config.data_dir):
        store = Store(config.data_dir)
        relay = Relay(config, store, GitHub(config, store), Codex(config))
        if args.command == "doctor":
            try:
                relay.test_connection()
                print(json.dumps(relay.connections, indent=2))
            finally:
                store.close()
            return
        try:
            server = make_server(relay)
        except OSError:
            store.close()
            raise RuntimeError("Dashboard port is busy. Check for another relay or change port in config.json") from None
        loop = threading.Thread(target=relay.loop, daemon=True)
        loop.start()
        url = f"http://127.0.0.1:{server.server_port}/#{server.relay_token}"
        print("Codex Relay is running locally. The runner starts only when you click Start runner.")
        print("Close this window or press Ctrl+C to stop. Runtime data: " + str(config.data_dir))
        if not args.no_browser:
            webbrowser.open(url)
        else:
            print("Open this private local link (do not share): " + url)
        try:
            server.serve_forever(poll_interval=.3)
        except KeyboardInterrupt:
            pass
        finally:
            relay.close()
            server.server_close()
            loop.join(timeout=25)
            if not (relay.worker and relay.worker.is_alive()):
                store.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as exc:
        print("Codex Relay: " + str(exc))
        raise SystemExit(1)
