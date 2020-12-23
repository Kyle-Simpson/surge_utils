# -*- coding: utf-8 -*-
'''
    Name of Module: utils.py
    Contents:
        get_core_ref
        set_roots
        collapse (like STATA collapse)
        rowtotal (like STATA rowtotal)
        wide_to_long (reshape)
        long_to_wide (reshape)
        aggregate_long_draws
        aggregate_wide_draws
        add_ihme_loc_id
        add_location_name
        add_region_id
        add_region_name
        add_super_region_id
        add_super_region_name
        add_loc_lancet_label
        add_loc_who_label
        add_cause_id
        add_acause
        add_cause_name
        add_cause_lancet_label
        launch_qsub

    Description: Contains useful functions for data formatting, including
                 python versions of common STATA commands.
    Arguments: N/A -- to use, import surge_utils.py_utils.utils at the
                      top of your file with the rest of your import statement
    Output: N/A
    Contributors: Kyle Simpson
'''
# Import packages
import getpass
import json
import sys
import yaml
from datetime import datetime
from db_queries import (
    get_cause_metadata,
    get_location_metadata
)
import numpy as np
import pandas as pd

# Variable prep
code_repo = ''
if sys.platform.lower() == 'linux':
    code_repo = '/ihme/homes/{}/repos/surge_utils/'.format(getpass.getuser())
elif 'win' in sys.platform.lower():
    code_repo = 'H:/repos/surge_utils/'


#----# Root and Path Helpers #----# 
def get_core_ref(param_name, sub_key=None):
    ''' Convenience function to pull static reference from refs.yaml.

    Arguments:
    param_name : str
                 A string containing the reference desired.
    sub_key : str (optional)
              A string containing the sub-reference needed.
    '''
    # Error handling
    if param_name is None:
        raise ValueError('Supplied param_name is None. You must supply a value.')

    with open('{}refs.yaml'.format(code_repo)) as file:
        refs = yaml.full_load(file)
    
    if sub_key is None:
        return(refs[param_name])
    else:
        return(refs[param_name][sub_key])

def set_roots():
    ''' Convenience function to create root filepaths.

    Arguments:
    None

    Returns:
    roots : Dictionary
            A dictionary of root filepaths.
    '''
    roots = {'j' : '', 'h' : '', 'k' : '', 'share' : '', 'gbd_round' : '', 'gbd_year' : ''}

    if sys.platform.lower() == 'linux':
        roots['j'] = '/home/j/'
        roots['h'] = '/ihme/homes/{}/'.format(getpass.getuser())
        roots['k'] = '/ihme/cc_resources/'
        roots['share'] = '/ihme/'
    elif 'win' in sys.platform.lower():
        roots['j'] = 'J:/'
        roots['h'] = 'H:/'
        roots['k'] = 'K:/'
    
    roots['gbd_round'] = get_core_ref('gbd_round_id')
    roots['gbd_year'] = get_core_ref('gbd_year')

    return(roots)

roots = set_roots()
#----------------------------------#

