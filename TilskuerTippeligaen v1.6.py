
import os
from bs4 import BeautifulSoup
import requests
import pandas
import re
from datetime import datetime
import numpy
import time
import geopy.distance # For å finne distanse mellom to koordinater
from geopy.geocoders import Nominatim


# Ber om input for å se informasjon fra sesong 2001 til 2018.
fraSesong = int(input('Hva er det første sesongen du vil se informasjon fra? Velg fra 2001 til 2018: '))

tot_start = time.time()
# Lager en klasse med objekter for å lagre informasjon om hvert lag
class Fotballag:
    instances = []  # Lager en liste over alle instances
                    # i Fotballag-klassen.
    """En klasse med informasjon om eliteserielagene"""
    def __init__(self, name, stadium, location1):
        self.name = name
        self.stadium = stadium
        self.location1 = location1
        self.derbylag = []
        self.rivallag = []
        self.wsta = []
        self.instances.append(self)     # Appender hver instance som initieres i fotballagklassen.
                                        # Vær obs på at det er __repr__ som appendes, men dette har ikke noe å si
                                        # når målet er å tråle gjennom (iterate) gjennom listen

    def finnForm(self, formLengde, poeng = True):
        dfTemporary = dfSesong[(dfSesong.Hjemmelag == self.name) | (dfSesong.Bortelag == self.name)] # Lager en midlertidig df for hvert lag
        new_index = list(range(0, len(dfTemporary.Dato)))   # Lager en ny index slik at man kan hente resultat for riktig lag. Indeksen fra dfSesong følger over til dfTemporary, så dette er nødvendig.
        dfTemporary = dfTemporary.set_index([dfTemporary.index, new_index]) # Setter inn den nye indeksen
        resultater1 = []
        # Iterater gjennom dfTemporary
        for ii, rows in dfTemporary.iterrows():
            # Finner resultater fra tidligere kamper i sesongen
            if rows.Hjemmelag == self.name:
                resNum = int(dfTemporary.iloc[ii[1]]['Mål_hjemmelag']) - int(dfTemporary.iloc[ii[1]]['Mål_bortelag'])
            elif rows.Bortelag == self.name:
                resNum = int(dfTemporary.iloc[ii[1]]['Mål_bortelag']) - int(dfTemporary.iloc[ii[1]]['Mål_hjemmelag'])

            if poeng == False:
                if resNum > 0:
                    res = 'V'
                elif resNum == 0:
                    res ='U'
                elif resNum < 0:
                    res = 'T'
                resultater1.append(res)
                if rows.Hjemmelag == self.name:
                    if ii[1] > formLengde-1: # Må ha n-1 tidligere kamper i inneværende sesong for å kunne regne ut form
                        if dfTemporary.iloc[ii[1]]['Dato'][-4:] == dfTemporary.iloc[ii[1]-formLengde]['Dato'][-4:]:
                            form = ''.join([str(resultater1[ii[1]-ix]) for ix in range(1,formLengde+1)])
                            dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = form[::-1] # backwards string
                        else:
                            dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = 'For få kamper' # Dersom årene ikke er like, må kampen være blant de første i sesongen
                    else:
                        dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = 'For få kamper' # Dersom indeks i dfTemporary ikke er større enn formLengde -1, er kampen nødt til å være blant de første i sesongen
            elif poeng == True:
                if resNum > 0:
                    res = 3
                elif resNum == 0:
                    res = 1
                elif resNum < 0:
                    res = 0
                resultater1.append(res)
                form = 0 # Initializing points in form
                if rows.Hjemmelag == self.name:
                    if ii[1] > formLengde-1: # Må ha n-1 tidligere kamper i inneværende sesong for å kunne regne ut form
                        if dfTemporary.iloc[ii[1]]['Dato'][-4:] == dfTemporary.iloc[ii[1]-formLengde]['Dato'][-4:]:
                            for ix in range(1, formLengde+1):
                                form += resultater1[ii[1]-ix]
                            dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = form # backwards string
                        else:
                            dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = 'For få kamper' # Dersom årene ikke er like, må kampen være blant de første i sesongen
                    else:
                        dfSesong.at[ii[0],'Form{form}'.format(form=formLengde)] = 'For få kamper' # Dersom indeks i dfTemporary ikke er større enn formLengde -1, er kampen nødt til å være blant de første i sesongen


    def goalsLastHomegame(self):
        # Finner antall scorede mål forrige hjemmekamp (for hjemmelaget) og lager en liste med alle forskjellige stadionnavn som lagres i objektet til laget
            dfTemporary = dfSesong[(dfSesong.Hjemmelag == self.name)] # Lager en midlertidig df for hvert lag
            new_index = list(range(0, len(dfTemporary.Dato)))   # Lager en ny index slik at man kan hente resultat for riktig lag. Indeksen fra dfSesong følger over til dfTemporary, så dette er nødvendig.
            dfTemporary = dfTemporary.set_index([dfTemporary.index, new_index]) # Setter inn den nye indeksen
            for ii, rows in dfTemporary.iterrows(): # Iterater gjennom dfTemporary
                if ii[1] > 0:   # Den første hjemmekampen for hvert lag vil alltid ha indeks 0
                    if dfTemporary.iloc[ii[1]]['Dato'][-4:] == dfTemporary.iloc[ii[1]-1]['Dato'][-4:]:  # Sjekker at årene for de to resultatene som sammenlignes er like
                        res = dfTemporary.iloc[ii[1]-1]['Mål_hjemmelag']     # Form1 tar resultatet fra lagets forrige kamp
                        dfSesong.at[ii[0], 'Mål forrige hjemmekamp'] = res         # Dersom årene er like, er Form1 lik resultat fra forrige kamp
                    else:
                        dfSesong.at[ii[0], 'Mål forrige hjemmekamp'] = "Første hjemmekamp i sesongen"    # Dersom årene ikke er like, må kampen være den første i sesongen
                else:
                    dfSesong.at[ii[0], 'Mål forrige hjemmekamp'] = "Første hjemmekamp i sesongen"    # Dersom indeks i dfTemporary ikke er større enn 0, er kampen nødt til å være den første i sesongen


