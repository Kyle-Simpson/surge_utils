# -*- coding: utf-8 -*-
'''
    Description: Automated testing of GBD Cause Helpers
    Contributors: Kyle Simpson
''' 
# Import packages
import pandas as pd
import unittest
from pandas.util.testing import assert_frame_equal
from surge_utils.py_utils.utils import (
    add_cause_id,
    add_acause,
    add_cause_name,
    add_cause_lancet_label
)


class TestAddCauseID(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_cause_id(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_cause_id(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_cause_ids(self):
        df = pd.DataFrame({'cause_name' : ['All causes'], 'cause_id' : [294]})
        test = add_cause_id(df)
        assert_frame_equal(df, test)

    def test_add_cause_id_by_acause(self):
        df = pd.DataFrame({'acause' : ['_all']})
        test = add_cause_id(df)
        self.assertEqual(test['cause_id'][0], 294)

    def test_add_cause_id_by_cause_name(self):
        df = pd.DataFrame({'cause_name' : ['All causes']})
        test = add_cause_id(df)
        self.assertEqual(test['cause_id'][0], 294)

    def test_no_extra_cols(self):
        df = pd.DataFrame({'cause_name' : ['All causes']})
        test = add_cause_id(df)
        self.assertEqual(len(test.columns), 2)


class TestAddAcause(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_acause(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_acause(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_acause(self):
        df = pd.DataFrame({'cause_id' : [294], 'acause' : ['_all']})
        test = add_acause(df)
        assert_frame_equal(df, test)

    def test_add_acause_by_cause_id(self):
        df = pd.DataFrame({'cause_id' : [294]})
        test = add_acause(df)
        self.assertEqual(test['acause'][0], '_all')

    def test_add_acause_by_cause_name(self):
        df = pd.DataFrame({'cause_name' : ['All causes']})
        test = add_acause(df)
        self.assertEqual(test['acause'][0], '_all')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'cause_name' : ['All causes']})
        test = add_acause(df)
        self.assertEqual(len(test.columns), 2)


class TestAddCauseName(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_cause_name(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_cause_name(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_cause_name(self):
        df = pd.DataFrame({'cause_id' : [294], 'cause_name' : ['All causes']})
        test = add_cause_name(df)
        assert_frame_equal(df, test)

    def test_add_cause_name_by_cause_id(self):
        df = pd.DataFrame({'cause_id' : [294]})
        test = add_cause_name(df)
        self.assertEqual(test['cause_name'][0], 'All causes')

    def test_add_cause_name_by_acause(self):
        df = pd.DataFrame({'acause' : ['_all']})
        test = add_cause_name(df)
        self.assertEqual(test['cause_name'][0], 'All causes')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'acause' : ['_all']})
        test = add_cause_name(df)
        self.assertEqual(len(test.columns), 2)


class TestAddCauseLancetLabel(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_cause_lancet_label(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_cause_lancet_label(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_cause_name(self):
        df = pd.DataFrame({'cause_id' : [294], 'lancet_label' : ['All causes']})
        test = add_cause_lancet_label(df)
        assert_frame_equal(df, test)

    def test_add_cause_lancet_label_by_cause_id(self):
        df = pd.DataFrame({'cause_id' : [294]})
        test = add_cause_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'All causes')

    def test_add_cause_lancet_label_by_acause(self):
        df = pd.DataFrame({'acause' : ['_all']})
        test = add_cause_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'All causes')

    def test_add_cause_lancet_label_by_cause_name(self):
        df = pd.DataFrame({'cause_name' : ['All causes']})
        test = add_cause_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'All causes')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'acause' : ['_all']})
        test = add_cause_lancet_label(df)
        self.assertEqual(len(test.columns), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)