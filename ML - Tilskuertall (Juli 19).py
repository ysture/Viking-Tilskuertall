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
    #TODO fiks [Mål forrige hjemmekamp] to integer
# spect['Mål forrige hjemmekamp'] =  pd.to_numeric(spect['Mål forrige hjemmekamp'])
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
    # [Form1] to category
spect['Form1'] = pd.Categorical(spect['Form1'])
    # [Temp], [Vind] and [Precip], first make '-' values NaN, then convert column dtypes to float
spect.replace('-',-100, inplace=True)
spect.count() # Counts NAs after previous line has been run, shows that '-' values are turned into 'NaN' strings, not into actual NA values
    # [Temp], [Vind] and [Precip] to numeric (float)
spect['Temp'] = pd.to_numeric(spect['Temp'])
spect['Vind'] = pd.to_numeric(spect['Vind'])
spect['Precip'] = pd.to_numeric(spect['Precip'])


# Descriptive statistics of the data set


# Simple visualization of the data set
import matplotlib.pyplot as plt
# Converts date column from datetime64 to datetime.date
from datetime import datetime
plt.plot(pd.to_datetime(spect['Dato'][spect['Hjemmelag']=='Viking'].to_numpy()),spect['Tilskuertall'][spect['Hjemmelag']=='Viking']) # Only plots Viking's spectator numbers

# Plots all time series in a grid
x=0
for team in set(spect['Hjemmelag']):
    x+=1
    plt.subplot(4, 7, x)
    plt.plot(pd.to_datetime(spect['Dato'][spect['Hjemmelag']==team].to_numpy()),spect['Tilskuertall'][spect['Hjemmelag']==team])
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False)

# Plots all time series with more than 200 home matches in the same plot to compare the spectator numbers)
'''for team in set(spect['Hjemmelag']):
    if len(spect['Tilskuertall'][spect['Hjemmelag']==team]) > 230:
        plt.plot(pd.to_datetime(spect['Dato'][spect['Hjemmelag']==team & (spect['Dato'] > '2003-01-01') & (spect['Dato'] < '2005-01-01')].to_numpy()),spect['Tilskuertall'][spect['Hjemmelag']==team])
'''
# TODO: Lag deseasonalized tidsserier der sesongvariasjoner er tatt ut (X11?). De to neste linjene fungerer ikke slik det står nå, på grunn av irregulære observasjonsintervaller. Hva er beste måten å løse dette på? Enten å ha sesongvise, ukentlige kamper med interpolated values eller noe annet.
#import statsmodels.api as sm
#res = sm.tsa.seasonal_decompose(spect['Tilskuertall'][spect['Hjemmelag']=='Viking'])


# Preprocessing (remove NAs and convert to categorical columns that can be handled by sklearn)
# Drop NAs and select which columns to use in the model
nanSpect = spect.dropna()
nanSpect = nanSpect[['Hjemmelag','Form1','TV-kanal','Ukedag','16. mai','Vind','Precip', 'Temp', 'Tilskuertall']]

# Convert to categorical columns that can be handled by ML algorithms in sklearn
from sklearn.preprocessing import OneHotEncoder
categorical_columns = ['Hjemmelag', 'Form1', 'TV-kanal', 'Ukedag','16. mai']
onehotencoder = sklearn.preprocessing.OneHotEncoder()
nanSpectEncoded = onehotencoder.fit_transform(nanSpect[categorical_columns]).toarray()
onehotencoder.categories_ # Displays all categories in the categorical columns that are now encoded

# Create simple linear regression model of the data (without test and train data)
from sklearn import linear_model
regr = linear_model.LinearRegression() # Create regression element to in linear regression model
regr.fit(X=nanSpectEncoded, y=nanSpect['Tilskuertall']) # Create model with X (predictors) and y (dependent variable)
regr.coef_ # Display coefficients
preds = regr.predict(nanSpectEncoded) # List predictions of stadium attendances
regr.score(nanSpectEncoded, nanSpect['Tilskuertall']) # In-sample R^2 score
# Linear regression model with train and test set
year = spect['Dato'].apply(lambda x: datetime.strptime(x, "%d.%m.%Y").year) # Create a year column to be able to index out test set based on year (2018 is test set)
test_y = nanSpect['Tilskuertall'][year == 2018] # Dependent variable test set
train_y = nanSpect['Tilskuertall'][year != 2018] # Dependent variable train set
x_array = onehotencoder.fit_transform(nanSpect[categorical_columns]).toarray() # Splits dependent variables into train and test set (first using onehotencoder, then indexing into train_x and test_x using length of test set
test_x = x_array[-len(test_y):]
train_x = x_array[:-len(test_y)]

regr_oos = linear_model.LinearRegression()
regr_oos.fit(X=train_x, y=train_y)
regr_oos.coef_
preds_oos = regr_oos.predict(X=test_x)
regr_oos.score(train_x, train_y) # In-sample R^2 score (with test set)
regr_oos.score(test_x, test_y) # Out-of-sample R^2 score



# Noe er rat med regr_oos.score, prøver å debugge og finne ut hva som er galt. Ser ut fra de 3 neste linjene ut som test_x og test_y stemmer overens med hverandre
onehotencoder.inverse_transform(test_x)
test_y
nanSpect.ix[3616]
import math
regr_residuals = [x**2 for x in (list(nanSpect['Tilskuertall'] - preds))] # Residuals for regression model without train and test set
regr_oos_residuals = [x**2 for x in (list(nanSpect['Tilskuertall'][year==2018] - preds_oos))]
sorted(regr_oos_residuals, reverse=True)[:15]
max(regr_oos_residuals, )
sorted(regr_residuals, reverse=True)[:15]

plt.plot(regr_residuals, '.')
plt.plot(regr_oos_residuals, '.')


