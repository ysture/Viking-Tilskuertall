import sklearn
import numpy as np
import pandas as pd

spect = pd.read_csv('tilskuertall_160719.csv')

# List first 20 objects in the spect dataframe
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
spect.head(20)

# List types for all columns in spect
spect.dtypes

# Changes all necessary columns
    # [Dato] to datetime
    spect['Dato'] = pd.to_datetime(spect['Dato'], dayfirst=True)
    # [Tilskuertall] to int
    spect['Tilskuertall'][10]
    spect['Tilskuertall'] = spect['Tilskuertall'].str.replace('\\xa0', '') # fjerner mellomrom (\xa0) som tusen-skilletegn
    spect['Tilskuertall'] = pd.to_numeric(spect['Tilskuertall'])