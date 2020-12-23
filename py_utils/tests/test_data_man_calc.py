# -*- coding: utf-8 -*-
'''
    Description: Automated testing of Data Manipulation and 
                 Calculation functions
    Contributors: Kyle Simpson
''' 
# Import packages
import getpass
import unittest
import yaml
import numpy as np
import pandas as pd
from surge_utils.py_utils.utils import (
    collapse,
    rowtotal,
    wide_to_long,
    long_to_wide,
    aggregate_long_draws,
    aggregate_wide_draws
)

class TestCollapse(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            collapse(df = None)

    def test_bad_agg_function(self):
        with self.assertRaises(ValueError):
            df = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5]})
            collapse(df, 'mat', group_cols='year', calc_cols='total')

    def test_bad_group_col_names(self):
        with self.assertRaises(ValueError):
            df = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5]})
            collapse(df, 'sum', group_cols='yr', calc_cols='total')

    def test_bad_calc_col_names(self):
        with self.assertRaises(ValueError):
            df = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5]})
            collapse(df, 'sum', group_cols='year', calc_cols='tot')

    def test_proper_collapse(self):
        dt = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5]})
        self.assertEqual(collapse(df=dt, agg_function='sum', group_cols=['year'], 
                            calc_cols=['total'])['total'][0], 15)
    
    def test_na_collapse(self):
        dt = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,np.nan,4,5]})
        self.assertEqual(collapse(df=dt, agg_function='sum', group_cols=['year'], 
                            calc_cols=['total'])['total'][0], 12)


class TestRowtotal(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            rowtotal(df = None)

    def test_existing_new_colname(self):
        with self.assertRaises(ValueError):
            df = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5], 'other_tot' : [1,2,3,4,5]})
            rowtotal(df, 'total', ['other_total'])

    def test_bad_rowtotal_cols(self):
        with self.assertRaises(ValueError):
            df = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5], 'other_tot' : [1,2,3,4,5]})
            rowtotal(df, 'new_total', ['tatal'])

    def test_rowtotal(self):
        dt = pd.DataFrame({'year' : np.full([5], 2020), 'total' : [1,2,3,4,5], 'other_tot' : [1,2,3,4,5]})
        self.assertTrue(rowtotal(dt, 'new_total', ['total', 'other_tot'])['new_total'][3], 8)