#----# Data Manipulation and Calculation Functions #----# 
def collapse(df, agg_function='sum', group_cols=None, calc_cols=None):
    ''' Convenience function for STATA-like collapsing. Like STATA, removes
    any columns not specified in either group_cols or calc_cols.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    group_cols : str or list-like
                 Columns you want to use to group the data and collapse over.
    agg_function : str, default 'sum'
                   The aggregation function you wish to perform (sum, mean, min, max).
    calc_cols : str or list-like, default None
                Columns you want to compute the aggregation function over
                If no columns passed all columns will be aggregated (except
                group columns).
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input df is not a pandas DataFrame.')
    if agg_function not in ['sum', 'mean', 'min', 'max']:
        raise ValueError('Supplied agg_function not one of: sum, mean, min, max.')

    # Get columns and ensure proper var types
    if isinstance(group_cols, str):
        group_cols = [group_cols]
    # Get all columns other than group_cols if no calc_cols given
    if not calc_cols:
        calc_cols = [c for c in list(df) if c not in group_cols]
    if isinstance(calc_cols, str):
        calc_cols = [calc_cols]

    if any(col not in df.columns for col in group_cols):
        raise ValueError('One or more supplied group_cols not found in df columns.')
    if any(col not in df.columns for col in calc_cols):
        raise ValueError('One or more supplied calc_cols not found in df columns.')

    # Remove columns that are not included in group or aggregation calculation
    # (mimics STATA behavior)
    df = df[group_cols + calc_cols]
    g = df.groupby(group_cols)

    # Make the calculation
    if agg_function == 'sum':
        g = g[calc_cols].agg(np.sum)
    elif agg_function == 'mean':
        g = g[calc_cols].agg(np.mean)
    elif agg_function == 'min':
        g = g[calc_cols].agg(np.min)
    elif agg_function == 'max':
        g = g[calc_cols].agg(np.max)

    return g.reset_index()

def rowtotal(df, new_colname=None, rowtotal_cols=None):
    ''' Convenience function to perform STATA-like row total.

    Arguments:
    df: DataFrame
        A pandas DataFrame.
    new_colname : str
                  A string containing the name of the row totaled column.
    rowtotal_cols : str or list-like
                    A string or list containing the names of the existing columns
                    you wish to total.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input df is not a pandas DataFrame.')
    if new_colname in df.columns:
        raise ValueError('Supplied new_colname already exists in df.')
    # Get columns and ensure proper var types
    if isinstance(rowtotal_cols, str):
        rowtotal_cols = [rowtotal_cols]
    if any(col not in df.columns for col in rowtotal_cols):
        raise ValueError('One or more supplied rowtotal_cols not found in df columns.')

    # Make the calculation
    df[new_colname] = df[rowtotal_cols].sum(axis=1)

    return(df)

def wide_to_long(df, stubnames, i, j, new_index=False, drop_others=False):
    ''' A convenience function to reshape a DataFrame wide to long.

    Arguments:
    df : DataFrame
         The wide-format DataFrame.
    stub : str (can be regex)
           The stub name or a regex for getting columns with
           a stub name. This will match any column that contains the stub name
           by default. If you only want to match columns that start with
           stub name, for example, pass a regex (such as "^stub").
    i : str or list-like
        (Existing) Columns to use as id variables.
    j: str
        (New) Column with sub-observation variables.
    new_index : Boolean, default=False
                If true, will output a multi-indexed dataframe.
    drop_others : Boolean, default=False
                  If true, will drop columns not included in i, j, or stub.
                  Note that this won't work well with the desired future
                  development of being able to reshape multiple stubnames.
                  Consider which features are most important.
    '''
    def get_varnames(df, stub):
        return(df.filter(regex=stub).columns.tolist())

    def melt_stub(df, stub, newVarNm):
        varnames = get_varnames(df, stub)
        # Use all cols as ids
        ids = [c for c in df.columns.values if c not in varnames]
        newdf = pd.melt(df, id_vars=ids, value_vars=varnames,
                        value_name=stub, var_name=newVarNm)
        # remove 'stub' from observations in 'newVarNm' columns, then
        #   recast to int typeif numeric suffixes were used new
        try:
            if newdf[newVarNm].unique().str.isdigit().all():
                newdf[newVarNm] = newdf[newVarNm].str.replace(
                    stub, '').astype(int)
        except AttributeError:
            newdf[newVarNm] = newdf[newVarNm].str.replace(stub, '').astype(str)
        return newdf

    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if isinstance(i, str):
        i = [i]
    if isinstance(stubnames, str):
        stubnames = [stubnames]
    if isinstance(j, str):
        j = [j]
    if len(j) != len(stubnames):
        raise ValueError("Stub list must be same length as j list.")
    if any(map(lambda s: s in list(df), stubnames)):
        raise ValueError("Stubname can't be identical to a column name.")
    if df[i].duplicated().any():
        raise ValueError("The id variables don't uniquely identify each row.")

    # Start the reshaping (pop stub in prep for rewriting for multiple stubs)
    stubcols = []
    for s in stubnames:
        stubcols +=  get_varnames(df, s)
    non_stubs = [c for c in df.columns if c not in stubcols+i]
    for pos, stub in enumerate(stubnames):
        jval = j[pos]
        temp_df = df.copy()
        # Drop extra columns if requested
        if drop_others:
            temp_df = temp_df[i + get_varnames(df, stub)]
        else:
            temp_df = temp_df[i + get_varnames(df, stub) + non_stubs]
        # add melted data to output dataframe 
        if pos == 0:
            newdf = melt_stub(temp_df, stub, jval)
        else:
            newdf = newdf.merge(melt_stub(temp_df, stub, jval))

    if new_index:
        return newdf.set_index(i + j)
    else:
        return newdf

