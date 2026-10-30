"""Fixed owner-popup action: start/reuse the controller and display its dashboard."""
import sys
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from bridge.client import ControllerClient
client=ControllerClient();client.ensure();client.request('bridge_open_dashboard');client.close()
