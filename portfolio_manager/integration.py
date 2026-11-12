"""Owner-controlled integration over the existing authenticated Windows pipe."""
from pathlib import Path
import os
import secrets
import threading
from .workspace import ChatWorkspaces, context_path


OPERATIONS = {
    'portfolio_open': 'Show Portfolio Manager for an explicit owner request.',
    'portfolio_context': 'Read the selected file or folder, operating mode and bounded portfolio project summary for this chat. Read the complete canonical record and checkpoint before resuming a project. Reconnect with the private reconnect key from the original open result when the transport changes.',
    'portfolio_select': 'Change this chat selection with path and optional revision. Accepts repository-relative paths.',
    'portfolio_start_selected': 'Start a background worker for the selected portfolio folder or project record at the owner’s request.',
    'portfolio_stop_selected': 'Stop only the worker assigned to this chat workspace.',
    'portfolio_status': 'Read operating mode, directory counts, and worker status.',
    'portfolio_start_worker': 'Start local work in a niche folder when the owner explicitly requests it.',
    'portfolio_register': 'Register this authorized Codex chat for a niche folder.',
    'portfolio_claim': 'Claim the next eligible project for a registered chat. Optionally provide project_id to claim only that project, within the registered folder.',
    'portfolio_heartbeat': 'Renew a chat project lease while working.',
    'portfolio_checkpoint': 'Save the owned canonical record using its expected content hash and active lease.',
    'portfolio_set_development': 'Set the source folder for the currently claimed development task using its active manual lease and expected record hash. Release the task for supervised background execution after setting the scope.',
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

    def workspace(self, client, args, *, active_clients=()):
        with self.workspace_lock:
            row = self.workspaces.attach(client, args.get('reconnect_key'), active_clients=active_clients)
            if 'path' in args:
                row.update(self.workspaces.select(row['id'], args['path'], args.get('revision'), client=client))
            return row

    def context_info(self, workspace):
        try:
            path = context_path(self.repo, workspace['selection'])
        except FileNotFoundError:
            return {'kind': 'missing'}
        data = {'kind': 'folder' if path.is_dir() else 'file'}
        if path.is_dir() and path.is_relative_to(self.coordinator.niches):
            state = self.coordinator.snapshot(path)
            projects = sorted(state['projects'], key=lambda row: (not row['eligible'], row['id']))
            fields = ('id', 'title', 'status', 'eligible', 'record_path', 'next_action', 'progress_pct', 'worker_id')
            data['portfolio'] = {
                'counts': state['counts'],
                'projects': [{key: row.get(key) for key in fields} for row in projects[:50]],
                'truncated': len(projects) > 50,
            }
        if path.is_file() and path.parent.name == 'projects' and path.is_relative_to(self.coordinator.niches):
            state = self.coordinator.snapshot(path.parent.parent)
            record = next((row for row in state['projects'] if row['record_path'] == workspace['selection']), None)
            if record:
                data['project'] = {k: record.get(k) for k in
                                   ('id', 'title', 'status', 'eligible', 'record_path', 'content_sha256',
                                    'worker_id', 'checkpoint', 'next_action', 'progress_pct', 'public_results')}
                milestones = record.get('milestones') or []
                milestone_fields = ('id', 'title', 'criteria', 'status', 'verified', 'provisional',
                                    'depends_on', 'checkpoint')
                data['project']['milestones'] = [
                    {key: milestone.get(key) for key in milestone_fields} for milestone in milestones[:50]
                ]
                data['project']['milestones_truncated'] = len(milestones) > 50
                current = record.get('current_task')
                data['project']['current_task'] = (
                    {key: current.get(key) for key in milestone_fields} if current else None
                )
        return data

    def start_workspace_worker(self, ident):
        with self.workspace_lock:
            row = self.get_workspace(ident)
            if row['worker_id'] and self.coordinator.worker(row['worker_id'])['state'] == 'running':
                raise ValueError('This workspace already has a running worker.')
            selection = context_path(self.repo, row['selection'])
            project_id = None
            label = selection.name
            if (selection.is_file() and selection.parent.name == 'projects'
                    and selection.suffix.lower() == '.md' and selection.is_relative_to(self.coordinator.niches)):
                project = self.context_info(row).get('project')
                if not project:
                    raise ValueError('The selected file is not a recognized portfolio project.')
                project_id = project['id']
                label = project['title'][:120]
                folder = selection.parent.parent
            elif selection.is_dir() and selection.is_relative_to(self.coordinator.niches):
                folder = selection
            else:
                raise ValueError('Select a portfolio folder or project to start a background worker.')
            worker = self.call('portfolio_start_worker', {'folder': str(folder), 'label': label,
                                                          'project_id': project_id})
            try:
                self.workspaces.assign(ident, worker['id'])
            except Exception:
                self.supervisor.stop(worker['id'])
                raise
            return worker

    def prepare_selected_development(self, ident, folder, *, expected_selection, expected_revision):
        """Bind the selected project's next task to a source folder and start it."""
        from .development import DevelopmentScope

        with self.workspace_lock:
            workspace = self.get_workspace(ident)
            if (workspace['selection'] != expected_selection or
                    workspace['revision'] != expected_revision):
                raise ValueError('The selection changed. Select the project again before starting development.')
            if workspace['worker_id'] and self.coordinator.worker(workspace['worker_id'])['state'] == 'running':
                raise ValueError('This workspace already has a running worker.')
            selection = context_path(self.repo, workspace['selection'])
            if not (selection.is_file() and selection.parent.name == 'projects'
                    and selection.suffix.lower() == '.md' and selection.is_relative_to(self.coordinator.niches)):
                raise ValueError('Select a portfolio project before starting development.')
            project = self.context_info(workspace).get('project')
            if not project:
                raise ValueError('The selected file is not a recognized portfolio project.')
            source = context_path(self.repo, folder)
            if not source.is_dir():
                raise ValueError('Choose a source folder for the selected project.')
            relative = source.relative_to(self.repo).as_posix()
            DevelopmentScope.discover(self.repo, relative)
            worker = self.coordinator.register(selection.parent.parent, kind='manual',
                                               label='Prepare development', project_id=project['id'])
            claim = None
            try:
                claim = self.coordinator.claim(worker['id'], project_id=project['id'])
                if not claim:
                    raise ValueError('This project has no eligible task or is already being worked on.')
                self.coordinator.set_development_scope(worker['id'], claim['lease_token'],
                                                       expected_sha256=claim['record_sha256'], folder=relative)
                self.coordinator.finish(worker['id'], claim['lease_token'], outcome='retry',
                                        summary=claim.get('checkpoint') or 'Ready for development.')
                claim = None
            finally:
                try:
                    if claim:
                        self.coordinator.finish(worker['id'], claim['lease_token'], outcome='retry',
                                                summary=claim.get('checkpoint') or 'Development setup was interrupted.')
                finally:
                    self.coordinator.set_worker_state(worker['id'], 'stopped')
            return self.start_workspace_worker(ident)

    def stop_workspace_worker(self, ident):
        with self.workspace_lock:
            worker = self.get_workspace(ident)['worker_id']
            if worker:
                self.supervisor.stop(worker)
            return {'stopped': bool(worker)}

    def review_candidate(self, project_id, task_id):
        from .development import candidate_review
        with self.workspace_lock:
            evidence = self.coordinator.candidate_evidence(project_id, task_id)
            review = candidate_review(self.repo, self.coordinator.db_path.parent,
                                      evidence['path'], evidence['sha256'])
            records, _ = self.coordinator._catalog()
            if not records.get(project_id) or records[project_id]['content_sha256'] != review['record_sha256']:
                raise ValueError('The project record changed. Prepare a new candidate.')
            return review

    def apply_candidate(self, project_id, task_id, expected_sha256):
        from .development import apply_reviewed_candidate, candidate_review
        with self.workspace_lock:
            def apply(evidence):
                if evidence['sha256'] != expected_sha256:
                    raise ValueError('The candidate changed. Review it again.')
                review = candidate_review(self.repo, self.coordinator.db_path.parent,
                                          evidence['path'], expected_sha256)
                records, _ = self.coordinator._catalog()
                if not records.get(project_id) or records[project_id]['content_sha256'] != review['record_sha256']:
                    raise ValueError('The project record changed. Prepare a new candidate.')
                return apply_reviewed_candidate(self.repo, self.coordinator.db_path.parent,
                                                evidence['path'], expected_sha256)
            return self.coordinator.guard_candidate(project_id, task_id, apply)

    def verify_candidate(self, project_id, task_id):
        from portfolio_autopilot.codex_relay.config import Config
        from .applied_verification import verify_applied
        from .development import BubblewrapVerifier
        distribution = Config().wsl_distribution if os.name == 'nt' else None
        verifier = BubblewrapVerifier(distribution)
        evidence = self.coordinator.candidate_evidence(project_id, task_id)
        state = self.coordinator.control()
        if state['stopped'] or state['emergency']:
            raise InterruptedError('Resume Portfolio Manager before verifying changes.')
        cancelled = threading.Event()
        finished = threading.Event()

        def watch_stop():
            while not finished.is_set():
                try:
                    state = self.coordinator.control()
                    if state['stopped'] or state['emergency']:
                        cancelled.set()
                        return
                except Exception:
                    cancelled.set()
                    return
                finished.wait(.1)

        watcher = threading.Thread(target=watch_stop, daemon=True)
        watcher.start()
        try:
            result = verify_applied(self.repo, self.coordinator.db_path.parent,
                                    evidence['path'], evidence['sha256'], verifier, cancelled)
            if cancelled.is_set():
                raise InterruptedError('Verification was cancelled.')
            def confirm(current):
                if cancelled.is_set():
                    raise InterruptedError('Verification was cancelled.')
                if any(current.get(key) != evidence.get(key) for key in ('kind', 'path', 'sha256')):
                    raise ValueError('The candidate changed. Review it again.')
                records, _ = self.coordinator._catalog()
                if not records.get(project_id) or records[project_id]['content_sha256'] != result['record_sha256']:
                    raise ValueError('The project record changed. Prepare a new candidate.')
                return result
            return self.coordinator.record_candidate_check(project_id, task_id, confirm)
        finally:
            finished.set()
            watcher.join(timeout=1)

    def complete_candidate(self, project_id, task_id, *, note):
        """Record the owner's review after the current candidate has passed checks."""
        return self.coordinator.complete_candidate(project_id, task_id, note=note)

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
                                               worker_key=worker_key, project_id=args.get('project_id'))
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
            return self.coordinator.claim(worker, project_id=args.get('project_id'))
        lease = args['lease_token']
        if operation == 'portfolio_heartbeat':
            return {'active': self.coordinator.heartbeat(worker, lease)}
        if operation == 'portfolio_checkpoint':
            return self.coordinator.apply_checkpoint(worker, lease, expected_sha256=args['expected_sha256'],
                                                     text=args['text'])
        if operation == 'portfolio_set_development':
            return self.coordinator.set_development_scope(worker, lease, expected_sha256=args['expected_sha256'],
                                                          folder=args['folder'])
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
