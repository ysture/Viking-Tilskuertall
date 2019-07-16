### Kan være mer hensiktsmessig å analysere dataene som paneldata, og bruke 
### hvilken sesong man er i som en fixed effect på en eller annen måte. Verdt å prøve hvertfall

# Laster inn filen som er laget i Python-scriptet "vikingkamper_fra_4_17"
data.df = read.csv(file = "C:\\Users\\Yngve\\PycharmProjects\\VikingRegresjonInnIExcel\\viking_hjemmekamper_4_17_formatert.csv", header = TRUE)
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


### Lager så et plot som viser hvilke kamper som var mot rivaler, med dato på x-aksen
plot(data.df$Dato, data.df$Tilskuertall,
     xlim=as.Date(c("2004-05-01", "2017-12-30")),
     ylim=c(5500,17000),
     las = 1)
par(new=TRUE)
plot(data.df$Dato[data.df$Rival==1], 
     data.df$Tilskuertall[data.df$Rival==1],
     col = 'red',
     pch = 19,
     xlim=as.Date(c("2004-05-01", "2017-12-30")),
     ylim=c(5500,17000),
     ylab = '',
     xlab = '',
     las = 1)
par(new=TRUE)
plot(data.df$Dato[data.df$mai_16==1], 
     data.df$Tilskuertall[data.df$mai_16==1],
     col = 'blue',
     pch = 19,
     xlim=as.Date(c("2004-05-01", "2017-12-30")),
     ylim=c(5500,17000),
     ylab = '',
     xlab = '',
     las = 1)

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

### Finner tilskuersnitt for hver sesong
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
            mean(data.df$Tilskuertall[data.df$Sesong == 17])
                 )






