import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
from statsmodels.stats.diagnostic import linear_rainbow, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from itertools import combinations
import warnings

warnings.filterwarnings('ignore')


def stats_from_columns(df, list_of_cols, dependent = 'SalePrice'):
    """
    Returns a dictionary of statistical tests done on the columns of a dataframe
    
    Parameters
    ----------
    df: Data Frame holding the data for the statistical tests
    list_of_cols: Columns that will be compared for statistical testing as the independent variables
    dependent: The dependant variable column name 
               Default: SalePrice, this is the dependant variable for the project but it can be changed if needed
    
    Returns
    -------
    A dictionary of multiple statistical tests
    Keys: columns: Columns used as independent variables
          ols: the model of the multiple regression test
          rainbow: a rainbow stats test from the model
          homoscadasticity: homoscadasticity test based on the columns and model
          vif: variance inflation factor data frame for the independant variables with eachother. 
               is set to string None if there is only 1 independent variable
               if the test fails for whatever reason it will be set to 'VIF failed'
    """
    dct = {"columns" : list_of_cols}
    model = get_model(df, list_of_cols, dependent) 
    dct["ols"] = model
    dct['rainbow'] = get_rainbow(model)
    dct['homoscadasticity'] = get_homoscadasticity(df, list_of_cols, dependent, model)
    dct['vif'] = get_vif(df, list_of_cols)
    return dct

def get_model(df, list_of_cols, dependent = 'SalePrice'):
    formula = f"{dependent} ~ " + " + ".join(list_of_cols)
    return ols(formula = formula, data = df).fit()

def get_rainbow(fsm):
    rainbow_statistic, rainbow_p_value = linear_rainbow(fsm)
    return {'statistic' : rainbow_statistic, 'p-value' : rainbow_p_value}

def get_homoscadasticity(df, list_of_cols, dependent, fsm):
    y = df[dependent]
    y_hat = fsm.predict()
    lm, lm_p_value, fvalue, f_p_value = het_breuschpagan(y-y_hat, df[list_of_cols])
    return {"Lagrange Multiplier p-value" : lm_p_value, "F-statistic p-value" : f_p_value}
    
def get_vif(df, list_of_cols):
    try:
        if len(list_of_cols) > 1:
            rows = df[list_of_cols].values
            vif_df = pd.DataFrame()
            vif_df["VIF"] = [variance_inflation_factor(rows, i) for i in range(len(list_of_cols))]
            vif_df["feature"] = list_of_cols
            return vif_df
        else: return "None"
    except: return "VIF failed"
    
    
    
    
def stats_of_combinations(df, n, columns = None, filter_vif = True):
    """
    WARNING --- Can lead to a lot of CPU usage and memory usage
    Okay this is a lot. And is pretty stupid. It takes in a data frame and returns stats for all the combinations of n columns
    You can set filter_vif to false for smaller sizes of combinations (under 1000 resulting combinations)
        but I would reccomnd leaving it true for leager combinations 
    """
    cols = None
    if columns:
        if len(columns) < n:
            print('n cannot be greater than number of columns!')
            return None
        cols = columns
    else:
        cols = df.columns
        cols = np.delete(cols, np.argwhere(cols == 'SalePrice')[0][0])
    if n == 1: filter_vif = False
    combs = combinations(cols, n)
    combs = list(combs)
    comb_count = len(combs)
    print("Combinations to go through: " + str(comb_count))
    combination_list = []
    count = -1
    prcts = [i / 10.0 for i in range(11)]
    for i in combs:
        count += 1
        if count / comb_count > prcts[0]:
            print("Percent Done: " + str(int(100 * prcts[0])))
            del prcts[0]
            
        stats_dict = stats_from_columns(df, list(i))
        if filter_vif:
            if (stats_dict['vif']['VIF'] > 5).sum() == 0:
                combination_list.append(stats_dict)
        else:
            combination_list.append(stats_dict)
        if len(combination_list) > 100:
            combination_list = sort_by_r2(combination_list)
            del combination_list[100]
            
    print("Percent Done: 100")
    return combination_list
    
# These two methods are for filtering and sorting lists returned by stats_of_combinations
# or by lists of multiple stats_from_columns returns

def filter_vif(giant_list_thing, upper_vf = 5):
    return list(filter(lambda x: (x['vif']['VIF'] > upper_vf).sum() == 0, giant_list_thing))

def sort_by_r2(giant_list_thing):
    return sorted(giant_list_thing, key = lambda x: x['ols'].rsquared, reverse = True)