class TestWideToLong(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            wide_to_long(df = None, stubnames='', i='', j='')

    def test_stub_list(self):
        with self.assertRaises(ValueError):
            wide_to_long(df = pd.DataFrame(), stubnames=['this', 'that'], i='', j='this')

    def test_stub_name(self):
        with self.assertRaises(ValueError):
            wide_to_long(df = pd.DataFrame({'this' : [1]}), stubnames=['this'], i='', j='this')

    def test_dup_rows(self):
        with self.assertRaises(ValueError):
            wide_to_long(df = pd.DataFrame({'this' : [1,1]}), stubnames='that', i='this', j='that')

    def test_reshape(self):
        df = df = pd.DataFrame({
            'famid': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'birth': [1, 2, 3, 1, 2, 3, 1, 2, 3],
            'ht1': [2.8, 2.9, 2.2, 2, 1.8, 1.9, 2.2, 2.3, 2.1],
            'ht2': [3.4, 3.8, 2.9, 3.2, 2.8, 2.4, 3.3, 3.4, 2.9]
        })
        test = wide_to_long(df, stubnames='ht', i=['famid', 'birth'], j='age')

        self.assertTrue(len(test),  18)
        self.assertTrue(len(test.columns), 4)


class TestLongToWide(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            long_to_wide(df = None, stub='', i='', j='')

    def test_dup_rows(self):
        with self.assertRaises(ValueError):
            long_to_wide(df = pd.DataFrame({'this' : [1,1], 'that' : [1,1]}), 
                                stub='', i='this', j='that')

    def test_null_j_param(self):
        with self.assertRaises(ValueError):
            long_to_wide(df = pd.DataFrame({'this' : [1,1], 'that' : [1,np.nan]}), 
                                stub='', i='this', j='that')

    def test_reshape(self):
        df = pd.DataFrame({
            'famid': [1,1,1,2,2,2,3,3,3,1,1,1,2,2,2,3,3,3],
            'birth': [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3],
            'age': [1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2],
            'ht': [2.8,2.9,2.2,2.0,1.8,1.9,2.2,2.3,2.1,3.4,3.8,2.9,3.2,2.8,2.4,3.3,3.4,2.9]
        })
        test = long_to_wide(df, stub='ht', i=['famid', 'birth'], j='age')

        self.assertTrue(len(test),  8)
        self.assertTrue(len(test.columns), 4)


class TestAggregateLongDraws(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            aggregate_long_draws(df=1, id_cols='', value_col='')

    def test_bad_id_cols_length(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame(), id_cols='', value_col='')

    def test_missing_id_col(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019]}), 
                                    id_cols='location_id', value_col='')

    def test_na_id_col_vals(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019, np.nan, 2019], 'draw_id' : [1,1,1], 'val' : [1,1,1]}), 
                                    id_cols='year', value_col='val')

    def test_bad_value_col_type(self):
        with self.assertRaises(TypeError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019], 'draw_id' : [1]}), 
                                    id_cols='year', value_col=1)

    def test_bad_value_col_length(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019], 'draw_id' : [1]}), 
                                    id_cols='year', value_col='')

    def test_missing_value_col(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019], 'draw_id' : [1], 'val' : [1]}), 
                                    id_cols='year', value_col='value')
    
    def test_na_value_col_vals(self):
        with self.assertRaises(ValueError):
            aggregate_long_draws(df=pd.DataFrame({'year' : [2019, 2019, 2019], 'draw_id' : [1,1,1], 'val' : [1,np.nan,1]}), 
                                    id_cols='year', value_col='val')

    def test_aggregate_long_draws(self):
        df = pd.DataFrame({
            'year' : [2019, 2019, 2020, 2020],
            'location_id' : [1, 1, 1, 1],
            'draw_num' : [1, 2, 1, 2],
            'draw_val' : [0, 1, 0, 1]
        })
        test = aggregate_long_draws(df=df, id_cols=['year', 'location_id'], value_col='draw_val')
        self.assertEqual(test['lower'][0], 0.025)
        self.assertEqual(test['mean'][0], 0.5)
        self.assertEqual(test['upper'][0], 0.975)


class TestAggregateWideDraws(unittest.TestCase):
    def test_non_dataframe(self):
        with self.assertRaises(TypeError):
            aggregate_wide_draws(df=1, draw_col_stub='')

    def test_bad_draw_col_stub_length(self):
        with self.assertRaises(ValueError):
            aggregate_wide_draws(df=pd.DataFrame(), draw_col_stub='')

    def test_bad_draw_col_stub(self):
        with self.assertRaises(ValueError):
            aggregate_wide_draws(df=pd.DataFrame({'year' : [2020]}), draw_col_stub='tree')

    def test_na_draw_col_stub_vals(self):
        with self.assertRaises(ValueError):
            aggregate_wide_draws(df=pd.DataFrame({'year' : [1, np.nan]}), draw_col_stub='year')

    def test_aggregate_wide_draws(self):
        df = pd.DataFrame({
            'year' : [2019, 2020],
            'location_id' : [1, 1],
            'draw_1' : [0, 0],
            'draw_2' : [1, 1]
        })
        test = aggregate_wide_draws(df, 'draw_')
        self.assertEqual(test['lower'][0], 0.025)
        self.assertEqual(test['mean'][0], 0.5)
        self.assertEqual(test['upper'][0], 0.975)

        
if __name__ == '__main__':
    unittest.main(verbosity=2)