# -*- coding: utf-8 -*-
'''
    Description: Automated testing of GBD location helpers
    Contributors: Kyle Simpson
''' 
# Import packages
import unittest
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from surge_utils.py_utils.utils import (
    add_ihme_loc_id,
    add_location_name,
    add_region_id,
    add_region_name,
    add_super_region_id,
    add_super_region_name,
    add_loc_lancet_label,
    add_loc_who_label
)


class TestAddIHMELocId(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_ihme_loc_id(1)

    def test_missing_location_id(self):
        with self.assertRaises(ValueError):
            add_ihme_loc_id(pd.DataFrame({'year' : [2020]}))

    def test_perf_locs(self):
        df = pd.DataFrame({'location_id' : [1], 'ihme_loc_id' : ['G']})
        test = add_ihme_loc_id(df)
        assert_frame_equal(df, test)

    def test_add_ihme_loc_id_by_location_id(self):
        df = pd.DataFrame({'location_id' : [1]})
        df = add_ihme_loc_id(df)
        self.assertTrue(df['ihme_loc_id'][0], 'G')

    def test_add_ihme_loc_id_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Global']})
        df = add_ihme_loc_id(df)
        self.assertTrue(df['ihme_loc_id'][0], 'G')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'location_id' : [1]})
        df = add_ihme_loc_id(df)
        self.assertTrue(len(df.columns), 2)


class TestAddLocationName(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_location_name(1)
    
    def test_missing_colnames(self):
        df = pd.DataFrame({'year' : [2020]})
        with self.assertRaises(ValueError):
            add_location_name(df)

    def test_perf_locs(self):
        df = pd.DataFrame({'location_id' : [1], 'location_name' : ['Global']})
        test = add_location_name(df)
        assert_frame_equal(df, test)

    def test_add_location_name_by_loc_id(self):
        df = pd.DataFrame({'location_id' : [1]})
        test = add_location_name(df)
        self.assertEqual(test['location_name'][0], 'Global')
    
    def test_add_location_name_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['G']})
        test = add_location_name(df)
        self.assertEqual(test['location_name'][0], 'Global')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'ihme_loc_id' : ['G']})
        test = add_location_name(df)
        self.assertEqual(len(test.columns), 2)