def long_to_wide(df, stub, i, j, drop_others=False):
    ''' Convenience function to reshape DataFrame long to wide.

    Arguments:
    df : DataFrame
         The long-format DataFrame.
    stub : str
          The stub name. Contains values in long format. The wide format
          columns will start with this stub name.
    i : str or list
        Columns to use as id variables. Together with `j`, should uniquely
        identify an observation in a row in `stub`.
    j : str
        Extant column with observations to use as suffix for the stub name.
    drop_others : bool, default=False
                  If true, will drop any columns not specified in either i or j.
                  Otherwise all columns will be included as additional
                  identifier columns.
    '''
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    
    if isinstance(i, str):
        i = [i]
    if isinstance(df.index, pd.core.index.MultiIndex):
        df = df.reset_index()
    # Error Checking
    if df[i + [j]].duplicated().any():
        raise ValueError("`i` and `j` don't uniquely identify each row.")
    if df[j].isnull().any():
        raise ValueError("`j` column has missing values. cannot reshape.")
    if df[j].astype(str).str.isnumeric().all():
        if df.loc[df[j] != df[j].astype(int), j].any():
            print(
                "Decimal values cannot be used in reshape suffix. {} coerced to integer".format(j))
        df.loc[:, j] = df[j].astype(int)
    else:
        df.loc[:, j] = df[j].astype(str)
    # Perform reshape
    if drop_others:
        df = df[i + [j]]
    else:
        i = [x for x in list(df) if x not in [stub, j]]
    df = df.set_index(i + [j]).unstack(fill_value=np.nan)
    # Ensure all stubs and suffixes are strings and join them to make col names
    cols = pd.Index(df.columns)
    # for each s in each col in cols, e.g. cols = [(s, s1), (s, s2)]
    cols = map(lambda col: map(lambda s: str(s), col), cols)
    cols = [''.join(c) for c in cols]
    # Set columns to the stub+suffix name and remove MultiIndex
    df.columns = cols
    df = df.reset_index()
    return df