viking = Fotballag('Viking', 'Viking Stadion', 'Stavanger')
viking.derbylag = ['Sandnes Ulf', 'Haugesund', 'Bryne']

valerenga = Fotballag('Vålerenga', 'Ullevaal Stadion ', 'Oslo')
valerenga.derbylag = ['Lyn', 'Stabæk', 'Lillestrøm', 'Strømsgodset']

brann = Fotballag('Brann', 'Brann Stadion', 'Bergen')

rosenborg = Fotballag('Rosenborg', 'Lerkendal Stadion','Trondheim')
rosenborg.derbylag = ['Ranheim']

stromsgodset = Fotballag('Strømsgodset', 'Marienlyst Stadion', 'Drammen')
stromsgodset.derbylag = ['Mjøndalen']

lyn = Fotballag('Lyn', 'Ullevaal Stadion','Oslo')
lyn.derbylag = ['Vålerenga']

mjondalen = Fotballag('Mjøndalen', 'Isaksen Stadion','Mjøndalen')
mjondalen.derbylag = ['Strømsgodset']

molde = Fotballag('Molde', 'Aker Stadion', 'Molde')
molde.derbylag = ['Aalesund', 'Kristiansund']

aalesund = Fotballag('Aalesund', 'Color Line Stadion', 'Aalesund')
aalesund.derbylag = ['Molde']

kristiansund = Fotballag('Kristiansund BK', 'Kristiansund Stadion', 'Kristiansund')
kristiansund.derbylag = ['Molde']

start = Fotballag('Start', 'Sør Arena', 'Kristiansand')

tromso= Fotballag('Tromsø', 'Alfheim Stadion', 'Tromsø')

hamkam = Fotballag('HamKam', 'Briskeby Stadion', 'Hamar')

fredrikstad = Fotballag('Fredrikstad', 'Fredrikstad Stadion', 'Fredrikstad')
fredrikstad.derbylag = ['Sarpsborg 08', 'Moss']

moss = Fotballag('Moss', 'Melløs', 'Moss')
moss.derbylag = ['Fredrikstad']

bodoglimt = Fotballag('Bodø/Glimt', 'Aspmyra', 'Bodø')

odd = Fotballag('Odd', 'Skagerak Arena', 'Skien')

stabaek = Fotballag('Stabæk', 'Nadderud', 'Bærum')
stabaek.derbylag = ['Vålerenga']

sandefjord = Fotballag('Sandefjord', 'Komplett Arena', 'Sandefjord')

sarpsborg = Fotballag('Sarpsborg 08', 'Sarpsborg Stadion', 'Sarpsborg')
sarpsborg.derbylag = ['Fredrikstad']

ranheim = Fotballag('Ranheim TF', 'Ranheim Extra Arena', 'Ranheim')
ranheim.derbylag = ['Rosenborg']

