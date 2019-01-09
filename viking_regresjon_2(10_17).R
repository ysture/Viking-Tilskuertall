### Utfører samme regresjoner som i viking_regresjon_1, men
### i dette settet har jeg kun inkludert data fra 2010-2017.

### Kan være mer hensiktsmessig å analysere dataene som paneldata, og bruke 
### hvilken sesong man er i som en fixed effect på en eller annen måte. Verdt å prøve hvertfall

# Laster inn filen som er laget i Python-scriptet "vikingkamper_fra_4_17"
data.df = read.csv(file = "C:\\Users\\Yngve\\PycharmProjects\\VikingRegresjonInnIExcel\\viking_hjemmekamper_10_17_formatert.csv", header = TRUE)
head(data.df)
# Sletter de to første kolonnene, da disse bare er indexer som ble laget av pandas i python.
data.df = data.df[, -c(1:2)]

colnames(data.df)[6:8] = c("goals_home", "goals_away", "tv_kanal")
colnames(data.df)[17] = "oilers_kamp"
colnames(data.df)[20] = "downfall"

# Fjerner'Â' og mellomrom fra Tilskuertall-kolonnen
data.df[] = lapply(data.df, gsub, pattern='Â', replacement='')
data.df$Tilskuertall <- gsub('Â', '', data.df$Tilskuertall)
data.df$Tilskuertall <- gsub('\\s+', '', data.df$Tilskuertall)

# Gjør alle verdiene i Tilskuertall-kolonnen til numeriske verdier 
data.df$Tilskuertall = as.numeric(as.character(data.df$Tilskuertall))

# Gjør det samme med temperatur-verdiene og form-verdiene
data.df[18:20] = lapply(data.df[18:20], gsub, pattern=',', replacement='.')
data.df$Temperatur = as.numeric(as.character(data.df$Temperatur))
data.df$Vindstyrke = as.numeric(as.character(data.df$Vindstyrke))
data.df$downfall = as.numeric(as.character(data.df$downfall))
data.df$form_1 = as.numeric(as.character(data.df$form_1))
data.df$form_3 = as.numeric(as.character(data.df$form_3))
data.df$form_5 = as.numeric(as.character(data.df$form_5))
data.df$goals_last_homegame = as.numeric(as.character(data.df$goals_last_homegame))
data.df$Dato = as.Date(data.df$Dato, format = "%d.%m.%Y")


# Plotter alle tilskuertall, med dato på x-aksen
plot(data.df$Dato, data.df$Tilskuertall,
     pch = 19)


# Lager tre regresjonstabeller, eneste forskjellen er hvilken form-kolonne som brukes.
reg1 = lm(data.df$Tilskuertall ~ factor(data.df$tv_kanal) + data.df$form_1 
          + factor(data.df$Ukedag) + factor(data.df$Rival) + factor(data.df$mai_16)
          + data.df$goals_last_homegame + factor(data.df$oilers_kamp) + data.df$Temperatur 
          + data.df$Vindstyrke + data.df$downfall, data = data.df)

reg2 = lm(data.df$Tilskuertall ~ factor(data.df$tv_kanal) + data.df$form_3 
          + factor(data.df$Ukedag) + factor(data.df$Rival) + factor(data.df$mai_16)
          + data.df$goals_last_homegame + factor(data.df$oilers_kamp) + data.df$Temperatur 
          + data.df$Vindstyrke + data.df$downfall, data = data.df) 

reg3 = lm(data.df$Tilskuertall ~ factor(data.df$tv_kanal) + data.df$form_5 
          + factor(data.df$Ukedag) + factor(data.df$Rival) + factor(data.df$mai_16)
          + data.df$goals_last_homegame + factor(data.df$oilers_kamp) + data.df$Temperatur 
          + data.df$Vindstyrke + data.df$downfall, data = data.df) 

