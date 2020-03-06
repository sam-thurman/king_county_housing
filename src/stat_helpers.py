#-------------------------#
import pandas as pd
import numpy as np
import psycopg2
import scipy.stats

import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.stats as stats
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.diagnostic import linear_rainbow, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
#-------------------------#


def welch_ttest(df, col_name):
    '''
    Takes in a dataframe and a column name (as str) Performs a welch's t-test on a column of binary data
    '''
    select_0s = df[df[col_name] == 0]['SalePrice']
    select_1s = df[df[col_name] == 1]['SalePrice']
    p_val = scipy.stats.ttest_ind(select_0s, select_1s, equal_var=False).pvalue
    t_stat = scipy.stats.ttest_ind(
        select_1s, select_0s, equal_var=False).statistic
    return ('p-value: ', p_val, 't-statistic: ', t_stat)


def bootstrapped_ttest_bin(df, col_name):
    '''
    Function takes in a dataframe and a column name as a string.

    Performs a two-sided t-test against the sale price and 0 and 
    1 values of the given column(binary data) of 1000 samples.
    '''
    select_0s = df[df[col_name] == 0]['SalePrice']
    select_1s = df[df[col_name] == 1]['SalePrice']
    Ps = []
    Ts = []
    for _ in range(0, 1000):
        falsy_sample = np.random.choice(select_0s, size=50, replace=False)
        truthy_sample = np.random.choice(select_1s, size=50, replace=False)
        p_val = scipy.stats.ttest_ind(falsy_sample, truthy_sample).pvalue
        t_stat = scipy.stats.ttest_ind(truthy_sample, falsy_sample).statistic
        Ps.append(p_val)
        Ts.append(t_stat)

    return 'p-value: ', np.array(Ps).mean(), 'statistic: ', np.array(Ts).mean()


def cohen_d(x, y):
    '''
    This function takes in x and y data for a feature (binary data: two subsets of the column where valus = 0 and 1).
    Returns Cohen's D, measure of effect size of a feature
    '''
    nx = len(x)
    ny = len(y)
    sx = np.std(x)
    sy = np.std(y)
    numer = (nx-1)*sx**2 + (ny-1)*sy**2
    denom = nx + ny - 2
    pool_std = np.sqrt(numer/denom)
    return abs(np.mean(x) - np.mean(y))/pool_std