sandnesulf = Fotballag('Sandnes Ulf', 'Sandnes Stadion', 'Sandnes')
sandnesulf.derbylag = ['Viking']

bryne = Fotballag('Bryne', 'Bryne Stadion', 'Bryne')
bryne.derbylag = ['Viking']

kongsvinger = Fotballag('Kongsvinger', 'Gjemselund', 'Kongsvinger')

honefoss = Fotballag('Hønefoss', 'AKA Arena', 'Hønefoss')

haugesund = Fotballag('Haugesund', 'Haugesund Stadion', 'Haugesund')
haugesund.derbylag = ['Viking']

sogndal = Fotballag('Sogndal', 'Fosshaugane Campus', 'Sogndal')

lillestrom = Fotballag('Lillestrøm', 'Åråsen', 'Lillestrøm')
lillestrom.derbylag = ['Vålerenga']

# Url-en for de forskjellige sesongene er like bortsett fra en urlKode
urlKode = list(range(340-(2018-fraSesong),341))

sesonger = list(range(2018-(urlKode[-1]-urlKode[0]),2019))         # liste med alle sesonger


# Samler url-ene for de forskjelligene sesongene i en liste
urlSesonger = []
for url in urlKode:
    urlSesonger.append('http://www.altomfotball.no/element.do?cmd=tournamentFixtures&tournamentId=1&seasonId='
                       + str(url) + '&useFullUrl=false')

print ("Henter inn data om alle sesongene som er valgt...")

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
ukedag = []
mai_16 = []
for url in urlSesonger:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    print("Henter inn data om kampene i sesong " + str(urlSesonger.index(url) + sesonger[0]) + "...")
    # Sett hjemmelag opp i en liste
    hjemmelag = soup.find_all('', class_="sd_fixtures_home")
    for lag in hjemmelag:
        hjemmelagOrdnet.append(lag.text[1:])

    # Sett bortelag opp i en liste
    bortelag = soup.find_all('', class_="sd_fixtures_away")
    for lag in bortelag:
        bortelagOrdnet.append(lag.text[1:])

    # Finner alle resultater (på formen 'x - y')
    resultater = soup.find_all("a", class_="sd_fixtures_score")

    # Lager en liste for antall mål for hjemmelag
    for resultat in resultater:
        hjemmelagGoals.append(int(resultat.text[0]))

    # Lager en liste for antall mål for bortelag
    for resultat in resultater:
        bortelagGoals.append(int(resultat.text[-1]))

    # Finner dato for kampene
    datoer = soup.find_all('', class_="sd_fixtures_date")
    for dato in datoer:
        datoerOrdnet.append(dato.text)

    # Finner tv-kanal kampen ble sendt på
    kanaler = soup.find_all(class_= "sd_fixtures_channels")
    for kanal in kanaler:
        tv_kanal.append(kanal.text)


# Fjerne \xa0 og erstatter med et vanlig mellom for alle hjemmelag og bortelag
hjemmelagOrdnet = [elem.replace('\xa0', ' ') for elem in hjemmelagOrdnet]
bortelagOrdnet = [elem.replace('\xa0', ' ') for elem in bortelagOrdnet]


#---------------------------------------------------------#
# Ordner opp i kanalliste

dict_kanaler = {'Ingen': ['-', ''],
                'Gratis':['Hovedkamp', 'NRK1', 'NRK2', 'TV2', 'TV 2 Zebra', 'TV2 (HD)', 'MAX', 'TVNorge',
                          'Eurosport Norge', 'Eurosport 1', 'VOX'],
                'Betal':['Eurosport Player', 'Eurosport Pluss',
                         'C More Live','C More Live 2', 'C More Live 3', 'C More Live 4', 'C More Live HD',
                         'C More Hockey', 'C More Tennis', 'C More Extreme', 'C SPORTS', 'C More Fotball',
                         'C More Fotball HD', 'TV2 Sumo', 'TV2 SPORT', 'TV 2 SPORT 1', 'TV 2 SPORT 2', 'TV 2 SPORT 3' ,
                         'TV 2 SPORT 4', 'TV 2 SPORT 5', 'TV 2 SPORT 5 (HD)',
                         'TV 2 Sport Premium 1', 'TV 2 Sport Premium 2', 'TV 2 Sport Premium 3', 'TV 2 Sport Premium 4',
                         'TV 2 Sport Premium 5', 'TV 2 Sport Premium 6', 'TV 2 Sport Premium 7', 'TV 2 Sport Premium 8']}


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
    for url2 in urlKamperUordnet:
        urlKamperForMange.append('http://www.altomfotball.no/' + url2.get('href'))
    for i in urlKamperForMange:
        if i not in urlKamper:
            urlKamper.append(i)



