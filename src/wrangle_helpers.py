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

from sklearn.linear_model import LinearRegression
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
  selecting interested columns
  '''
  groomed_df = unfiltered_df[['pin', 'SalePrice', 'SqFtTotLiving', 'SqFtOpenPorch', 
                          'SqFtEnclosedPorch', 'SqFtDeck', 'Bedrooms', 'BathHalfCount', 
                          'Bath3qtrCount', 'BathFullCount','TidelandShoreland',
                          'TrafficNoise', 'Stories', 'Condition', 'Area', 
                          'DocumentDate', 'MtRainier', 'Olympics', 'Cascades', 
                          'Territorial', 'SeattleSkyline', 'PugetSound', 
                          'LakeWashington', 'LakeSammamish', 'SmallLakeRiverCreek', 
                          'OtherView','WaterSystem', 'SewerSystem', 'OtherProblems', 'YrBuilt', 
                          'YrRenovated', 'BldgGrade', 'Township', 'FpSingleStory', 'FpMultiStory']]
  '''
  convert 'otherproblems' column (Ys, Ns) into 1s and 0s
  '''
  mylist = groomed_df['OtherProblems']
  for (i, item) in enumerate(mylist):
    if item == 'N':
        mylist[i] = 0
    elif item == 'Y':
        mylist[i] = 1
  groomed_df['OtherProblems'] = mylist

  township_mean_sale_prices = {}
  for town in unfiltered_df['Township'].value_counts().index:
    township_mean_sale_prices[town] = groomed_df[groomed_df['Township'] == town]['SalePrice'].mean()
  groomed_df['TownshipMeanSalePrice'] = groomed_df['Township'].map(township_mean_sale_prices)
  groomed_df['TownshipMeanSalePrice'] = groomed_df['TownshipMeanSalePrice'].astype(int)
  groomed_df['ExpensiveForArea?'] = (groomed_df['SalePrice'] >= groomed_df['TownshipMeanSalePrice']).astype(int)


  groomed_df = groomed_df[groomed_df['SqFtTotLiving'] < 50000]
  groomed_df['PricePerSqFt'] = groomed_df['SalePrice']/groomed_df['SqFtTotLiving']
  groomed_df['TidelandShoreland'].value_counts()
  groomed_df['TidelandShoreland'], groomed_df['TrafficNoise'] = num_to_bin([groomed_df['TidelandShoreland'], groomed_df['TrafficNoise']])
  groomed_df['YrRenovated'] = groomed_df['YrRenovated'].astype(int)

  return groomed_df

def load_and_wrangle_data(file_path):
  '''
  
  '''
  ungroomed_df = pd.read_csv(file_path, encoding='latin-1')
  groomed_df = filter_and_groom(ungroomed_df)
  return ungroomed_df, groomed_df
