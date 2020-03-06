'''
importing necessary libraries and tools
'''
#-------------------------#
import pandas as pd
import numpy as np
import psycopg2
import scipy.stats

import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.stats as stats
from statsmodels.formula.api import ols
from statsmodels.stats.diagnostic import linear_rainbow, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
#-------------------------#


def num_to_bin(list_of_cols):
    '''
    This function takes dataframe columns with numeric values representing categorical data.
    It returns the dataframe with the column values converted to binary: 1s representing the presence
    of a feature and 0s representing that the house did not have this feature
    '''
    for _ in range(len(list_of_cols)):
        list_of_cols[_] = list_of_cols[_].astype(bool).astype(int)
    return list_of_cols


def filter_and_groom(unfiltered_df):
    '''
    This function takes in our takes in our unfiltered data and returns a groomed dataframe with 
    the columns we are interested in, and their values cleaned and in a usable format
    '''

    '''
    selecting interested columns
    '''
    groomed_df = unfiltered_df[['pin', 'SalePrice', 'SqFtTotLiving', 'SqFtOpenPorch',
                                'SqFtEnclosedPorch', 'SqFtDeck', 'Bedrooms', 'BathHalfCount',
                                'Bath3qtrCount', 'BathFullCount', 'PowerLines', 'TrafficNoise',
                                'AirportNoise', 'TidelandShoreland', 'Stories',
                                'Condition', 'Area', 'DocumentDate', 'MtRainier', 'Olympics', 'Cascades',
                                'Territorial', 'SeattleSkyline', 'PugetSound',
                                'LakeWashington', 'LakeSammamish', 'SmallLakeRiverCreek',
                                'OtherView', 'WaterSystem', 'SewerSystem', 'OtherProblems', 'YrBuilt',
                                'YrRenovated', 'BldgGrade', 'Township', 'FpSingleStory', 'FpMultiStory']]
    '''
    convert OtherProblems and PowerLines column (Ys, Ns) into binary values
    '''

    for (i, item) in enumerate(groomed_df['OtherProblems']):
        if item == 'N':
            groomed_df['OtherProblems'][i] = 0
        elif item == 'Y':
            groomed_df['OtherProblems'][i] = 1
    for (i, item) in enumerate(groomed_df['PowerLines']):
        if item == 'N':
            groomed_df['PowerLines'][i] = 0
        elif item == 'Y':
            groomed_df['PowerLines'][i] = 1
    '''
    ViewScore is a composite of three views (SeattleSkyline, LakeWashington, LakeSammamish).  These three views were found to have the most impact on sale price and
    capturing variance in our model so we decided to use these three values summed as it's own feature.  This is not a
    score for the total quality of view from the house, simply views of these three features.
    '''
    columns = ['SeattleSkyline', 'LakeWashington', 'LakeSammamish']
    groomed_df['ViewScore'] = 0
    for column in columns:
        groomed_df['ViewScore'] = groomed_df['ViewScore'] + groomed_df[column]

    township_mean_sale_prices = {}
    for town in unfiltered_df['Township'].value_counts().index:
        township_mean_sale_prices[town] = groomed_df[groomed_df['Township']
                                                     == town]['SalePrice'].mean()
    groomed_df['TownshipMeanSalePrice'] = groomed_df['Township'].map(
        township_mean_sale_prices)
    groomed_df['TownshipMeanSalePrice'] = groomed_df['TownshipMeanSalePrice'].astype(
        int)
    groomed_df['ExpensiveForArea?'] = (
        groomed_df['SalePrice'] >= groomed_df['TownshipMeanSalePrice']).astype(int)

    groomed_df = groomed_df[groomed_df['SqFtTotLiving'] < 50000]
    groomed_df['PricePerSqFt'] = groomed_df['SalePrice'] / \
        groomed_df['SqFtTotLiving']
    groomed_df['TidelandShoreland'].value_counts()
    groomed_df['TidelandShoreland'], groomed_df['TrafficNoise'] = num_to_bin(
        [groomed_df['TidelandShoreland'], groomed_df['TrafficNoise']])
    groomed_df['YrRenovated'] = groomed_df['YrRenovated'].astype(int)

    return groomed_df


def load_and_wrangle_data(file_path):
    '''
    this function grabs the csv containing unfiltered housing data fom 2019
    and calls filter_and_groom to return an ungroomed and groomed version of our 2019 data
    '''
    ungroomed_df = pd.read_csv(file_path, encoding='latin-1')
    groomed_df = filter_and_groom(ungroomed_df)
    return ungroomed_df, groomed_df
