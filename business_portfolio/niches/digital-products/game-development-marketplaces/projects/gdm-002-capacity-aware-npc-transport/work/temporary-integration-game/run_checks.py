"""Run this temporary game's integration checks with isolated Godot user data."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
godot = Path(sys.argv[1]).resolve(strict=True)
cases = {'test_game.gd': 'Temporary game integration: PASS',
         'test_disruption.gd': 'Temporary game disruption: PASS',
         'test_disruption_world_restore.gd': 'Temporary game full scene recovery restore: PASS',
         'test_multi_game.gd': 'Temporary game two-passenger contention: PASS',
         'test_passenger_blocking.gd': 'Temporary game passenger blocking: PASS',
         'test_dispatch_requeue.gd': 'Temporary game dispatch requeue: PASS',
         'test_auto_avoidance.gd': 'Temporary game cooperative avoidance: PASS',
         'test_late_demand.gd': 'Temporary game late-demand dispatch: PASS',
         'test_demand_return.gd': 'Temporary game demand-triggered return: PASS',
         'test_alternate_yield.gd': 'Temporary game alternate-side avoidance: PASS',
         'test_no_safe_yield.gd': 'Temporary game blocked avoidance: PASS',
         'test_no_floor_yield.gd': 'Temporary game unsupported yield rejection: PASS',
         'test_two_routes.gd': 'Temporary game two-route dispatch: PASS',
         'test_extended_avoidance.gd': 'Temporary game extended avoidance: PASS',
         'test_yield_floor_gap.gd': 'Temporary game sampled-floor gap: PASS',
         'test_yield_new_obstacle.gd': 'Temporary game yield interrupted by obstacle: PASS',
         'test_seeded_dispatch.gd': 'Temporary game seeded multi-vehicle dispatch: PASS',
         'test_parallel_vehicles.gd': 'Temporary game parallel physical vehicles: PASS',
         'test_parallel_disruption.gd': 'Temporary game parallel vehicle disruption: PASS',
         'test_three_passenger_avoidance.gd': 'Temporary game three-passenger avoidance: PASS'}
cases['test_moving_crowd.gd'] = 'Temporary game moving crowd avoidance: PASS'
cases['test_mapped_physical_dispatch.gd'] = 'Temporary game event-mapped physical dispatch: PASS'
cases['test_moving_crowd_cancel.gd'] = 'Temporary game crowd sidestep cancellation: PASS'
cases['test_three_moving_crowd.gd'] = 'Temporary game three-moving-passenger crowd avoidance: PASS'
cases['test_mapped_dispatch_recovery.gd'] = 'Temporary game mapped physical dispatch recovery: PASS'
cases['test_four_moving_crowd.gd'] = 'Temporary game four-moving-passenger crowd avoidance: PASS'
cases['test_crossing_vehicle_dispatch.gd'] = 'Temporary game crossing-vehicle dispatch: PASS'
cases['test_multi_junction_dispatch.gd'] = 'Temporary game multi-junction dispatch: PASS'
cases['test_junction_interruption_recovery.gd'] = 'Temporary game junction interruption recovery: PASS'
cases['test_coordinator_junction_dispatch.gd'] = 'Temporary game coordinator-driven junction dispatch: PASS'
cases['test_generated_junction_layouts.gd'] = 'Temporary game generated junction layouts: PASS'
cases['test_junction_crossing_restore.gd'] = 'Temporary game junction crossing reconstruction: PASS'
cases['test_capacity_two_crossing_restore.gd'] = 'Temporary game capacity-two crossing reconstruction: PASS'
cases['test_navigation_unreachable.gd'] = 'Disconnected navigation boarding integration: PASS'
cases['test_seeded_physical_dispatch.gd'] = 'Temporary game seeded physical dispatch: PASS'
cases['test_generated_fleet_dispatch.gd'] = 'Temporary game generated fleet dispatch: PASS'
cases['test_fleet_dispatch_restore.gd'] = 'Temporary game fleet dispatch reconstruction: PASS'
cases['test_recovery_dispatch_restore.gd'] = 'Temporary game recovery dispatch reconstruction: PASS'
cases['test_parallel_recovery_restore.gd'] = 'Temporary game parallel recovery reconstruction: PASS'
cases['test_footprint_clearance.gd'] = 'Temporary game footprint clearance: PASS'
cases['test_endpoint_clearance.gd'] = 'Temporary game endpoint clearance: PASS'
with tempfile.TemporaryDirectory(prefix='temporary-game-check-') as scratch:
    env = os.environ.copy()
    env['APPDATA'] = scratch
    env['LOCALAPPDATA'] = scratch
    for script, expected in cases.items():
        result = subprocess.run([str(godot), '--headless', '--path', str(root), '--script', 'res://' + script], env=env, text=True, capture_output=True, timeout=90)
        output = result.stdout + result.stderr
        errors = [line for line in output.splitlines() if 'ERROR:' in line and 'Failed to read the root certificate store' not in line]
        if result.returncode or expected not in output or 'SCRIPT ERROR' in output or errors:
            print(script + ': FAIL\n' + output)
            sys.exit(1)
        print(script + ': PASS; root-certificate-store warnings: ' + str(output.count('Failed to read the root certificate store')), flush=True)
print(f'Temporary game integration: {len(cases)}/{len(cases)} passed')
