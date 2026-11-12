"""Local chat entry point for the already-installed Windows controller."""
import argparse
import json
from pathlib import Path
import sys

from .integration import OPERATIONS


def main():
    parser = argparse.ArgumentParser(description='Connect to Portfolio Manager')
    parser.add_argument('action', choices=[name.removeprefix('portfolio_') for name in OPERATIONS])
    parser.add_argument('--folder', help='Folder under business_portfolio/niches, or its full path')
    parser.add_argument('--arguments', help='JSON arguments for worker lease operations')
    args = parser.parse_args()
    app = Path(__file__).resolve().parents[1] / 'apps' / 'codex_desktop_assistant'
    sys.path.insert(0, str(app))
    from bridge.client import ControllerClient

    data = json.loads(args.arguments) if args.arguments else {}
    if not isinstance(data, dict):
        parser.error('--arguments must be a JSON object')
    if args.folder is not None:
        data['folder'] = args.folder
    client = ControllerClient()
    try:
        health = client.ensure()
        if not health.get('portfolio_manager'):
            raise RuntimeError('Quit the older Computer Bridge from its tray menu, then open Start_Portfolio_Manager.cmd.')
        operation = 'portfolio_' + args.action
        result = client.request(operation, data)
        print(json.dumps(result, indent=2, ensure_ascii=True))
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
