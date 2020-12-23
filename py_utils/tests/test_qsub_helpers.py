# -*- coding: utf-8 -*-
'''
    Description: Automated testing of QSUB Helpers
    Contributors: Kyle Simpson
''' 
# Import packages
import sys
import unittest
from surge_utils.py_utils.utils import (
    code_repo,
    launch_qsub
)

# @contextmanager
# def captured_output():
#     new_out, new_err = StringIO(), StringIO()
#     old_out, old_err = sys.stdout, sys.stderr
#     try:
#         sys.stdout, sys.stderr = new_out, new_err
#         yield sys.stdout, sys.stderr
#     finally:
#         sys.stdout, sys.stderr = old_out, old_err

class TestQsub(unittest.TestCase):
    def test_bad_errors_path_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(errors_path=1)
    
    def test_bad_output_path_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(output_path=1)

    def test_bad_job_name_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name=1)

    def test_bad_queue_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue=1)
    def test_bad_queue_value(self):
        with self.assertRaises(ValueError):
            launch_qsub(job_name='t', queue='t.q')

    def test_bad_cluster_project_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', cluster_project=1)

    def test_missing_num_threads(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=None)
    def test_bad_num_threads_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads='t')

    def test_missing_num_gigs(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=None)
    def test_bad_num_gigs_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs='t')

    def test_missing_runtime(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, runtime=None)
    def test_bad_runtime_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, runtime=1)

    def test_missing_script_language(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language=None)
    def test_bad_script_language_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language=1)
    def test_bad_script_language_value(self):
        with self.assertRaises(ValueError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language='Java')

    def test_missing_script_path(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language='r', script_path=None)
    def test_bad_script_path_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language='r', script_path=1)

    def test_bad_extra_args_type(self):
        with self.assertRaises(TypeError):
            launch_qsub(job_name='t', queue='i.q', num_threads=1, num_gigs=1, 
                                runtime='01:00:00', script_language='r', script_path='this',
                                extra_args={'arg1' : 1})

    def test_proper_use_py_script(self):
        launch_qsub(job_name='test', num_threads=1, num_gigs=1, runtime='00:02:00', 
                    script_path='{}py_utils/tests/test_root_path.py'.format(code_repo))
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip() # because stdout is an StringIO instance
        self.assertEqual(output, 'PYTHON job submit using 1 gigs, 1 threads, and 00:02:00 runtime.')

    def test_proper_use_r_script(self):
        launch_qsub(job_name='test', num_threads=1, num_gigs=1, runtime='00:02:00', 
                    script_language='r', script_path='{}r_utils/tests/test_root_path.R'.format(code_repo))
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip() # because stdout is an StringIO instance
        self.assertEqual(output, 'R job submit using 1 gigs, 1 threads, and 00:02:00 runtime.')

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)