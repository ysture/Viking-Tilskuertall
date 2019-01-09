
import os
import time
from bs4 import BeautifulSoup
import requests
import pandas
import time
import re
import itertools
from datetime import datetime
import numpy


# Ber om input for å se informasjon fra sesong 2001 til 2017.
fraSesong = int(input('Hva er det første sesongen du vil se informasjon fra? Velg fra 2001 til 2017: '))

# Url-en for de forskjellige sesongene er like bortsett fra en urlKode
urlKode = list(range(339-(2017-fraSesong),340))

sesonger = list(range(2017-(urlKode[-1]-urlKode[0]),2018))         # liste med alle sesonger



# Samler url-ene for de forskjelligene sesongene i en liste
urlSesonger = []
for url in urlKode:
    urlSesonger.append('http://www.altomfotball.no/element.do?cmd=team&teamId=303&tournamentId=1&seasonId=' + str(url) + '&useFullUrl=false')

print ("Henter inn data om sesongene...")

# Hent først linken med request, før
# det lages en soup til å kunne hente
# inn html-en fra.
page = requests.get(urlSesonger[0])
soup = BeautifulSoup(page.content, "html.parser")


# Finn data for alle sesonger
klokkeslett = []
hjemmelagOrdnet = []
bortelagOrdnet = []
hjemmelagGoals = []
bortelagGoals = []
datoerOrdnet = []
tv_kanal = []
for url in urlSesonger:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # Sett hjemmelag opp i en liste
    hjemmelag = soup.find_all('', class_="sd_fixtures_home")
    print("Henter inn data om hjemmelag i sesong "+ str(urlSesonger.index(url)+sesonger[0]) +"...")
    for lag in hjemmelag:
        hjemmelagOrdnet.append(lag.text[1:])
    # Sett bortelag opp i en liste
    bortelag = soup.find_all('', class_="sd_fixtures_away")
    print("Henter inn data om bortelag i sesong " + str(urlSesonger.index(url)+sesonger[0]) + "...")
    for lag in bortelag:
        bortelagOrdnet.append(lag.text[1:])
    # Finner alle resultater (på formen 'x - y')
    resultater = soup.find_all("a", class_="sd_fixtures_score")
    # Lager en liste for antall mål for hjemmelag
    print("Henter inn data om resultater i sesong " + str(urlSesonger.index(url)+sesonger[0]) + "...")
    for resultat in resultater:
        hjemmelagGoals.append(int(resultat.text[0]))
    # Lager en liste for antall mål for bortelag
    for resultat in resultater:
        bortelagGoals.append(int(resultat.text[-1]))
    # Finner dato for kampene
    datoer = soup.find_all('', class_="sd_fixtures_date")
    print("Henter inn data om datoer i sesong " + str(urlSesonger.index(url) + sesonger[0]) + "...")
    for dato in datoer:
        datoerOrdnet.append(dato.text)
    # Finner tv-kanal kampen ble sendt på
    kanaler = soup.find_all(class_= "sd_fixtures_channels")
    for kanal in kanaler:
        tv_kanal.append(kanal.text)


#---------------------------------------------------------#
#---------------------------------------------------------#

# Finner tilskuertall for hver kamp i hver sesong
urlKamperUordnet = []
urlKamperForMange = []
urlKamper = []
tilskuertall = []
for url in urlSesonger:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # Samler inn url-ene for de forskjellige kampene i hver sesong i en liste
    listeKamper = soup.find_all('a', class_='sd_fixtures_score')
    for kamp in listeKamper:
        urlKamperUordnet.append(kamp)
    print("Henter inn url-en for kampene i sesong " + str(urlSesonger.index(url)+sesonger[0]) +" ...")
    for url in urlKamperUordnet:
        urlKamperForMange.append('http://www.altomfotball.no/' + url.get('href'))
    for i in urlKamperForMange:
        if i not in urlKamper:
            urlKamper.append(i)

    # går inn i hver enkelt kamp og finner tilskuertallet
# Lager en liste med sesongene fra 2001-2007 for å kunne sette alle hovedkampene som tv-kamper
klokkeslett = []
urlKode_01_07 = [323,324,325,326,327,328,329]
for url in urlKamper:
    page1 = requests.get(url)
    soup = BeautifulSoup(page1.content, "html.parser")
    print("Henter inn data om tilskuertall for kamp "+ str(urlKamper.index(url)+1) +" ...")
    tilskuertallUordnet = soup.find_all(text=re.compile('Tilskuere'), limit=1)
    for tall in tilskuertallUordnet:
        tilskuertall.append(tall)
    # sjekker om kampen er i sesong 01-07, for å kunne finne klokkeslett for å vurdere eventuell hovedkamp
    try:
        if int(re.search('seasonId=(3(23|24|25|26|27|28|29))', url).group(1)) in urlKode_01_07:
            tidspunkt = soup.find(text=re.compile('Eliteserien:.*'))
            tidspunkt = tidspunkt[-5:]
            klokkeslett.append(tidspunkt)
    except AttributeError:
        continue

