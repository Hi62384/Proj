"""Owner-controlled integration over the existing authenticated Windows pipe."""
from pathlib import Path
import secrets
import threading
from .workspace import ChatWorkspaces, context_path


OPERATIONS = {
    'portfolio_open': 'Show Portfolio Manager for an explicit owner request.',
    'portfolio_context': 'Read the selected file or folder and operating mode for this chat. Reconnect with the private reconnect key from the original open result when the transport changes.',
    'portfolio_select': 'Change this chat selection with path and optional revision. Accepts repository-relative paths.',
    'portfolio_start_selected': 'Start a background worker for the selected portfolio folder at the owner’s request.',
    'portfolio_stop_selected': 'Stop only the worker assigned to this chat workspace.',
    'portfolio_status': 'Read operating mode, directory counts, and worker status.',
    'portfolio_start_worker': 'Start local work in a niche folder when the owner explicitly requests it.',
    'portfolio_register': 'Register this authorized Codex chat for a niche folder.',
    'portfolio_claim': 'Claim the next eligible project for a registered chat.',
    'portfolio_heartbeat': 'Renew a chat project lease while working.',
    'portfolio_checkpoint': 'Save the owned canonical record using its expected content hash and active lease.',
    'portfolio_release': 'Release an interrupted or blocked chat assignment with a checkpoint.',
    'portfolio_request_human': 'Save a scoped human request for a claimed chat task.',
}


class ManagerHost:
    def __init__(self, repo, directory):
        from .coordinator import Coordinator
        from .runner import Supervisor

        self.repo = Path(repo).resolve()
        self.coordinator = Coordinator(self.repo, Path(directory) / 'portfolio-manager' / 'coordinator.sqlite3')
        self.coordinator.recover_controller()
        self.supervisor = Supervisor(self.coordinator)
        self.workspaces = ChatWorkspaces(self.coordinator)
        self.workspace_lock = threading.RLock()

    def get_workspace(self, ident):
        return self.workspaces.get(ident)

    def select(self, ident, path, revision=None):
        with self.workspace_lock:
            return self.workspaces.select(ident, path, revision)

    def workspace(self, client, args):
        with self.workspace_lock:
            row = self.workspaces.attach(client, args.get('reconnect_key'))
            if 'path' in args:
                row.update(self.workspaces.select(row['id'], args['path'], args.get('revision'), client=client))
            return row

    def context_info(self, workspace):
        try:
            path = context_path(self.repo, workspace['selection'])
        except FileNotFoundError:
            return {'kind': 'missing'}
        data = {'kind': 'folder' if path.is_dir() else 'file'}
        if path.is_file() and path.parent.name == 'projects' and path.is_relative_to(self.coordinator.niches):
            state = self.coordinator.snapshot(path.parent.parent)
            record = next((row for row in state['projects'] if row['record_path'] == workspace['selection']), None)
            if record:
                data['project'] = {k: record.get(k) for k in
                                   ('id', 'title', 'status', 'checkpoint', 'next_action', 'progress_pct', 'public_results')}
        return data

    def start_workspace_worker(self, ident):
        with self.workspace_lock:
            row = self.get_workspace(ident)
            if row['worker_id'] and self.coordinator.worker(row['worker_id'])['state'] == 'running':
                raise ValueError('This workspace already has a running worker.')
            folder = context_path(self.repo, row['selection'])
            if not folder.is_dir() or not folder.is_relative_to(self.coordinator.niches):
                raise ValueError('Select a portfolio folder to start a background worker. Use the chat to work on a specific file.')
            worker = self.call('portfolio_start_worker', {'folder': str(folder), 'label': folder.name})
            self.workspaces.assign(ident, worker['id'])
            return worker

    def stop_workspace_worker(self, ident):
        with self.workspace_lock:
            worker = self.get_workspace(ident)['worker_id']
            if worker:
                self.supervisor.stop(worker)
            return {'stopped': bool(worker)}

    def control(self):
        return self.coordinator.control()

    def emergency_stop(self):
        self.supervisor.stop_all(emergency=True)

    def restore(self):
        self.supervisor.restore()

    def close(self):
        self.supervisor.close()

    def call(self, operation, args):
        if operation == 'portfolio_status':
            state = self.coordinator.snapshot(args.get('folder'))
            # Keep the wire response bounded and leave canonical records on disk.
            workers = [{key: row.get(key) for key in ('label', 'folder', 'kind', 'status', 'project_id', 'task_id')}
                       for row in state['workers'][:100]]
            return {**{key: state[key] for key in ('mode', 'stopped', 'emergency', 'counts')}, 'workers': workers}
        if operation in ('portfolio_start_worker', 'portfolio_register'):
            state = self.control()
            if state['stopped'] or state['emergency']:
                raise PermissionError('Resume Portfolio Manager in its window before starting workers.')
            background = operation == 'portfolio_start_worker'
            worker_key = None if background else secrets.token_hex(32)
            worker = self.coordinator.register(args.get('folder'), kind='background' if background else 'manual',
                                               label=args.get('label'), session_ref=args.get('session_ref'),
                                               worker_key=worker_key)
            if background:
                try:
                    self.supervisor.start(worker['id'])
                except Exception:
                    self.coordinator.set_worker_state(worker['id'], 'stopped')
                    raise
            return worker if background else {**worker, 'worker_key': worker_key}
        worker = args['worker_id']
        self.coordinator.verify_manual_worker(worker, args.get('worker_key'))
        if operation == 'portfolio_claim':
            return self.coordinator.claim(worker)
        lease = args['lease_token']
        if operation == 'portfolio_heartbeat':
            return {'active': self.coordinator.heartbeat(worker, lease)}
        if operation == 'portfolio_checkpoint':
            return self.coordinator.apply_checkpoint(worker, lease, expected_sha256=args['expected_sha256'],
                                                     text=args['text'])
        if operation == 'portfolio_release':
            outcome = args.get('outcome', 'paused')
            if outcome not in ('paused', 'blocked', 'retry'):
                raise ValueError('Use the supervised verification path to complete a task.')
            return self.coordinator.finish(worker, lease, outcome=outcome, summary=args['summary'])
        if operation == 'portfolio_request_human':
            return self.coordinator.request_human(worker, lease, action=args['action'], reason=args['reason'],
                                                  scope=args['scope'], cost_cad=args.get('cost_cad', 0),
                                                  consequences=args.get('consequences', ''), after=args.get('after', ''),
                                                  kind=args.get('kind', 'approval'))
        raise ValueError('Unknown Portfolio Manager operation.')
