from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import patch

from portfolio_manager.coordinator import Coordinator, CoordinatorError


def write_fixture(repo):
    portfolio = repo / 'business_portfolio'
    research = portfolio / 'research'
    research.mkdir(parents=True)
    (research / 'SOURCE_REGISTER.json').write_text(json.dumps([
        {'id': 'fixture', 'title': 'Fictional test data', 'url': 'https://example.invalid/fixture'}]), encoding='utf8')
    paths = ['agency', 'agency/deep', 'agency/deep/third', 'products']
    for i, name in enumerate(paths):
        folder = portfolio / 'niches' / name
        folder.mkdir(parents=True)
        parent = 'N-' + str(paths.index(name.rsplit('/', 1)[0])) if '/' in name else None
        (folder / 'NICHE.json').write_text(json.dumps({'id': f'N-{i}', 'path': name,
              'parent': parent, 'title': name.split('/')[-1].title()}), encoding='utf8')
    records = {}
    for number, niche, status, kind in ((1, paths[0], 'planned', 'standalone_service'),
                                        (2, paths[2], 'active', 'standalone_service'),
                                        (3, paths[0], 'blocked', 'standalone_service'),
                                        (4, paths[0], 'planned', 'bundled_component'),
                                        (5, paths[3], 'planned', 'standalone_service'),
                                        (6, paths[3], 'deferred', 'deferred_download')):
        pid = f'TST-{number:03}'
        record = {'id': pid, 'title': f'Fictional project {number}', 'schema_version': 1,
                  'niche_path': niche, 'niche_id': f'N-{paths.index(niche)}', 'record_type': kind,
                  'origin': 'current_package', 'priority': 'P1', 'work_state': status,
                  'commercial_validation': 'unvalidated', 'evidence_basis': 'fictional',
                  'source_ids': ['fixture'], 'parent_project': None, 'related_projects': [],
                  'next_action': f'Prepare fictional artifact {number}', 'last_reviewed': '2026-11-11',
                  'execution_authorized': False, 'privacy': 'public_only', 'actual_revenue': None}
        file = portfolio / 'niches' / niche / 'projects' / f'{pid.lower()}.md'
        file.parent.mkdir(exist_ok=True)
        file.write_text('---\n' + json.dumps(record) + '\n---\n# Fictional business\n\nPurpose and milestones.\n', encoding='utf8')
        records[pid] = file
    return records


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.records = write_fixture(self.repo)
        self.manager = Coordinator(self.repo)

    def worker(self, folder='agency'):
        return self.manager.register(folder, kind='background')['id']

    def evidence(self, project_id, filename='proof.md', text='A verified fictional artifact.'):
        path = self.repo / 'business_portfolio' / 'results' / project_id / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf8')
        return {'kind': 'verified_artifact', 'path': path.relative_to(self.repo).as_posix(),
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def row(self, project_id):
        return next(row for row in self.manager.snapshot()['projects'] if row['id'] == project_id)

    def test_recursive_scope_uses_real_ids_and_preserves_records(self):
        before = {pid: path.read_bytes() for pid, path in self.records.items()}
        view = self.manager.snapshot('agency')
        self.assertEqual(view['counts']['total'], 4)
        self.assertEqual(view['counts']['eligible'], 2)
        self.assertIn('Purpose and milestones.', self.row('TST-002')['body'])
        worker = self.worker('agency/deep/third')
        claim = self.manager.claim(worker)
        self.assertEqual(claim['project_id'], 'TST-002')
        self.assertTrue(claim['task']['provisional'])
        self.assertIsNone(self.row('TST-002')['progress_pct'])
        self.assertEqual(before, {pid: path.read_bytes() for pid, path in self.records.items()})
        self.assertNotIn(claim['lease_token'], json.dumps(self.manager.snapshot()))
        with self.assertRaises(CoordinatorError):
            self.manager.register(self.repo)
        with self.assertRaises(CoordinatorError):
            self.manager.register('../niches/agency')

    def test_specific_project_claim_never_falls_back_to_another_project(self):
        first = self.worker('agency')
        second = self.worker('agency')
        self.assertIsNone(self.manager.claim(first, project_id='TST-005'))
        claim = self.manager.claim(first, project_id='TST-001')
        self.assertEqual(claim['project_id'], 'TST-001')
        self.assertIsNone(self.manager.claim(second, project_id='TST-001'))
        self.assertEqual(self.manager.claim(second, project_id='TST-002')['project_id'], 'TST-002')

    def test_overlapping_claims_are_atomic_across_connections(self):
        a, b = self.worker(), self.worker()
        managers = self.manager, Coordinator(self.repo)
        barrier = threading.Barrier(2)

        def take(manager, worker):
            barrier.wait(timeout=4)
            return manager.claim(worker)

        with ThreadPoolExecutor(2) as pool:
            futures = [pool.submit(take, manager, worker) for manager, worker in zip(managers, (a, b))]
            self.assertEqual({f.result(timeout=8)['project_id'] for f in futures}, {'TST-001', 'TST-002'})
        self.assertIsNone(self.manager.claim(self.worker()))
        self.worker('products')
        with self.assertRaisesRegex(CoordinatorError, 'worker limit'):
            Coordinator(self.repo, max_workers=10).register()

    def test_verified_milestone_dependencies_and_commercial_independence(self):
        self.manager.configure_plan('TST-002', [
            {'id': 'proof', 'title': 'Proof', 'criteria': 'Exact artifact exists', 'weight': 1,
             'verification': {'kind': 'artifact', 'name': 'proof.md'}},
            {'id': 'qa', 'title': 'QA', 'criteria': 'Report exists', 'weight': 3, 'depends_on': ['proof']}])
        worker = self.worker('agency/deep')
        claim = self.manager.claim(worker)
        self.assertEqual(claim['task_id'], 'proof')
        token = claim['lease_token']
        with self.assertRaisesRegex(CoordinatorError, 'Completion requires'):
            self.manager.finish(worker, token, outcome='completed', summary='Worker says done')
        with self.assertRaisesRegex(CoordinatorError, 'verification rule'):
            self.manager.finish(worker, token, outcome='completed', summary='Wrong artifact',
                                evidence=self.evidence('TST-002', 'other.md'))
        proof = self.evidence('TST-002')
        self.manager.finish(worker, token, outcome='completed', summary='Proof checked', evidence=proof)
        self.assertEqual(self.row('TST-002')['progress_pct'], 25)
        (self.repo / proof['path']).write_text('Changed after verification.', encoding='utf8')
        self.assertIsNone(self.manager.claim(worker))
        self.assertEqual(self.row('TST-002')['progress_pct'], 0)
        self.evidence('TST-002')
        claim = self.manager.claim(worker)
        self.assertEqual(claim['task_id'], 'qa')
        self.manager.finish(worker, claim['lease_token'], outcome='completed', summary='QA checked',
                            evidence=self.evidence('TST-002', 'qa.md'))
        project = self.row('TST-002')
        self.assertEqual(project['progress_pct'], 100)
        self.assertEqual(project['commercial_validation'], 'unvalidated')
        self.assertIsNone(project['actual_revenue'])

    def test_plan_dependency_validation(self):
        a = {'id': 'a', 'title': 'A', 'criteria': 'Evidence', 'weight': 1, 'depends_on': ['b']}
        b = {'id': 'b', 'title': 'B', 'criteria': 'Evidence', 'weight': 1, 'depends_on': ['a']}
        with self.assertRaisesRegex(CoordinatorError, 'cycle'):
            self.manager.configure_plan('TST-001', [a, b])
        with self.assertRaisesRegex(CoordinatorError, 'Unknown task dependency'):
            self.manager.configure_plan('TST-001', [a])

    def test_afk_login_waits_and_independent_projects_continue(self):
        worker = self.worker()
        claim = self.manager.claim(worker)
        request = self.manager.request_human(worker, claim['lease_token'], kind='login',
                          action='Sign in manually', reason='Fixture sign-in required', scope='example.invalid')
        self.assertEqual(self.manager.control()['mode'], 'afk')
        self.assertEqual(self.row(claim['project_id'])['status'], 'waiting')
        with self.assertRaisesRegex(CoordinatorError, 'Human Available'):
            self.manager.resolve_request(request['id'], 'complete')
        independent = self.manager.claim(worker)
        self.assertNotEqual(independent['project_id'], claim['project_id'])
        self.manager.finish(worker, independent['lease_token'], outcome='blocked', summary='Fixture blocked')
        reopened = Coordinator(self.repo)
        reopened.set_mode('human')
        self.assertEqual(reopened.snapshot()['requests'][0]['id'], request['id'])
        with self.assertRaisesRegex(CoordinatorError, 'matching'):
            reopened.resolve_request(request['id'], 'approve')
        reopened.resolve_request(request['id'], 'complete')
        resumed = reopened.claim(worker)
        self.assertEqual(resumed['project_id'], claim['project_id'])
        self.assertEqual(resumed['human_responses'][0]['status'], 'manual_completed')
        self.assertIn('Verify', resumed['checkpoint'])

    def test_owner_denial_and_pending_request_expiry_do_not_redispatch(self):
        clock = [1000.0]
        with patch('portfolio_manager.coordinator.time.time', side_effect=lambda: clock[0]):
            worker = self.worker()
            claim = self.manager.claim(worker)
            first = self.manager.request_human(worker, claim['lease_token'], action='Publish', reason='Fixture', scope='draft 1')
            self.manager.resolve_request(first['id'], 'deny')
            second = self.manager.claim(worker)
            self.manager.request_human(worker, second['lease_token'], action='Publish', reason='Fixture', scope='draft 2', ttl_seconds=5)
            clock[0] += 6
            view = self.manager.snapshot()
            self.assertFalse(view['requests'])
            self.assertEqual(self.row(second['project_id'])['status'], 'blocked')
            self.assertIsNone(self.manager.claim(worker))

    def test_effect_reservation_checks_exact_scope_and_survives_restart(self):
        self.manager.set_mode('human')
        worker = self.worker('agency/deep')
        claim = self.manager.claim(worker)
        request = self.manager.request_human(worker, claim['lease_token'], action='Publish fixture',
                                            reason='Owner decision', scope='only fictional draft 42')
        self.manager.resolve_request(request['id'], 'approve')
        resumed = self.manager.claim(worker)
        kwargs = {'approval_id': request['id'], 'dedup_key': 'fictional-publish-42', 'action': 'Publish fixture'}
        with self.assertRaisesRegex(CoordinatorError, 'exact effect'):
            self.manager.begin_effect(worker, resumed['lease_token'], scope='other draft', **kwargs)
        effect = self.manager.begin_effect(worker, resumed['lease_token'], scope=request['scope'], **kwargs)
        self.assertEqual(effect['state'], 'uncertain')
        restarted = Coordinator(self.repo)
        with self.assertRaisesRegex(CoordinatorError, 'cannot be replayed'):
            restarted.begin_effect(worker, resumed['lease_token'], scope=request['scope'], **kwargs)
        finished = restarted.finish(worker, resumed['lease_token'], outcome='blocked', summary='Process interrupted')
        self.assertEqual(finished['status'], 'reconcile')
        self.assertIsNone(restarted.claim(worker))
        with self.assertRaisesRegex(CoordinatorError, 'Reconcile the external effect'):
            restarted.reconcile_task(resumed['project_id'], resumed['task_id'], note='Unsafe retry')
        restarted.reconcile_effect(effect['id'], status='verified', evidence='Fictional provider read-back confirms outcome')
        restarted.reconcile_task(resumed['project_id'], resumed['task_id'], note='Resume verification only')
        again = restarted.claim(worker)
        with self.assertRaisesRegex(CoordinatorError, 'cannot be replayed'):
            restarted.begin_effect(worker, again['lease_token'], scope=request['scope'], **kwargs)

    def test_mode_revisions_invalidate_approval_and_stop_persists(self):
        self.manager.set_mode('human')
        worker = self.worker('agency/deep')
        claim = self.manager.claim(worker)
        request = self.manager.request_human(worker, claim['lease_token'], action='Approve draft', reason='Fixture', scope='draft')
        self.manager.resolve_request(request['id'], 'approve')
        self.manager.set_mode('afk')
        self.assertEqual(self.manager.set_mode('human')['mode_epoch'], 3)
        resumed = self.manager.claim(worker)
        self.assertFalse(resumed['human_responses'])
        self.manager.stop_all(emergency=True)
        restarted = Coordinator(self.repo)
        self.assertTrue(restarted.control()['emergency'])
        self.assertFalse(restarted.heartbeat(worker, resumed['lease_token']))
        self.assertIsNone(restarted.claim(worker))
        with self.assertRaisesRegex(CoordinatorError, 'explicit reset'):
            restarted.resume()
        self.assertFalse(restarted.resume(clear_emergency=True)['stopped'])
        self.assertEqual(restarted.snapshot()['workers'][0]['state'], 'paused')

    def test_lease_heartbeat_expiry_requires_reconciliation(self):
        clock = [1000.0]
        with patch('portfolio_manager.coordinator.time.time', side_effect=lambda: clock[0]):
            manager = Coordinator(self.repo, lease_seconds=10)
            worker = manager.register('agency/deep')['id']
            first = manager.claim(worker)
            clock[0] += 8
            self.assertTrue(manager.heartbeat(worker, first['lease_token']))
            clock[0] += 8
            self.assertTrue(manager.heartbeat(worker, first['lease_token']))
            clock[0] += 11
            restarted = Coordinator(self.repo, lease_seconds=10)
            self.assertFalse(restarted.heartbeat(worker, first['lease_token']))
            replacement = restarted.register('agency/deep')['id']
            self.assertIsNone(restarted.claim(replacement))
            restarted.reconcile_task(first['project_id'], first['task_id'], note='Reviewed local checkpoint')
            second = restarted.claim(replacement)
            self.assertEqual(second['project_id'], first['project_id'])
            self.assertNotEqual(second['lease_token'], first['lease_token'])

    def test_controller_restart_reconciles_background_but_keeps_independent_chat(self):
        background = self.worker('agency/deep')
        manual = self.manager.register('products')['id']
        former = self.manager.claim(background)
        independent = self.manager.claim(manual)
        restarted = Coordinator(self.repo)
        self.assertEqual(restarted.recover_controller(), 1)
        self.assertFalse(restarted.heartbeat(background, former['lease_token']))
        self.assertTrue(restarted.heartbeat(manual, independent['lease_token']))
        workers = {row['id']: row for row in restarted.snapshot()['workers']}
        self.assertEqual(workers[background]['state'], 'paused')
        self.assertEqual(workers[manual]['status'], 'working')

    def test_prior_artifacts_are_project_scoped_and_survive_plan_setup(self):
        worker = self.worker('agency/deep')
        claim = self.manager.claim(worker)
        pid = claim['project_id']
        path = self.manager.db_path.parent / 'worker-runs' / 'TST-001' / 'test' / 'result.md'
        path.parent.mkdir(parents=True)
        path.write_text('Another project result.', encoding='utf8')
        unrelated = {'kind': 'verified_artifact', 'path': str(path),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        with self.assertRaisesRegex(CoordinatorError, 'outside the project'):
            self.manager.finish(worker, claim['lease_token'], outcome='completed', summary='Wrong scope', evidence=unrelated)
        proof = self.evidence(pid)
        self.manager.finish(worker, claim['lease_token'], outcome='completed', summary='Proof checked', evidence=proof)
        self.manager.configure_plan(pid, [{'id': 'next', 'title': 'Review proof', 'criteria': 'Review document', 'weight': 1}])
        next_claim = self.manager.claim(worker)
        self.assertEqual(next_claim['prior_artifacts'][0]['sha256'], proof['sha256'])
        self.assertEqual(self.row(pid)['progress_pct'], 0)

    def test_project_dependency_waits_for_verified_milestones(self):
        path = self.records['TST-005']
        opening, metadata, ending = path.read_text(encoding='utf8').split('---', 2)
        body = json.loads(metadata)
        body['depends_on'] = ['TST-002']
        path.write_text(opening + '---\n' + json.dumps(body) + '\n---' + ending, encoding='utf8')
        dependent = self.worker('products')
        self.assertIsNone(self.manager.claim(dependent))
        self.assertEqual(self.row('TST-005')['status'], 'blocked')
        self.manager.configure_plan('TST-002', [{'id': 'verify', 'title': 'Verify', 'criteria': 'Proof exists', 'weight': 1}])
        provider = self.worker('agency/deep')
        claim = self.manager.claim(provider)
        self.manager.finish(provider, claim['lease_token'], outcome='completed', summary='Proof checked',
                            evidence=self.evidence('TST-002'))
        self.assertEqual(self.manager.claim(dependent)['project_id'], 'TST-005')

    def test_checkpoint_rejects_edited_record_and_preserves_original_metadata(self):
        worker = self.worker('agency/deep')
        claim = self.manager.claim(worker)
        path = self.records[claim['project_id']]
        old = path.read_text(encoding='utf8')
        token = claim['lease_token']
        with self.assertRaisesRegex(CoordinatorError, 'preserve metadata'):
            self.manager.apply_checkpoint(worker, token, expected_sha256=claim['record_sha256'],
                                          text=old.replace('unvalidated', 'commercially_validated') + '\nChanged')
        result = self.manager.apply_checkpoint(worker, token, expected_sha256=claim['record_sha256'],
                                               text=old + '\n## Checked fixture\n\nEvidence saved.\n')
        self.assertNotEqual(result['record_sha256'], claim['record_sha256'])
        self.assertIn('Evidence saved.', path.read_text(encoding='utf8'))
        path.write_text(old + '\nAn unrelated editor added text.\n', encoding='utf8')
        with self.assertRaisesRegex(CoordinatorError, 'Project record changed'):
            self.manager.guard_lease(worker, token, lambda _: self.fail('Stale work ran'))


if __name__ == '__main__':
    unittest.main()