# Lager en som bruker klokkeslett til å lag en liste med TV-kamper og ikke-TVkamper
tv_kanal_01_07 = []
for k in klokkeslett:
    if k[0:2] == '20':
        tv_kanal_01_07.append('Hovedkamp')
    else:
        tv_kanal_01_07.append('-')

# Setter sammen oversikt over alle tv-kanaler
for t in tv_kanal:
    if tv_kanal.index(t) <= (len(tv_kanal_01_07)-1):
        tv_kanal[tv_kanal.index(t)] = tv_kanal_01_07[tv_kanal.index(t)]


# får orden på tilskuertallene, ved å kun hente ut de faktiske tallene, og fjerne "Tilskuere: "
tilskuertallOrdnet = []
for tall in tilskuertall:
    tallOrdnet = tall[11:]
    tilskuertallOrdnet.append(tallOrdnet)

#---------------------------------------------------------#
#---------------------------------------------------------#


print("Begynner å lage datasettet...")
time.sleep(1)

HovedDataSet = list(zip(datoerOrdnet, hjemmelagOrdnet, bortelagOrdnet, tilskuertallOrdnet, hjemmelagGoals, bortelagGoals, tv_kanal))
    # lager tabellen med pandas
dfSesong = pandas.DataFrame(data=HovedDataSet,
                                columns=['Dato', 'Hjemmelag', 'Bortelag', 'Tilskuertall', 'Mål_hjemmelag', 'Mål_bortelag', 'TV-kanal'])

print("Ferdig å lage datasettet.")


# ---------------------------------------------------------#
# ---------------------------------------------------------#
# Regner ut resultat for hver kamp
resultat = []
for ii, row in dfSesong.iterrows():
    if dfSesong.iloc[ii]['Hjemmelag'] == 'Viking':
        resultat.append(int(dfSesong.iloc[ii]['Mål_hjemmelag'] - dfSesong.iloc[ii]['Mål_bortelag']))
    else:
        resultat.append(int(dfSesong.iloc[ii]['Mål_bortelag'] - dfSesong.iloc[ii]['Mål_hjemmelag']))


# regner ut om hver kamp gir seier (V), uavgjort (U) eller tap(T) for Viking

for r in resultat:
    if type(r) == int:
        if r > 0:
            resultat[resultat.index(r)] = 'V'
        elif r == 0:
            resultat[resultat.index(r)] = 'U'
        elif r < 0:
            resultat[resultat.index(r)] = 'T'

dfSesong['Resultat'] = resultat

# Bruker resultatet fra hver kamp til å regne ut Vikings resultat forrige kamp
form_1 = []
form_1.append('U')
for r in resultat[:-1]:
    form_1.append(r)

dfSesong['form_1'] = form_1

# Regner ut form siste 3 kamper
form_3 = []

for ii, row in dfSesong.iterrows():
    if ii == 0:
        form_3.append('U'+'U'+'U')
    elif ii == 1:
        form_3.append('U'+'U'+dfSesong.iloc[ii - 1]['Resultat'])
    elif ii == 2:
        form_3.append('U'+dfSesong.iloc[ii - 2]['Resultat']+dfSesong.iloc[ii - 1]['Resultat'])
    else:
        form_3.append(dfSesong.iloc[ii - 3]['Resultat'] + dfSesong.iloc[ii - 2]['Resultat'] + dfSesong.iloc[ii - 1]['Resultat'])


dfSesong['form_3'] = form_3

# Regner ut form siste 5 kamper
form_5 = []

for ii, row in dfSesong.iterrows():
    if ii == 0:
        form_5.append('U'+'U'+'U'+'U'+'U')
    elif ii == 1:
        form_5.append('U'+'U'+'U'+'U'+dfSesong.iloc[ii - 1]['Resultat'])
    elif ii == 2:
        form_5.append('U'+'U'+'U'+dfSesong.iloc[ii - 2]['Resultat']+dfSesong.iloc[ii - 1]['Resultat'])
    elif ii == 3:
        form_5.append('U'+'U'+ dfSesong.iloc[ii - 3]['Resultat'] + dfSesong.iloc[ii - 2]['Resultat'] + dfSesong.iloc[ii - 1]['Resultat'])
    elif ii == 4:
        form_5.append('U'+dfSesong.iloc[ii-4]['Resultat'] + dfSesong.iloc[ii - 3]['Resultat'] + dfSesong.iloc[ii - 2]['Resultat'] + dfSesong.iloc[ii - 1]['Resultat'])
    else:
        form_5.append(dfSesong.iloc[ii - 5]['Resultat'] + dfSesong.iloc[ii - 4]['Resultat'] + dfSesong.iloc[ii - 3][
        'Resultat'] + dfSesong.iloc[ii - 2]['Resultat'] + dfSesong.iloc[ii - 1]['Resultat'])


