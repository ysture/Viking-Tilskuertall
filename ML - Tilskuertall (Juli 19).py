import sklearn
import numpy as np
import pandas as pd

spect = pd.read_csv('tilskuertall_160719.csv')

# List first 20 objects in the spect dataframe
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
spect.head(20)

# Change all '-' values in the df (except for in column [TV-kanal]) to NaN
spect.drop(columns='Unnamed: 0', axis=1)

# TODO: få til value_counts()['-'] for alle kolonner
# Count how many instances of '-' in each column in spect
spect[['Temp', 'Vind', 'Precip']].apply(lambda x: x.value_counts()['-'], axis=0)


# List types for all columns in spect
spect.dtypes

# Changes type all necessary columns
    # [Dato] to datetime
    spect['Dato'] = pd.to_datetime(spect['Dato'], dayfirst=True)
    # [Tilskuertall] to int
    spect['Tilskuertall'] = spect['Tilskuertall'].str.replace('\\xa0', '') # fjerner mellomrom (\xa0) som tusen-skilletegn
    spect['Tilskuertall'] = pd.to_numeric(spect['Tilskuertall'])
    # [Ukedag] to categorical
    spect['Ukedag'] = pd.Categorical(spect['Ukedag'])
    # [Hjemmelag] and [Bortelag] to categorical
    spect['Hjemmelag'] = pd.Categorical(spect['Hjemmelag'])
    spect['Bortelag'] = pd.Categorical(spect['Bortelag'])
    # [Resultat] to categorical
    spect['Resultat'] = pd.Categorical(spect['Resultat'])
    # [16. mai] to categorical
    spect['16. mai'] = pd.Categorical(spect['16. mai'])
    # For [Derby], first fill all NAs out with 0, and then turns into category
    spect['Derby'].fillna(0, inplace=True)
    spect['Derby'] = pd.Categorical(spect['Derby'])
    # Groups [TV-kanal] into three groups: no broadcasting, free broadcasting and exclusive broadcasting
        # Groups the channels
        dict_kanaler = {'Ingen': ['-', '', 'NaN'],
                        'Gratis':['Hovedkamp', 'NRK1', 'NRK2', 'TV2', 'TV 2 Zebra', 'TV2 (HD)', 'MAX', 'TVNorge', 'Eurosport Norge', 'Eurosport 1', 'VOX'],
                        'Betal':['Eurosport Player', 'Eurosport Pluss',
                                 'C More Live','C More Live 2', 'C More Live 3', 'C More Live 4', 'C More Live HD',
                                 'C More Hockey', 'C More Tennis', 'C More Extreme', 'C SPORTS', 'C More Fotball', 'C More Fotball HD',
                                 'TV2 Sumo', 'TV2 SPORT', 'TV 2 SPORT 1', 'TV 2 SPORT 2', 'TV 2 SPORT 3' , 'TV 2 SPORT 4', 'TV 2 SPORT 5', 'TV 2 SPORT 5 (HD)',
                                 'TV 2 Sport Premium 1', 'TV 2 Sport Premium 2', 'TV 2 Sport Premium 3', 'TV 2 Sport Premium 4',
                                 'TV 2 Sport Premium 5', 'TV 2 Sport Premium 6', 'TV 2 Sport Premium 7', 'TV 2 Sport Premium 8']}
        for ii, r in spect.iterrows():
            for key in dict_kanaler.keys():
                if spect.at[ii,'TV-kanal'] in dict_kanaler[key]:
                    spect.at[ii,'TV-kanal'] = key
    # [TV-kanaler] to category
    spect['TV-kanal'] = pd.Categorical(spect['TV-kanal'])
    # [Temp], [Vind] and [Precip], first make '-' values NaN, then convert column dtypes to float
    spect.replace('-',-100, inplace=True)
        spect.count() # Counts NAs after previous line has been run, shows that '-' values are turned into 'NaN' strings, not into actual NA values
    # [Temp], [Vind] and [Precip] to numeric (float)
    spect['Temp'] = pd.to_numeric(spect['Temp'])
    spect['Vind'] = pd.to_numeric(spect['Vind'])
    spect['Precip'] = pd.to_numeric(spect['Precip'])


# Descriptive statistics and simple visualization of the data set
import matplotlib.pyplot as plt


# Creates simple models to make prediction models of the data set
from sklearn import linear_model
regr = linear_model.LinearRegression()
regr.fit(X=spect[['Precip', 'Temp']], y=spect['Tilskuertall'])
