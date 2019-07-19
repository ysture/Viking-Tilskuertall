import sklearn
import pandas as pd

spect = pd.read_csv('tilskuertall_160719.csv')

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
spect.head(20)