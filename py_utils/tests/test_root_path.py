# -*- coding: utf-8 -*-
'''
    Description: Automated testing of Root & Path functions
    Contributors: Kyle Simpson
''' 
# Import packages
import getpass
import unittest
import yaml
from surge_utils.py_utils.utils import (
    code_repo,
    get_core_ref,
    set_roots
)


class TestGetCoreRef(unittest.TestCase):
    def test_none_param_name(self):
        with self.assertRaises(ValueError):
            get_core_ref(param_name=None)

    def test_get_core_ref(self):
        test = get_core_ref('gbd_round_id')
        with open('{}refs.yaml'.format(code_repo)) as file:
            gbd_rid = yaml.full_load(file)['gbd_round_id']
        self.assertTrue(test, gbd_rid)


class TestSetRoots(unittest.TestCase):
    def test_proper_h(self):
        h = '/ihme/homes/{}/'.format(getpass.getuser())
        roots = set_roots()
        self.assertEqual(h, roots['h'])


if __name__ == '__main__':
    unittest.main(verbosity=2)