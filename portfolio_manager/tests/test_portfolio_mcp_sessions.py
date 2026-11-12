"""Exercise separate MCP chats against one real Windows controller."""
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'apps' / 'codex_desktop_assistant'


@unittest.skipUnless(os.name == 'nt', 'Windows controller required')
class PortfolioMCPSessionTests(unittest.TestCase):
    def test_two_stdio_clients_share_controller_and_keep_selections(self):
        sys.path.insert(0, str(APP))
        self.addCleanup(sys.path.remove, str(APP))
        from bridge.client import ControllerClient

        with tempfile.TemporaryDirectory(prefix='portfolio-mcp-') as temporary:
            local = Path(temporary)
            state = local / 'CodexDesktopAssistant'
            environment = {**os.environ, 'LOCALAPPDATA': str(local), 'QT_QPA_PLATFORM': 'offscreen'}
            packages = str(Path(sys.prefix) / 'Lib' / 'site-packages')
            # Use the venv's dependencies without the extra Windows launcher process.
            invoke = ('import runpy,site,sys; site.addsitedir(sys.argv.pop(1)); '
                      'sys.exit(runpy.run_path(sys.argv.pop(1))["main"]())')
            command = [sys._base_executable, '-c', invoke, packages, str(APP / 'run.py'), '--background']
            with subprocess.Popen(command, cwd=APP, env=environment, creationflags=subprocess.CREATE_NO_WINDOW,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as controller:
                try:
                    client = ControllerClient(state)
                    deadline = time.monotonic() + 20
                    while True:
                        if controller.poll() is not None:
                            self.fail(controller.stderr.read().decode(errors='replace')[-2000:])
                        try:
                            health = client.request('bridge_health')
                            break
                        except (OSError, ValueError, RuntimeError):
                            if time.monotonic() >= deadline:
                                raise
                            time.sleep(.1)
                    self.assertTrue(health['portfolio_manager'])
                    self.assertEqual(health['pid'], controller.pid)
                    saved = asyncio.run(self.exercise_sessions(environment, packages, state, controller.pid))
                    self.assertEqual(client.request('bridge_health')['pid'], controller.pid)
                    self.assertEqual(client.request('portfolio_status')['workers'], [])
                finally:
                    controller.terminate()
                    controller.wait(timeout=10)
            # Restart only this disposable process, keeping its temporary profile.
            with subprocess.Popen(command, cwd=APP, env=environment, creationflags=subprocess.CREATE_NO_WINDOW,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as restarted:
                try:
                    client = ControllerClient(state)
                    deadline = time.monotonic() + 20
                    while True:
                        if restarted.poll() is not None:
                            self.fail(restarted.stderr.read().decode(errors='replace')[-2000:])
                        try:
                            health = client.request('bridge_health')
                            if health['pid'] == restarted.pid:
                                break
                        except (OSError, ValueError, RuntimeError):
                            pass
                        if time.monotonic() >= deadline:
                            self.fail('The disposable controller did not restart')
                        time.sleep(.1)
                    asyncio.run(self.exercise_restart(environment, packages, saved, restarted.pid))
                    # Exercise the real Stop handler against this disposable
                    # profile only; never revoke the owner's live grants.
                    stopped = client.request('bridge_stop')
                    self.assertTrue(stopped['stopped'])
                    health = client.request('bridge_health')
                    self.assertTrue(health['stopped'])
                    self.assertFalse(health['desktop_authorized'])
                    control = client.request('portfolio_status')
                    self.assertTrue(control['stopped'])
                    self.assertTrue(control['emergency'])
                    with self.assertRaises(RuntimeError):
                        client.request('desktop.inspect', {'window': 1})
                finally:
                    restarted.terminate()
                    restarted.wait(timeout=10)

    async def exercise_sessions(self, environment, packages, state, controller_pid):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from portfolio_manager.coordinator import Coordinator

        bootstrap = ('import runpy,site,sys; site.addsitedir(sys.argv.pop(1)); '
                     'runpy.run_path(sys.argv.pop(1), run_name="__main__")')
        parameters = StdioServerParameters(command=sys._base_executable,
                                          args=['-c', bootstrap, packages, str(APP / 'bridge' / 'server.py')],
                                          cwd=APP, env=environment)

        def hook_key(session_id, source):
            event = {'session_id': session_id, 'source': source, 'hook_event_name': 'SessionStart', 'cwd': str(ROOT)}
            result = subprocess.run(
                [sys._base_executable, '-c', bootstrap, packages, str(ROOT / 'portfolio_manager' / 'codex_session_hook.py')],
                input=json.dumps(event), cwd=ROOT, env=environment, capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout)
            context = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
            keys = re.findall(r'\b[0-9a-f]{64}\b', context)
            self.assertEqual(len(keys), 1)
            return keys[0]

        @asynccontextmanager
        async def connect():
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=15)) as session:
                    await session.initialize()
                    yield session

        async def call(session, name, **arguments):
            payload = {'arguments': arguments} if name.startswith('portfolio_') else {}
            result = await session.call_tool(name, payload)
            self.assertFalse(result.isError, f'{name} failed')
            return json.loads(result.content[0].text)

        # No external account, browser action, inference or worker is needed.
        first_path = 'docs/PORTFOLIO_MANAGER_WORKFLOW.md'
        second_path = 'business_portfolio/niches/ai-workflow-automation/agency'
        first_key = hook_key('thr_test_first', 'startup')
        second_key = hook_key('thr_test_second', 'startup')
        async with connect() as first:
            tools = await first.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            self.assertTrue({'portfolio_open', 'portfolio_select', 'portfolio_context'} <=
                            tool_names)
            self.assertNotIn('bridge_bind_codex_session', tool_names)
            workspace = await call(first, 'portfolio_open', reconnect_key=first_key)
            self.assertEqual((await call(first, 'portfolio_open'))['id'], workspace['id'])
            async with connect() as competing:
                denied = await competing.call_tool('portfolio_open', {'arguments': {'reconnect_key': first_key}})
                self.assertTrue(denied.isError)
                self.assertEqual((await call(first, 'portfolio_context'))['id'], workspace['id'])
            async with connect() as second:
                other = await call(second, 'portfolio_open', path=second_path, reconnect_key=second_key)
                self.assertNotEqual(workspace['id'], other['id'])
                denied = await second.call_tool('portfolio_context', {'arguments': {'reconnect_key': first_key}})
                self.assertTrue(denied.isError)
                for session in (first, second):
                    self.assertEqual((await call(session, 'bridge_health'))['pid'], controller_pid)
                await call(first, 'portfolio_select', path=first_path, revision=workspace['revision'])
                first_context = await call(first, 'portfolio_context')
                second_context = await call(second, 'portfolio_context')
                self.assertEqual((first_context['selection'], first_context['kind']), (first_path, 'file'))
                self.assertEqual((second_context['selection'], second_context['kind']), (second_path, 'folder'))
                self.assertGreater(second_context['portfolio']['counts']['total'], 0)
                self.assertTrue(all(row['record_path'].startswith(second_path + '/')
                                    for row in second_context['portfolio']['projects']))
                self.assertNotIn('portfolio', first_context)

                # Update the shared setting through the same owner-side method as the UI.
                coordinator = Coordinator(ROOT, state / 'portfolio-manager' / 'coordinator.sqlite3')
                mode = 'human' if first_context['mode'] == 'afk' else 'afk'
                coordinator.set_mode(mode)
                for session in (first, second):
                    self.assertEqual((await call(session, 'portfolio_context'))['mode'], mode)

        async with connect() as resumed:
            restored = await call(resumed, 'portfolio_open', reconnect_key=hook_key('thr_test_first', 'resume'))
            self.assertEqual(restored['id'], workspace['id'])
            self.assertEqual(restored['selection'], first_path)
            self.assertEqual(restored['mode'], mode)

        # Reconnect one transport while another workspace remains connected.
        # This uses the isolated controller above, never the owner's controller.
        async with connect() as unaffected:
            still_open = await call(unaffected, 'portfolio_open', reconnect_key=second_key)
            self.assertEqual(still_open['id'], other['id'])
            async with connect() as interrupted:
                before = await call(interrupted, 'portfolio_open', reconnect_key=first_key)
                self.assertEqual(before['selection'], first_path)
            async with connect() as reconnected:
                after = await call(reconnected, 'portfolio_open', reconnect_key=first_key)
                self.assertEqual(after['id'], workspace['id'])
                self.assertEqual(after['selection'], first_path)
                unchanged = await call(unaffected, 'portfolio_context')
                self.assertEqual(unchanged['id'], other['id'])
                self.assertEqual(unchanged['selection'], second_path)
                self.assertEqual(unchanged['mode'], mode)
                self.assertEqual((await call(unaffected, 'bridge_health'))['pid'], controller_pid)
        return ((first_key, workspace['id'], first_path), (second_key, other['id'], second_path), mode)

    async def exercise_restart(self, environment, packages, saved, controller_pid):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        bootstrap = ('import runpy,site,sys; site.addsitedir(sys.argv.pop(1)); '
                     'runpy.run_path(sys.argv.pop(1), run_name="__main__")')
        parameters = StdioServerParameters(command=sys._base_executable,
                                          args=['-c', bootstrap, packages, str(APP / 'bridge' / 'server.py')],
                                          cwd=APP, env=environment)
        first, second, mode = saved
        async with stdio_client(parameters) as (read_a, write_a):
            async with ClientSession(read_a, write_a, read_timeout_seconds=timedelta(seconds=15)) as session_a:
                await session_a.initialize()
                async with stdio_client(parameters) as (read_b, write_b):
                    async with ClientSession(read_b, write_b, read_timeout_seconds=timedelta(seconds=15)) as session_b:
                        await session_b.initialize()
                        for session, (key, workspace_id, selection) in ((session_a, first), (session_b, second)):
                            result = await session.call_tool('portfolio_open', {'arguments': {'reconnect_key': key}})
                            self.assertFalse(result.isError)
                            restored = json.loads(result.content[0].text)
                            self.assertEqual(restored['id'], workspace_id)
                            self.assertEqual(restored['selection'], selection)
                            self.assertEqual(restored['mode'], mode)
                            health = await session.call_tool('bridge_health', {})
                            self.assertEqual(json.loads(health.content[0].text)['pid'], controller_pid)
