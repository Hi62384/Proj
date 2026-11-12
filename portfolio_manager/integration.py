"""Owner-controlled integration over the existing authenticated Windows pipe."""
from pathlib import Path
import secrets


OPERATIONS = {
    'portfolio_open': 'Show Portfolio Manager for an explicit owner request.',
    'portfolio_status': 'Read operating mode, directory counts, and worker status.',
    'portfolio_start_worker': 'Start local work in a niche folder when the owner explicitly requests it.',
    'portfolio_register': 'Register this authorized Codex chat for a niche folder.',
    'portfolio_claim': 'Claim the next eligible project for a registered chat.',
    'portfolio_heartbeat': 'Renew a chat project lease while working.',
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