# går inn i hver enkelt kamp og finner tilskuertallet
# Lager en liste med sesongene fra 2001-2007 for å kunne sette alle hovedkampene som tv-kamper
klokkeslett = []
urlKode_01_07 = [323,324,325,326,327,328,329]
stadium_list = []
start_tilskuertall = time.time()
for url in urlKamper:
    page1 = requests.get(url)
    soup = BeautifulSoup(page1.content, "html.parser")
    print("Henter inn data om tilskuertall for kamp "+ str(urlKamper.index(url)+1) +"/" + str(len(urlKamper))  +" ...")
    tilskuertallUordnet = soup.find_all(text=re.compile('Tilskuere'), limit=1)
    # arena = soup.find_all(class_='sd_game_home')
    # stadium_list.append(re.search('.*\\t(.*)Tilskuere:', arena[1].text).group(1))
    # Gjør ikke dette, da det gjør at man ikke finner koordinatene til mange av stadionene.
    # I tillegg viser den nåværende stadion også på historiske kamper
    for tall in tilskuertallUordnet:
        tilskuertall.append(tall[11:])
    # sjekker om kampen er i sesong 01-07, for å kunne finne klokkeslett for å vurdere eventuell hovedkamp
    try:
        if int(re.search('seasonId=(3(23|24|25|26|27|28|29))', url).group(1)) in urlKode_01_07:
            tidspunkt = soup.find(text=re.compile('Eliteserien:.*'))
            tidspunkt = tidspunkt[-5:]
            klokkeslett.append(tidspunkt)
    except AttributeError:
        continue

time_tilskuertall = round(time.time() - start_tilskuertall,2)

# Lager en liste som bruker klokkeslett til å lage en liste med TV-kamper og ikke-TVkamper
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



#---------------------------------------------------------#
#---------------------------------------------------------#

# Lager en liste som skal bli kolonnen "Resultater". Denne er tom
# fordi den da kan fylles ut gjennom en iteration senere i scriptet (rad 248 i scriptet)
derby = ["-"]*len(datoerOrdnet)
rival = ["-"]*len(datoerOrdnet)
temperature = ["-"]*len(datoerOrdnet)
wind = ["-"]*len(datoerOrdnet)
downfall = ["-"]*len(datoerOrdnet)


print("Begynner å lage datasettet...")
time.sleep(1)

HovedDataSet = list(zip(datoerOrdnet,
                        hjemmelagOrdnet, bortelagOrdnet,
                        tilskuertall,
                        hjemmelagGoals, bortelagGoals,
                        tv_kanal))
    # lager tabellen med pandas
dfSesong = pandas.DataFrame(data=HovedDataSet,
                                columns=['Dato',
                                         'Hjemmelag', 'Bortelag',
                                         'Tilskuertall',
                                         'Mål_hjemmelag', 'Mål_bortelag',
                                         'TV-kanal'])

print("Ferdig å lage datasettet.")

# Fyller ut datokolonnen slik at de tomme radene tar forrige kjente verdi
dfSesong.loc[dfSesong.Dato == "\xa0", 'Dato'] = numpy.NaN
dfSesong = dfSesong.fillna(method='ffill')


# finner ukedag for hver kamp og sjekker om kampdato er 16. mai
ukedag = []
mai_16 = []
for d in dfSesong.Dato:
    datoFormat = datetime.strptime(d, '%d.%m.%Y')
    ukedag.append(datoFormat.isoweekday())
    if d[0:5] == '16.05':
        mai_16.append('1')
    else:
        mai_16.append('0')

dfSesong['Ukedag'] = ukedag
dfSesong['16. mai'] = mai_16



# ---------------------------------------------------------#
# ---------------------------------------------------------#
print('Regner ut lagenes form...')
for team in Fotballag.instances:
    team.finnForm(1)
    team.finnForm(3)
    team.finnForm(5)
    team.goalsLastHomegame()

print('Fant lagenes form.')
#---------------------------------------------------------#
#---------------------------------------------------------#
# finner ut om kampen var et derby
for team in Fotballag.instances:
    for ii,row in dfSesong.iterrows():
        if (dfSesong.iloc[ii]['Hjemmelag'] == team.name and dfSesong.iloc[ii]['Bortelag'] in team.derbylag):
            dfSesong.set_value(ii, 'Derby', 1)
        else:
            continue