# Lager en fjerde regresjon, med form siste 5 kamper, 
# der sesong er tatt med som fixed effect
reg4 = lm(data.df$Tilskuertall ~ factor(data.df$tv_kanal) + factor(data.df$Sesong)
          + data.df$form_5 
          + factor(data.df$Ukedag) + factor(data.df$Rival) + factor(data.df$mai_16)
          + data.df$goals_last_homegame + factor(data.df$oilers_kamp) + data.df$Temperatur 
          + data.df$Vindstyrke + data.df$downfall, data = data.df) 

# Setter opp en regresjonstabell som sammenligner de tre regresjonene. 
# Lister opp p-verdiene for hver koeffisient istedenfor standardavviket
library('stargazer')
reg_tot = stargazer(reg1, reg2, reg3, reg4, type = 'text', align = TRUE, report = ('vc*p'))
reg_tot


### Sjekker robustheten av regresjonen med form siste 5 kamper, men uten sesongeffektene
stargazer(reg3, type = 'text')

## 2. Sjekker for heteroskedastisitet
plot(reg3$fitted.values, reg3$residuals)
abline(h=0)
reg.reg = lm(reg3$fitted.values~reg3$residuals)
abline(reg.reg)
# Ser rimelig greit ut

## 4. Sjekker om feilleddene er normalfordelte
# Lager først et histogram
hist(reg3$residuals, freq = FALSE,
     ylim = c(0,0.00025),
     xlim = c(-6000, 6000))
# Legger til en estimert tetthetsfunksjon
lines(density(reg3$residuals), col = 'red')
# Legger til en ekte normalfordelt kurve for å sammenligne
lines(seq(-6000,6000, by=100), 
      dnorm(seq(-6000,6000, by=100), mean(reg3$residuals), 
            sd(reg3$residuals)), col = 'blue')
# Fortsetter å se om feilleddene er normalfordelte ved å lage et qq-plot
plot(reg3, which = 2,
     id.n = 0)
# Finner cook's distance
cd3 = sort(cooks.distance(reg3), decreasing = TRUE)
cd3 = cd3[1:10]
plot(reg3, which = 4,
     id.n = 9,
     #labels.id = paste(data.df$Dato, data.df$Bortelag, sep = ','
)
# Velger å kjøre en regresjon uten kampene mot Molde og Tromsø
data.df_adj = data.df
data.df_adj = data.df_adj[-c(30,190), ]
reg_adj = lm(data.df_adj$Tilskuertall ~ factor(data.df_adj$tv_kanal) + data.df_adj$form_5 
             + factor(data.df_adj$Ukedag) + factor(data.df_adj$Rival) + factor(data.df_adj$mai_16)
             + data.df_adj$goals_last_homegame + factor(data.df_adj$oilers_kamp) + data.df_adj$Temperatur 
             + data.df_adj$Vindstyrke + data.df_adj$downfall, data = data.df_adj)
plot(reg_adj, which = 4)
View(data.df_adj)

# Lager en tabell for å sammenligne regresjonen med og uten outlier-verdiene.
stargazer(reg3, reg_adj, type = 'text',
          align = TRUE)

#### Lager en grafisk fremstilling av gjennomsnittlig 
#### tilskuertall for antall scorede mål forrige hjemmekamp
# Lager først en liste med gjennomsnittlig tilskuertall
# for hvert antall scorede mål forrige hjemmekamp
avg_goals = c(mean(data.df$Tilskuertall[data.df$goals_last_homegame==0]),
              mean(data.df$Tilskuertall[data.df$goals_last_homegame==1]),
              mean(data.df$Tilskuertall[data.df$goals_last_homegame==2]),
              mean(data.df$Tilskuertall[data.df$goals_last_homegame==3]),
              mean(data.df$Tilskuertall[data.df$goals_last_homegame==4]),
              mean(data.df$Tilskuertall[data.df$goals_last_homegame==5]))

# Lager så en liste som angir navn for hvert nivå i listen avg_fans. 
# Bruker bare antall mål gjennomsnittet er tatt fra
names(avg_goals) = c(0,1,2,3,4,5)