class TestAddRegionId(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_region_id(1)

    def test_missing_colnames(self):
        df = pd.DataFrame({'year' : [2020]})
        with self.assertRaises(ValueError):
            add_region_id(df)

    def test_perf_regions(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2'], 'region_id' : [32]})
        test = add_region_id(df)
        assert_frame_equal(df, test)

    def test_add_region_id_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_region_id(df)
        self.assertEqual(test['region_id'][0], 32)

    def test_add_region_id_by_location_id(self):
        df = pd.DataFrame({'location_id' : [32]})
        test = add_region_id(df)
        self.assertEqual(test['region_id'][0], 32)

    def test_add_region_id_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Central Asia']})
        test = add_region_id(df)
        self.assertEqual(test['region_id'][0], 32)

    def test_add_region_id_by_region_name(self):
        df = pd.DataFrame({'region_name' : ['Central Asia']})
        test = add_region_id(df)
        self.assertEqual(test['region_id'][0], 32)

    def test_no_extra_cols(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_region_id(df)
        self.assertEqual(len(test.columns), 2)


class TestAddRegionName(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_region_name(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_region_name(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_regions(self):
        df = pd.DataFrame({'ihme_loc_id' : ['G'], 'region_name' : ['Global']})
        test = add_region_name(df)
        assert_frame_equal(df, test)

    def test_add_region_name_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_region_name(df)
        self.assertEqual(test['region_name'][0], 'Central Asia')

    def test_add_region_name_by_location_id(self):
        df = pd.DataFrame({'location_id' : [32]})
        test = add_region_name(df)
        self.assertEqual(test['region_name'][0], 'Central Asia')

    def test_add_region_name_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Central Asia']})
        test = add_region_name(df)
        self.assertEqual(test['region_name'][0], 'Central Asia')

    def test_add_region_name_by_region_id(self):
        df = pd.DataFrame({'region_id' : [32]})
        test = add_region_name(df)
        self.assertEqual(test['region_name'][0], 'Central Asia')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_region_name(df)
        self.assertEqual(len(test.columns), 2)


class TestAddSuperRegionId(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_super_region_id(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_super_region_id(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_regions(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2'], 'super_region_id' : [31]})
        test = add_super_region_id(df)
        assert_frame_equal(df, test)

    def test_add_super_region_id_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_add_super_region_id_by_location_id(self):
        df = pd.DataFrame({'location_id' : [32]})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_add_super_region_id_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Central Asia']})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_add_super_region_id_by_region_id(self):
        df = pd.DataFrame({'region_id' : [32]})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_add_super_region_id_by_region_name(self):
        df = pd.DataFrame({'region_name' : ['Central Asia']})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_add_super_region_id_by_super_region_name(self):
        df = pd.DataFrame({'super_region_name' : ['Central Europe, Eastern Europe, and Central Asia']})
        test = add_super_region_id(df)
        self.assertEqual(test['super_region_id'][0], 31)

    def test_no_extra_cols(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_super_region_id(df)
        self.assertEqual(len(test.columns), 2)


class TestAddSuperRegionName(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_super_region_name(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_super_region_name(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_regions(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2'], 'super_region_name' : ['Central Europe, Eastern Europe, and Central Asia']})
        test = add_super_region_name(df)
        assert_frame_equal(df, test)

    def test_add_super_region_name_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_add_super_region_name_by_location_id(self):
        df = pd.DataFrame({'location_id' : [32]})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_add_super_region_name_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Central Asia']})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_add_super_region_name_by_region_id(self):
        df = pd.DataFrame({'region_id' : [32]})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_add_super_region_name_by_region_name(self):
        df = pd.DataFrame({'region_name' : ['Central Asia']})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_add_super_region_name_by_super_region_id(self):
        df = pd.DataFrame({'super_region_id' : [31]})
        test = add_super_region_name(df)
        self.assertEqual(test['super_region_name'][0], 'Central Europe, Eastern Europe, and Central Asia')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2']})
        test = add_super_region_name(df)
        self.assertEqual(len(test.columns), 2)


class TestAddLocLancetLabel(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_loc_lancet_label(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_loc_lancet_label(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_labels(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2'], 'lancet_label' : ['Global']})
        test = add_loc_lancet_label(df)
        assert_frame_equal(df, test)

    def test_add_loc_lancet_label_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['G']})
        test = add_loc_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'Global')

    def test_add_loc_lancet_label_by_location_id(self):
        df = pd.DataFrame({'location_id' : [1]})
        test = add_loc_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'Global')

    def test_add_loc_lancet_label_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Global']})
        test = add_loc_lancet_label(df)
        self.assertEqual(test['lancet_label'][0], 'Global')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'location_name' : ['Global']})
        test = add_loc_lancet_label(df)
        self.assertEqual(len(test.columns), 2)


class TestAddLocWHOLabel(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            add_loc_who_label(df=1)

    def test_missing_colnames(self):
        with self.assertRaises(ValueError):
            add_loc_who_label(df = pd.DataFrame({'year' : [2020]}))

    def test_perf_labels(self):
        df = pd.DataFrame({'ihme_loc_id' : ['R2'], 'who_label' : ['Global']})
        test = add_loc_who_label(df)
        assert_frame_equal(df, test)

    def test_add_loc_who_label_by_ihme_loc_id(self):
        df = pd.DataFrame({'ihme_loc_id' : ['G']})
        test = add_loc_who_label(df)
        self.assertEqual(test['who_label'][0], 'Global')

    def test_add_loc_who_label_by_location_id(self):
        df = pd.DataFrame({'location_id' : [1]})
        test = add_loc_who_label(df)
        self.assertEqual(test['who_label'][0], 'Global')

    def test_add_loc_who_label_by_location_name(self):
        df = pd.DataFrame({'location_name' : ['Global']})
        test = add_loc_who_label(df)
        self.assertEqual(test['who_label'][0], 'Global')

    def test_no_extra_cols(self):
        df = pd.DataFrame({'location_name' : ['Global']})
        test = add_loc_who_label(df)
        self.assertEqual(len(test.columns), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)