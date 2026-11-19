"""Only synthetic child processes and temporary markers are used."""
import pathlib, subprocess, sys, time, unittest, tempfile
import job_experiment as job

if len(sys.argv) > 1 and sys.argv[1] == 'worker':
    marker = pathlib.Path(sys.argv[2]); mode = sys.argv[3]
    if mode == 'child':
        subprocess.Popen([sys.executable, __file__, 'worker', str(marker), 'grandchild'])
        while not marker.exists(): time.sleep(.01)
        time.sleep(60)
    elif mode == 'grandchild':
        marker.write_text('child started', encoding='utf-8'); time.sleep(60)
    elif mode == 'marker': marker.write_text('should not run', encoding='utf-8')
    elif mode == 'success': sys.exit(0)
    elif mode == 'failure': sys.exit(7)
    sys.exit(0)

class JobExperimentTests(unittest.TestCase):
    def test_success_and_nonzero_are_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            for mode, code in [('success', 0), ('failure', 7)]:
                self.assertEqual(job.run([sys.executable, __file__, 'worker', str(pathlib.Path(d)/mode), mode], 5000)[:2], ('exited', code))
    def test_timeout_terminates_worker_and_child(self):
        with tempfile.TemporaryDirectory() as d:
            marker = pathlib.Path(d)/'child-started'
            status, code, count = job.run([sys.executable, __file__, 'worker', str(marker), 'child'], 3000)
            self.assertTrue(marker.exists(), 'grandchild did not start before deadline')
            self.assertEqual((status, code), ('timeout', 124))
            self.assertGreaterEqual(count, 2)
    def test_assignment_failure_never_runs_worker(self):
        with tempfile.TemporaryDirectory() as d:
            marker = pathlib.Path(d)/'marker'
            with self.assertRaises(OSError):
                job.run([sys.executable, __file__, 'worker', str(marker), 'marker'], 1000, True)
            self.assertFalse(marker.exists())
    def test_rejects_invalid_deadline(self):
        with self.assertRaises(ValueError): job.run([], 0)
if __name__ == '__main__': unittest.main(verbosity=2)