# Lager så et plot som viser den grafiske fremstillingen. 
# xpd= FALSE gjør at hver søyle ikke går forbi y-aksen
# yaxp justerer y-aksen. yaxp = c(MINSTE NIVÅ, HØYESTE NIVÅ, ANTALL TICKS)
plot_goals = barplot(avg_goals, main = "Gjennomsnittlig tilskuere for antall mål forrige hjemmekamp",
                     xlab = "Antall mål forrige hjemmekamp",
                     ylab = "Antall tilskuere",
                     ylim = c(8000,14000),
                     xpd = FALSE,
                     yaxp = c(0,13000,13),
                     col = rgb(0,0.051,0.53))


#### Gjør det samme for hver ukedag
avg_day = c(mean(data.df$Tilskuertall[data.df$Ukedag == 1]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 2]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 3]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 4]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 5]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 6]),
            mean(data.df$Tilskuertall[data.df$Ukedag == 7])
)

names(avg_day) = c('Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag')

# Lager så et plot som viser den grafiske fremstillingen. 
# xpd= FALSE gjør at hver søyle ikke går forbi y-aksen
# yaxp justerer y-aksen. yaxp = c(MINSTE NIVÅ, HØYESTE NIVÅ, ANTALL TICKS)
plot_day = barplot(avg_day, main = "Gjennomsnittlig tilskuere for hver ukedag",
                   xlab = "Ukedag",
                   ylab = "Antall tilskuere",
                   ylim = c(8000,14000),
                   xpd = FALSE,
                   yaxp = c(0,13000,13),
                   col = rgb(0,0.051,0.53))


#### Gjør det samme for om kampen har gått på TV
avg_channel = c(mean(data.df$Tilskuertall[data.df$tv_kanal==0]),
                mean(data.df$Tilskuertall[data.df$tv_kanal==1]),
                mean(data.df$Tilskuertall[data.df$tv_kanal==2])
)

names(avg_channel) = c('Ikke på TV', 'Gratis-kanal', 'Betal-kanal')

# Lager plottet
plot_channel = barplot(avg_channel, main = "Gjennomsnittlig antall tilskuere for TV-visning",
                       xlim = c(0000,15000),
                       #xpd = FALSE,
                       xaxp = c(0,15000,15),
                       col = rgb(0,0.051,0.53),
                       horiz = TRUE,
                       las = 1
)
# Endrer aksetitlene. cex.lab justerer skriftstørrelse, mens line justerer plassering
title(ylab = "Hvor kampen ble vist", cex.lab = 1.3, line = 6.2)
title(xlab = "Antall tilskuere", cex.lab = 1.3, line = 3)
# Endrer marginene slik at hele plottet skal få plass med tick-titler
par(mar = c(5,8,3.5,1.5))


### Lager så et plot som viser hvilke kamper som var mot rivaler og 16.mai-kamper, med dato på x-aksen
plot(data.df$Dato, data.df$Tilskuertall,
     xlim=as.Date(c("2004-03-01", "2017-12-30")),
     ylim=c(5500,17000),
     las = 1)
par(new=TRUE)
plot(data.df$Dato[data.df$Rival==1], 
     data.df$Tilskuertall[data.df$Rival==1],
     col = 'red',
     pch = 19,
     xlim=as.Date(c("2004-03-01", "2017-12-30")),
     ylim=c(5500,17000),
     ylab = '',
     xlab = '',
     las = 1)
par(new=TRUE)
plot(data.df$Dato[data.df$mai_16==1], 
     data.df$Tilskuertall[data.df$mai_16==1],
     col = 'blue',
     pch = 19,
     xlim=as.Date(c("2004-03-01", "2017-12-30")),
     ylim=c(5500,17000),
     ylab = '',
     xlab = '',
     las = 1)