#-------------------------------------------------#
#-------------------------------------------------#
# Finner koordinatene til hver stadion
def coord_stadium(stadium):
    try:
        geolocator = Nominatim(user_agent='myapplication')
        location = geolocator.geocode(stadium)
        lon = location.longitude
        lat = location.latitude
        coord = (lon, lat)
        return coord
    except:
        print('Fant ikke koordinater til {stadium}'.format(stadium=stadium))


def closest_wsta(coord, additional_wsta = 5, maxDist = 30):
    wsta = {}
    client_id = '0bc47091-15bd-4a22-93d6-9f262a1e91a2'
    endpoint = 'https://frost.met.no/sources/v0.jsonld?types=SensorSystem&geometry=nearest(POINT({lon}%20{lat}))&nearestmaxcount={additional_wsta}'.format(
        lon = str(coord[0]),
        lat = str(coord[1]),
        additional_wsta = additional_wsta
    )
    r = requests.get(endpoint, auth=(client_id, ''))
    json = r.json()
    for station in json['data']:
        dist = geopy.distance.vincenty(coord, station['geometry']['coordinates']).km
        if dist < maxDist:
            wsta[station['id']] = geopy.distance.vincenty(coord, station['geometry']['coordinates']).km # Regner ut distansen (i luftlinje) mellom værstasjonen og stadion
    return wsta


# Finner koordinater for alle lag. "Stadium"-attributten i klassen blir da en dictionary der 'Key' er stadionnavn og 'Value' er koordinater til stadion.
start_coord = time.time() # For å ta tiden på hvor lang tid det tar å finne koordinater
for team in Fotballag.instances:
    team.stadium = {team.stadium : coord_stadium(team.stadium)}
    team.location1 = {team.location1 : coord_stadium(team.location1)}
    print('Fant koordinater for ' + team.name)


# Finner de nest nærmeste værstasjone for alle lag i Fotballag.instances uten å laste ned informasjon om alle værstasjonene i Norge (som ble gjort i v1.2)
    # Lager først en funksjon for å gjøre dette, der coord er input. Denne er lagret i Stadium['Coord'] for hvert objekt i klassen Fotballag



    # Finner de ti neste værstasjonene for alle lag ved å bruke funksjonen ovenfor
for team in Fotballag.instances:
    print('Finner værstasjoner for ' + team.name + '...')
    try:
        coord = list(team.stadium.values())[-1]
        team.wsta = closest_wsta(coord, 20)
    except:
        continue

for team in Fotballag.instances:
    print(team.name)
    print(team.wsta)

time_coord = round(time.time() - start_coord,2)