def aggregate_long_draws(df, id_cols, value_col):
    ''' Convenience function which aggregates draws in long format.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    id_cols : str or list-like
              A single column name, or multiple which uniquely
              identify rows.
    value_col : str
                A single column name identifying draw values.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if isinstance(id_cols, str):
        id_cols = [id_cols]
    if len(id_cols) == 0:
        raise ValueError('Supplied id_cols are blank.')
    if any(c not in df.columns.values for c in id_cols):
        raise ValueError('One or more supplied id_cols are not in df columns.')
    for col in id_cols:
        if df[col].isnull().any():
            raise ValueError('Values in {} contain NAs. Please fix.'.format(col))
    if not isinstance(value_col, str):
        raise TypeError('Supplied value_col is not a string.')
    if len(value_col) == 0:
        raise ValueError('Supplied value_col is blank.')
    if value_col not in df.columns:
        raise ValueError('Supplied value_col not present in df columns.')
    if df[value_col].isnull().any():
        raise ValueError('Values in {} contain NAs. Please fix.'.format(value_col))

    t = df.drop_duplicates(id_cols)[id_cols]
    t['lower'] = df.groupby(id_cols)[value_col].quantile(0.025).values
    t['mean'] = df.groupby(id_cols)[value_col].mean().values
    t['upper'] = df.groupby(id_cols)[value_col].quantile(0.975).values

    return(t.reset_index())

def aggregate_wide_draws(df, draw_col_stub):
    ''' Convenience function which aggregates draws in wide format.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    draw_col_stub : str
                    A stub matching each column containing draws.
    '''
    # Error handing
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if len(draw_col_stub) == 0:
        raise ValueError('Supplied blank draw_col_stub.')
    if all(draw_col_stub not in c for c in df.columns.values):
        raise ValueError('Supplied draw_col_stub not found in any df columns.')
    draw_cols = df.columns.values
    draw_cols = draw_cols[np.array([draw_col_stub in c for c in draw_cols])]
    for col in draw_cols:
        if df[col].isnull().any():
            raise ValueError('Values in {} contain NAs. Please fix.'.format(col))

    keep_cols = df.columns.values
    keep_cols = keep_cols[np.array([draw_col_stub not in c for c in keep_cols])]

    t = df.drop_duplicates(keep_cols).reset_index()[keep_cols]
    t['lower'] = df[draw_cols].quantile(0.025, axis=1).values
    t['mean'] = df[draw_cols].mean(axis=1).values
    t['upper'] = df[draw_cols].quantile(0.975, axis=1).values

    return(t)

def add_loc_lancet_label(df):
    ''' Convenience function which returns DataFrame with lancet_label column.

    Arguments:
    df : DataFrame
        A pandas DataFrame
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id', 'location_id', 'location_name']):
        raise ValueError('Supplied df is missing column for ihme_loc_id, location_id, or location_name.')
    if 'lancet_label' in df.columns:
        if df['lancet_label'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['lancet_label']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name','lancet_label']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    else:
        t = pd.merge(df, locs, on='location_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_loc_who_label(df):
    ''' Convenience function which returns DataFrame with who_label column.

    Arguments:
    df : DataFrame
        A pandas DataFrame
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id', 'location_id', 'location_name']):
        raise ValueError('Supplied df is missing column for ihme_loc_id, location_id, or location_name.')
    if 'who_label' in df.columns:
        if df['who_label'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['who_label']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name','who_label']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    else:
        t = pd.merge(df, locs, on='location_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)
#-------------------------------------------------------#

#----# GBD Location Tools #----# 
def add_ihme_loc_id(df):
    ''' Convenience function which returns DataFrame with ihme_loc_id column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['location_id', 'location_name']):
        raise ValueError('Supplied df does not contain columns for location_id or location_name.')
    if 'ihme_loc_id' in df.columns:
        if df['ihme_loc_id'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['ihme_loc_id']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['location_id','location_name','ihme_loc_id']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    else :
        t = pd.merge(df, locs, on='location_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_location_name(df):
    ''' Convenience function which returns a DataFrame with location_name column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id', 'location_id']):
        raise ValueError('Supplied df does not contain columns for ihme_loc_id or location_id.')
    if 'location_name' in df.columns:
        if df['location_name'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['location_name']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    else:
        t = pd.merge(df, locs, on='location_id', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_region_id(df):
    ''' Convenience function which returns a DataFrame with region_id.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id','location_id','location_name','region_name']):
        raise ValueError('Supplied df does not contain column for ihme_loc_id, location_id, location_name, or region_name.')
    if 'region_id' in df.columns:
        if df['region_id'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['region_id']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name','region_id','region_name']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    elif 'location_name' in df.columns:
        t = pd.merge(df, locs, on='location_name', how='left')
    else :
        t = pd.merge(df, locs.drop_duplicates(subset=['region_id', 'region_name']), on='region_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_region_name(df):
    ''' Convenience function which returns a DataFrame with region_name column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id','location_id','location_name','region_id']):
        raise ValueError('Supplied df does not contain column for ihme_loc_id, location_id, location_name, or region_id.')
    if 'region_name' in df.columns:
        if df['region_name'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['region_name']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name','region_id','region_name']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    elif 'location_name' in df.columns:
        t = pd.merge(df, locs, on='location_name', how='left')
    else :
        t = pd.merge(df, locs.drop_duplicates(subset=['region_id', 'region_name']), on='region_id', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_super_region_id(df):
    ''' Convenience function which returns a DataFrame with super_region_id column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id', 'location_id','location_name',
                                                'region_id','region_name','super_region_name']):
        raise ValueError('Supplied df does not contain column for ihme_loc_id, location_id, location_name, region_id, region_name, or super_region_name.')
    if 'super_region_id' in df.columns:
        if df['super_region_id'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['super_region_id']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['ihme_loc_id','location_id','location_name','region_id','region_name','super_region_id','super_region_name']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    elif 'location_name' in df.columns:
        t = pd.merge(df, locs, on='location_name', how='left')
    elif 'region_id' in df.columns:
        t = pd.merge(df, locs.drop_duplicates(subset=['region_id', 'super_region_id']), on='region_id', how='left')
    elif 'region_name' in df.columns:
        t = pd.merge(df, locs.drop_duplicates(subset=['region_name', 'super_region_id']), on='region_name', how='left')
    else:
        t = pd.merge(df, locs.drop_duplicates(subset=['super_region_name', 'super_region_id']), on='super_region_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_super_region_name(df):
    ''' Convenience function which returns a DataFrame with super_region_name column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['ihme_loc_id', 'location_id','location_name',
                                                'region_id','region_name','super_region_id']):
        raise ValueError('Supplied df does not contain column for ihme_loc_id, location_id, location_name, region_id, region_name, or super_region_id.')
    if 'super_region_name' in df.columns:
        if df['super_region_name'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['super_region_name']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['location_id','ihme_loc_id','location_name','region_id','region_name','super_region_id','super_region_name']
    locs = get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'ihme_loc_id' in df.columns:
        t = pd.merge(df, locs, on='ihme_loc_id', how='left')
    elif 'location_id' in df.columns:
        t = pd.merge(df, locs, on='location_id', how='left')
    elif 'location_name' in df.columns:
        t = pd.merge(df, locs, on='location_name', how='left')
    elif 'region_id' in df.columns:
        t = pd.merge(df, locs.drop_duplicates(subset=['region_id', 'super_region_name']), on='region_id', how='left')
    elif 'region_name' in df.columns:
        t = pd.merge(df, locs.drop_duplicates(subset=['region_name', 'super_region_name']), on='region_name', how='left')
    else:
        t = pd.merge(df, locs.drop_duplicates(subset=['super_region_id', 'super_region_name']), on='super_region_id', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)
#------------------------------#

#----# GBD Cause Tools #----# 
def add_cause_id(df):
    ''' Convenience function which returns DataFrame with cause_id column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['acause', 'cause_name']):
        raise ValueError('Supplied df does not contain column for acause or cause_name.')
    if 'cause_id' in df.columns:
        if df['cause_id'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['cause_id']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['cause_id', 'acause', 'cause_name']
    causes = get_cause_metadata(cause_set_id=3, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'acause' in df.columns:
        t = pd.merge(df, causes, on='acause', how='left')
    else:
        t = pd.merge(df, causes, on='cause_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_acause(df):
    ''' Convenience function which returns DataFrame wich acause column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['cause_id', 'cause_name']):
        raise ValueError('Supplied df missing column for cause_id or cause_name.')
    if 'acause' in df.columns:
        if df['acause'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['acause']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['cause_id', 'acause', 'cause_name']
    causes = get_cause_metadata(cause_set_id=3, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'cause_id' in df.columns:
        t = pd.merge(df, causes, on='cause_id', how='left')
    else:
        t = pd.merge(df, causes, on='cause_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_cause_name(df):
    ''' Convenience function which returns DataFrame with cause_name column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['cause_id', 'acause']):
        raise ValueError('Supplied df missing column for cause_id or acause.')
    if 'cause_name' in df.columns:
        if df['cause_name'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['cause_name']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['cause_id', 'acause', 'cause_name']
    causes = get_cause_metadata(cause_set_id=3, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'cause_id' in df.columns:
        t = pd.merge(df, causes, on='cause_id', how='left')
    else:
        t = pd.merge(df, causes, on='acause', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)

def add_cause_lancet_label(df):
    ''' Convenience function which returns a DataFrame with lancet_label column.

    Arguments:
    df : DataFrame
         A pandas DataFrame.
    '''
    # Error handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Supplied df is not a pandas DataFrame.')
    if all(c not in df.columns.values for c in ['cause_id', 'acause', 'cause_name']):
        raise ValueError('Supplied df is missing column for cause_id, acause, or cause_name.')
    if 'lancet_label' in df.columns:
        if df['lancet_label'].notnull().all():
            return(df)

    ret_cols = list(df.columns) + ['lancet_label']
    gbd_rid = get_core_ref('gbd_round_id')
    d_step = get_core_ref('decomp_step')
    meta_cols = ['cause_id', 'acause', 'cause_name', 'lancet_label']
    causes = get_cause_metadata(cause_set_id=3, gbd_round_id=gbd_rid, decomp_step=d_step)[meta_cols]

    if 'cause_id' in df.columns:
        t = pd.merge(df, causes, on='cause_id', how='left')
    elif 'acause' in df.columns:
        t = pd.merge(df, causes, on='acause', how='left')
    else:
        t = pd.merge(df, causes, on='cause_name', how='left')

    # Remove any non-required cols
    t = t[ret_cols]
    return(t)
#---------------------------#

#----# QSUB Helpers #----# 
import subprocess
def launch_qsub(errors_path=roots['h'], output_path=roots['h'], job_name=None, queue='i.q', 
                cluster_project='ihme_general', num_threads=None, num_gigs=None, runtime=None, 
                script_path=None, script_language='python', extra_args=None):
    ''' Convenience function to launch a qsub on the cluster.

    Arguments:
    errors_path : str
                  String filepath to desired errors file.
    output_path : str
                  String filepath to desired output file.
    job_name : str
               String name of the job to be launched.
    queue : str
            String name of the queue the job should be launched
            in. E.x. i.q, all.q, long.q, etc..
    cluster_project : str
                      String name of the cluster project the job 
                      should be launched under.
    num_threads : int
                  Number of threads needed for the job.
    num_gigs : int
               Number of threads needed for the job.
    runtime : str
              String representation of time in HH:MM:SS the job
              requires to complete.
    script_path : str
                  A string containing the full filepath to the
                  script to be launched.
    script_language : str
                      A string containing the name of the language
                      of the script to be launched.
    extra_args : list-like
                 An optional list-like object of extra arguments.
    '''
    # Validate parameter types
    if not isinstance(errors_path, str):
        raise TypeError('Supplied errors_path is not a string.')
    if len(errors_path) == 0:
        errors_path = roots['h']

    if not isinstance(output_path, str):
        raise TypeError('Supplied output_path is not a string.')
    if len(output_path) == 0:
        output_path = roots['h']

    if not isinstance(job_name, str):
        raise TypeError('Supplied job_name is not a string.')
    if len(job_name) == 0:
        job_name = '{}_{}'.format(getpass.getuser(), datetime.date(datetime.now()))

    if not isinstance(queue, str):
        raise TypeError('Supplied queue is not a string.')
    if len(queue) == 0:
        queue = 'i.q'
    if queue not in ['i.q', 'all.q', 'long.q', 'd.q']:
        raise ValueError('Supplied queue is not a valid cluster queue.')

    if not isinstance(cluster_project, str):
        raise TypeError('Supplied cluster_project is not a string.')
    if len(cluster_project) == 0:
        cluster_project = 'ihme_general'

    if num_threads is None:
        raise TypeError('You must supply the number of threads required.')
    if not isinstance(num_threads, int):
        raise TypeError('Supplied num_threads is not an integer.')

    if num_gigs is None:
        raise TypeError('You must supply the number of gigabytes required.')
    if not isinstance(num_gigs, int):
        raise TypeError('Supplied num_gigs is not an integer.')

    if runtime is None:
        raise TypeError('You must supply the amount of time required in HH:MM:SS.')
    if not isinstance(runtime, str):
        raise TypeError('Supplied runtime is not a string in HH:MM:SS.')

    if script_language is None:
        raise TypeError('You must supply the language of the script to run.')
    if not isinstance(script_language, str):
        raise TypeError('Supplied script_language is not a string.')
    if script_language.lower() not in ['r', 'python']:
        raise ValueError('Supplied script language is not one of: r, python')
    if script_language.lower() == 'python':
        shell = '{}shell_python.sh'.format(code_repo)
    elif script_language.lower() == 'r':
        shell = '/ihme/singularity-images/rstudio/shells/execRscript.sh -i /ihme/singularity-images/rstudio/ihme_rstudio_4030.img -s'

    if script_path is None:
        raise TypeError('You must supply the path to the script to run.')
    if not isinstance(script_path, str):
        raise TypeError('Supplied script_path is not a string.')

    if extra_args is not None:
        if not isinstance(extra_args, list):
            raise TypeError('Supplied extra_args is not a list.')
    else:
        extra_args = ''

    qsub = ('qsub -e {}errors.txt '.format(errors_path),
            '-o {}output.txt '.format(output_path),
            '-N {} '.format(job_name),
            '-l archive=TRUE -q {} '.format(queue),
            '-P {} '.format(cluster_project),
            '-l fthread={} '.format(num_threads),
            '-l m_mem_free={}G '.format(num_gigs),
            '-l h_rt={} '.format(runtime),
            '{} '.format(shell),
            '{} '.format(script_path),
            '{}'.format(extra_args)
    ) 

    qsub = ''.join(qsub)

    print('  {} job submit using {} gigs, {} threads, and {} runtime.'.format(script_language.upper(), num_gigs, num_threads, runtime))
    
    subprocess.call(qsub, shell=True)
#------------------------# 