## Legger til gjennomsnittlig tilskuertall for hver sesong
# Finner først tilskuersnitt for hver sesong
avg_season = c(mean(data.df$Tilskuertall[data.df$Sesong == 4]),
               mean(data.df$Tilskuertall[data.df$Sesong == 5]),
               mean(data.df$Tilskuertall[data.df$Sesong == 6]),
               mean(data.df$Tilskuertall[data.df$Sesong == 7]),
               mean(data.df$Tilskuertall[data.df$Sesong == 8]),
               mean(data.df$Tilskuertall[data.df$Sesong == 9]),
               mean(data.df$Tilskuertall[data.df$Sesong == 10]),
               mean(data.df$Tilskuertall[data.df$Sesong == 11]),
               mean(data.df$Tilskuertall[data.df$Sesong == 12]),
               mean(data.df$Tilskuertall[data.df$Sesong == 13]),
               mean(data.df$Tilskuertall[data.df$Sesong == 14]),
               mean(data.df$Tilskuertall[data.df$Sesong == 15]),
               mean(data.df$Tilskuertall[data.df$Sesong == 16]),
               mean(data.df$Tilskuertall[data.df$Sesong == 17]))


# Legger til sesong tilhørende x-aksen for å kunne plotte de gj.snittlige tilskuertallene
names(avg_season) = as.Date(c("2004-06-01", "2005-06-01", "2006-06-01", "2007-06-01",
                              "2008-06-01", "2009-06-01", "2010-06-01", "2011-06-01",
                              "2012-06-01", "2013-06-01", "2014-06-01", "2015-06-01",
                              "2016-06-01", "2017-06-01"))

# Legger så til disse punktene i plottet
par(new=TRUE)
plot(names(avg_season), avg_season,
     ylab = '',
     xlab = '',
     pch = 8,
     col = 'green',
     ylim = c(5500,17000),
     las = 1
     #xlim=as.Date(c("2004-03-01", "2017-12-30"))
)

legend("topright",
       c('Kamper mot rivaler', '16.mai-kamper', 'Andre kamper'),
       col = c('red', 'blue', 'black'),
       pch = c(19,19,1))




### Lager ett plot for hver sesong for å se om man lettere kan se trender
seasons = unique(data.df$Sesong)

for (season in seasons) {
  png(filename = paste('tilskuertall i sesong ',
                       ifelse(nchar(season)==1,"200","20"),
                       season,".png", sep = ""))
  
  plot(data.df$Dato[data.df$Sesong==season],
       data.df$Tilskuertall[data.df$Sesong==season],
       main = paste('Tilskuertall i sesong ', ifelse(nchar(season)==1,"200","20"),
                    season, sep=""),
       xlab = 'Dato',
       ylab = 'Tilskuertall',
       las = 1,
       xlim=as.Date(c(paste(ifelse(nchar(season)==1,"200","20"), season,"-03-01", sep=""), 
                      paste(ifelse(nchar(season)==1,"200","20"), season,"-11-30",sep=""))),
       ylim=c(5500,17000))
  
  par(new=TRUE)
  
  plot(data.df$Dato[(data.df$Sesong==season) & (data.df$Rival==1)],
       data.df$Tilskuertall[(data.df$Sesong==season) & (data.df$Rival==1)],
       xlab = 'Dato',
       ylab = 'Tilskuertall',
       las = 1,
       col = 'red',
       pch = 19,
       xlim=as.Date(c(paste(ifelse(nchar(season)==1,"200","20"), season,"-03-01", sep=""), 
                      paste(ifelse(nchar(season)==1,"200","20"), season,"-11-30",sep=""))),
       ylim=c(5500,17000))
  
  par(new=TRUE)
  
  plot(data.df$Dato[(data.df$Sesong==season) & (data.df$mai_16==1)],
       data.df$Tilskuertall[(data.df$Sesong==season) & (data.df$mai_16==1)],
       xlab = 'Dato',
       ylab = 'Tilskuertall',
       las = 1,
       col = 'blue',
       pch = 19,
       xlim=as.Date(c(paste(ifelse(nchar(season)==1,"200","20"), season,"-03-01", sep=""), 
                      paste(ifelse(nchar(season)==1,"200","20"), season,"-11-30",sep=""))),
       ylim=c(5500,17000))
  
  legend("topright",
         c('Kamper mot rivaler', '16.mai-kamp', 'Andre kamper'),
         col = c('red', 'blue', 'black'),
         pch = c(19,19,1))
  
  dev.off()
}











