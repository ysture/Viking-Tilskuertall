
import os, time, requests, pandas, time, re, csv

from bs4 import BeautifulSoup
import itertools
import numpy
from datetime import datetime

# tar inn CSV-filen. Dette vil gjøre at ikke all infoen trenger å hentes inn hver gang.
# dfSesong = pandas.read_csv('vikingkamper_4_17(8).csv')
dfHjemmekamper = pandas.read_csv('viking_hjemmekamper_4_17(11).csv', index_col = False)

#---------------------------------------------------#
#---------------------------------------------------#
# funksjon for å lagre til csv
def lagre_csv(dataframe, filnavn):
    dataframe.to_csv(filnavn + '.csv')
    print('Lagret til CSV-fil i path.')
    return
#---------------------------------------------------#

print(dfHjemmekamper.to_string())

### Må få gjort om alle verdier i dataframen til verdier det går an å analysere i en regresjonsanalyse

# Begynner med nedbør, fjerner " mm"
for ii, row in dfHjemmekamper.iterrows():
    dfHjemmekamper.at[ii, 'Nedbør'] = (str(dfHjemmekamper.iloc[ii]['Nedbør']))[0:-3]

# Fjerner " m/s" fra vind-verdiene
for ii,row in dfHjemmekamper.iterrows():
    dfHjemmekamper.at[ii, 'Vindstyrke'] = (str(dfHjemmekamper.iloc[ii]['Vindstyrke']))[0:-4]

# Fjerner "°" fra alle temperatur-verdiene
for ii,row in dfHjemmekamper.iterrows():
    dfHjemmekamper.at[ii, 'Temperatur'] = (str(dfHjemmekamper.iloc[ii]['Temperatur']))[:-1]


# Endrer alle "Ja" i 'Oilers-kamp?' til 1, og alle "Nei" til 0.
for ii,row in dfHjemmekamper.iterrows():
    if dfHjemmekamper.iloc[ii]['Oilers-kamp?'] == 'Ja':
        dfHjemmekamper.at[ii, 'Oilers-kamp?'] = 1
    elif dfHjemmekamper.iloc[ii]['Oilers-kamp?'] == 'Nei':
        dfHjemmekamper.at[ii, 'Oilers-kamp?'] = 0
    #else:
        #dfHjemmekamper.at[ii, 'Oilers-kamp?'] = 'NaN'

# Endrer verdiene for kolonnene i 'TV-kanal'
# Ingen TV-kanal = 0
# Gratis-kanal = 1
# Betalingskanal = 2

dict_kanaler = {'Ingen': ['-', ''], 'Gratis':['Hovedkamp', 'NRK1', 'TV2', 'TV 2 Zebra', 'TV2 (HD)', 'MAX', 'TVNorge'], 'Betal':[]}

for ii,row in dfHjemmekamper.iterrows():
    if dfHjemmekamper.iloc[ii]['TV-kanal'] in dict_kanaler['Ingen']:
        dfHjemmekamper.at[ii, 'TV-kanal'] = 0
    elif dfHjemmekamper.iloc[ii]['TV-kanal'] in dict_kanaler['Gratis']:
        dfHjemmekamper.at[ii, 'TV-kanal'] = 1
    else:
        dfHjemmekamper.at[ii, 'TV-kanal'] = 2

lagre_csv(dfHjemmekamper, 'viking_hjemmekamper_4_17_formatert')

print(dfHjemmekamper.to_string())