dfSesong['form_5'] = form_5

# ---------------------------------------------------------#
# ---------------------------------------------------------#
# finnner ukedag for hver kamp
ukedag = []
for d in dfSesong.Dato:
    datoFormat = datetime.strptime(d, '%d.%m.%Y')
    ukedag.append(datoFormat.isoweekday())

dfSesong['Ukedag'] = ukedag

# ---------------------------------------------------------#
# ---------------------------------------------------------#


# Lager en egen tabell med bare hjemmekampene
dfHjemmekamper = dfSesong[dfSesong.Hjemmelag == 'Viking']
dfHjemmekamper = dfHjemmekamper.reset_index(drop=True)

#---------------------------------------------------------#
#---------------------------------------------------------#
# finner ut om kampen var et derby/ble spilt mot rivaler og 16.mai-kamper

derby_Viking = ['Bryne', 'Sandnes Ulf']
rivaler_Viking = ['Rosenborg', 'Haugesund', 'Brann']

dict_lag = {'Viking' :{'Derby': derby_Viking, 'Rivaler': rivaler_Viking}
            }
# derby
derby = []
for ii,row in dfHjemmekamper.iterrows():
    if dfHjemmekamper.iloc[ii]['Bortelag'] in dict_lag['Viking']['Derby']:
        derby.append(int('1'))
    else:
        derby.append(int('0'))

# rivaler
rivaler = []
for ii,row in dfHjemmekamper.iterrows():
    if dfHjemmekamper.iloc[ii]['Bortelag'] in dict_lag['Viking']['Rivaler']:
        rivaler.append(int('1'))
    else:
        rivaler.append(int('0'))

dfHjemmekamper['Rival'] = rivaler

# 16.mai
mai_16 = []
for ii, row in dfHjemmekamper.iterrows():
    if (dfHjemmekamper.iloc[ii]['Dato'])[0:5] == '16.05':
        mai_16.append('1')
    else:
        mai_16.append('0')

dfHjemmekamper['mai_16'] = mai_16

print(dfHjemmekamper.to_string())

#---------------------------------------------------------#
#---------------------------------------------------------#
# finne antall scorede mål forrige hjemmekamp
goals_last_homegame = []
goals_last_homegame.append(int('0'))
for ii, row in dfHjemmekamper.iterrows():
    goals_last_homegame.append(dfHjemmekamper.iloc[ii - 1]['Mål_hjemmelag'])
del goals_last_homegame[-1]

dfHjemmekamper['goals_last_homegame'] = goals_last_homegame

#---------------------------------------------------------#
#---------------------------------------------------------#
# henter inn informasjon om Oilers har spilt kamp samme dag som Viking



page = requests.get('http://oilers.papirfly.no/Kamper.aspx')
soup = BeautifulSoup(page.content, "html.parser")

oilersDatoer = []
print('Henter data om Oilers-kamper...')

oilersDatoerUordnet = soup.find_all('', class_='SortTdTrue')
for dato in oilersDatoerUordnet:
    oilersDatoer.append(dato.text)
oilersDatoer = oilersDatoer[1:]         # fjerner første element i listen, da denne bare var "KampDato".


# Lager en liste med H/B for om Oilers spiller hjemmekamp eller bortekamp
oilersHjemmeEllerBorte = soup.find_all(text=['H','B'])
# Lager en dictionary på formen Dato:H eller Dato:B.
dicDatoHjemme = dict(zip(oilersDatoer, oilersHjemmeEllerBorte))
# Fjerner alle bortekampene fra dictionaryen
for key in list(dicDatoHjemme.keys()):      # creates a list of all keys
    if dicDatoHjemme[key] == 'B':
        del dicDatoHjemme[key]

# lager en liste for å vise om det er Oilers-kamp samme dag som Viking spiller hjemmekamp. 1=oilers-kamp, 0=ikke oilers-kamp
oilersKamper = list(itertools.repeat("Nei", len(dfHjemmekamper.index)))



# Bare for å sjekke om det finnes felles datoer
oilersDatoerHjemme = list(dicDatoHjemme.keys())
vikingDatoerHjemme = dfHjemmekamper['Dato'].tolist()
fellesdatoer = []
for dato in oilersDatoerHjemme:
    if dato in vikingDatoerHjemme:
        fellesdatoer.append(dato)