#-------------------------------------------------#
# Finner temperature, vindstyrke og nedbør den aktuelle dagen
start_weather = time.time()
# Legger data over vind og temperature til dfSesong
dfSesong['Temp'] = None
dfSesong['Vind'] = None
dfSesong['Precip'] = None
for i in range(len(dfSesong.index)):      # for i in range(len(dfSesong.index)): (den linjen som egentlig skal være her)
    # print('Vær for kamp ' + str(i+1) + '...') Overflødig når man faktisk finner vind og temperature for de fleste kamper
    hour=15 # Klokkeslett (Time)
    tempObs = '' # Lager tempObs-variabelen slik at det lett kan sjekkes om temperature har blitt funnet for hver kamp
    windObs = '' # Lager windObs-variabelen slik at det lett kan sjekkes om vind har blitt funnet for hver kamp
    precipObs = ''
    for team in Fotballag.instances:
        if dfSesong.iloc[i,1] == team.name:
            client_id = '0bc47091-15bd-4a22-93d6-9f262a1e91a2'
            wsta_string = ''
            for wsta in team.wsta: # Lager en string med alle værstasjoner for hjemmelaget, med '%2C' istedenfor alle mellomrom
                wsta_string = (wsta_string + '%2C' + wsta)
            wsta_string = wsta_string[3:]
            if not tempObs or not windObs or not precipObs:
                endpoint = 'https://frost.met.no/observations/v0.jsonld?sources={wsta}&referencetime={year}-{month}-{day}&elements=air_temperature%2Cwind_speed%2Csum(precipitation_amount%20P1D)'.format(
                    wsta=wsta_string,
                    year=dfSesong.iloc[i,0][-4:],
                    month=dfSesong.iloc[i,0][3:5],
                    day=dfSesong.iloc[i,0][0:2],
                    hour=hour)
                r = requests.get(endpoint,auth=(client_id,''))
                json = r.json()
                if not tempObs:
                    try:
                        for elem in range(0,len(json['data'])):
                            if not tempObs:
                                try:
                                    for key in json['data'][elem]['observations']:
                                        for value in (key.values()):
                                            if not tempObs:
                                                if value == 'air_temperature':
                                                    tempObs = list(key.values())[list(key.values()).index('air_temperature') + 1]
                                                    dfSesong.loc[i,'Temp'] = tempObs
                                                    print('Fant temperatur for kamp ' + str(i+1))
                                                    try:
                                                        dfSesong.loc[i,'Temp.dist'] = team.wsta[re.search('(.*):',json['data'][elem]['sourceId']).group(1)]
                                                        print(team.wsta[re.search('(.*):',json['data'][elem]['sourceId']).group(1)])
                                                    except:
                                                        continue
                                except:
                                    continue
                    except KeyError:
                        dfSesong.loc[i, 'Temp'] = '-'
                        print('Fant ikke temperatur for kamp' + str(i+1))

                if not windObs:
                    try:
                        for elem in range(0,len(json['data'])):
                            if not windObs:
                                try:
                                    for key in json['data'][elem]['observations']:
                                        for value in (key.values()):
                                            if not windObs:
                                                if value == 'wind_speed':
                                                    windObs = list(key.values())[list(key.values()).index('wind_speed') + 1]
                                                    dfSesong.loc[i, 'Vind'] = windObs
                                                    print('Fant vind for kamp ' + str(i+1))
                                                    try:
                                                        dfSesong.loc[i,'Wind.dist'] = team.wsta[re.search('(.*):',json['data'][elem]['sourceId']).group(1)]
                                                        print(team.wsta[re.search('(.*):',json['data'][elem]['sourceId']).group(1)])
                                                    except:
                                                        continue
                                except:
                                    continue
                    except KeyError:
                        dfSesong.loc[i, 'Vind'] = '-'
                        print('Fant ikke vinddata for kamp' + str(i+1))
                if precipObs == '':
                    try:
                        for elem in range(0,len(json['data'])):
                            if precipObs == '':
                                try:
                                    for key in json['data'][elem]['observations']:
                                        for value in (key.values()):
                                            if value == 'sum(precipitation_amount P1D)' and precipObs == '':
                                                precipObs = list(key.values())[list(key.values()).index('sum(precipitation_amount P1D)') + 1]
                                                dfSesong.loc[i, 'Precip'] = precipObs
                                                print('Fant nedbør for kamp ' + str(i+1))
                                                try:
                                                    dfSesong.loc[i, 'Precip.dist'] = team.wsta[re.search('(.*):',json['data'][elem]['sourceId']).group(1)]
                                                    print(team.wsta[re.search('(.*):', json['data'][elem]['sourceId']).group(1)])
                                                except:
                                                    continue
                                except:
                                    continue
                    except KeyError:
                        dfSesong.loc[i, 'Precip'] = '-'
                        print('Fant ikke nedbørsdata for kamp' + str(i+1))


time_weather = round(time.time() - start_weather,2)


print('Total tid brukt: {min} minutter og {sek} sekunder.'.format(min = int((time.time() - tot_start) // 60),
                                                                  sek = int((time.time() - tot_start) % 60)))
print('Tid brukt for å finne tilskuertall: {min} minutter og {sek} sekunder.'.format(min = int(time_tilskuertall // 60),
                                                                                    sek = int(time_tilskuertall%60)))
print('Tid brukt for å finne koordinater: {min} minutt(er) og {sek} sekunder.'.format(min = int(time_coord // 60),
                                                                                    sek = int(time_coord%60)))
print('Tid brukt for å finne informasjon om vær: {min} minutter og {sek} sekunder.'.format(min = int(time_weather // 60),
                                                                                           sek = int(time_weather % 60)))

#-------------------------------------------------#

# Lager en funksjon for enkel lagring

dfSesong.to_csv('tilskuertall_170119.csv', encoding='iso8859_10')

# for å se antall av en verdi i en dataframe:
# dfSesong['Ukedag'].value_counts()
# print ut hele dataframen:
print(dfSesong.to_string())
# dfHjemmekamper['Nedbør'].value_counts


## TO DO
# Noen av stadionene har for lang avstand dersom man bruker 20 nærmeste værstasjoner. Sett begrensninger på dette