# Sjekker om listen med fellesdatoer har felles verdier med dfHjemmekamper. Dersom dette er tilfellet, endres tilhørende verdi i oilersKamper til '1'.
for kamp in fellesdatoer:
    if dfHjemmekamper.isin(fellesdatoer).all:
        oilersKamper[(dfHjemmekamper[dfHjemmekamper.Dato == kamp].index.tolist())[0]] = 'Ja'
        print('Fant matchende dato.')
    else:
        print('Fant ikke matchende dato')

# Legger den nye listen med oversikt over om det spilles Oilers-kamp samme dagen til dataframen.
dfHjemmekamper['Oilers-kamp?'] = oilersKamper


#-------------------------------------------------#
#-------------------------------------------------#


# må hente data om værforhold på kampdag
temperatur = []
windData = []
wind = []
downfallData = []
downfall = []
# begynner med å finne linken der værdataene ligger
for dato in vikingDatoerHjemme:
    page = requests.get('https://www.yr.no/sted/Norge/Rogaland/Stavanger/Gausel~15360/almanakk.html?dato=%s-%s-%s' % (dato[6:], dato[3:5], dato[:2]))
    soup = BeautifulSoup(page.content, 'html.parser')
    print('Henter værdata for kamp ' + str(vikingDatoerHjemme.index(dato)+1))
    # henter inn data om temperatur. Bruker 'Middel-temperatur'.
    try:
        temperatur.append(((soup.find(text=re.compile('Middel'))).nextSibling).text)
    except AttributeError:
        print('Problemer med å hente ut info om temperatur. NoneType object has no attribute nextSibling')
        temperatur.append('N/A')
    # henter inn data om vind. Bruker vinden målt kl. 14
    try:
        windData.append((((soup.find(text=re.compile('kl 14'))).parent.parent.parent).text))
        elemWind = re.search(('\s\d+,?\d*\sm/s'), windData[-1])
        elemWind = (elemWind.group())[1:]       # fjerner mellomrommet i begynnelsen av stringen
        wind.append(elemWind)
    except AttributeError:
        print("Problemer med å hente ut målt vind for kamp " + str(vikingDatoerHjemme.index(dato)+1))
        wind.append('N/A')
    # henter inn data om nedbør
    try:
        downfallData = ((soup.find(class_='all-day-values')).text)
        elemDownfall = re.search('.?\d+.?\d*\smm', downfallData)
        if elemDownfall.group() == '-1 mm':
            page = requests.get('https://www.yr.no/sted/Norge/Rogaland/Stavanger/Stavanger_(Våland)_målestasjon/almanakk.html?dato=%s-%s-%s' % (dato[6:], dato[3:5], dato[:2]))
            soup = BeautifulSoup(page.content, 'html.parser')
            downfallData = ((soup.find(class_='all-day-values')).text)
            elemDownfall = re.search('.?\d+.?\d*\smm', downfallData)
            print('Fant data om nedbør fra Våland istedenfor Sola.')
            if (elemDownfall.group())[0] == '-':
                page = requests.get(
                    'https://www.yr.no/sted/Norge/Rogaland/Klepp/Særheim_målestasjon/almanakk.html?dato=%s-%s-%s' % (
                    dato[6:], dato[3:5], dato[:2]))
                soup = BeautifulSoup(page.content, 'html.parser')
                downfallData = ((soup.find(class_='all-day-values')).text)
                elemDownfall = re.search('.?\d+.?\d*\smm', downfallData)
                print('Fant data om nedbør fra Klepp istedenfor Sola.')
        elemDownfall = (elemDownfall.group(0))
        downfall.append(elemDownfall)
    except:
        print('Problemer med å hente ut målt nedbør for kamp ' + str(vikingDatoerHjemme.index(dato)+1))
        downfall.append('N/A')



# Lager et nytt datasett med været inkludert
dfHjemmekamper['Temperatur'] = temperatur
dfHjemmekamper['Vindstyrke'] = wind
dfHjemmekamper['Nedbør'] = downfall


# Lager en funksjon for enkel lagring

def to_csv(dataframe, filnavn):
    dataframe.to_csv(filnavn + '.csv')
    print('Lagret til CSV-fil i path.')
    return

to_csv(dfSesong, 'vikingkamper_10_17(1)')
to_csv(dfHjemmekamper, 'viking_hjemmekamper_10_17(1)')

# for å se antall av en verdi i en dataframe:
# dfSesong['Ukedag'].value_counts()
# print ut hele dataframen:
print(dfSesong.to_string())
print(dfHjemmekamper.to_string())
# dfHjemmekamper['Nedbør'].value_counts()
