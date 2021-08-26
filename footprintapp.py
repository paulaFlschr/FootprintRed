# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 17:18:44 2021

@author: Paula

In dieser Datei ist die Homepage Fußabdruck der Zukunft mit den entsprechenden Unterseiten
implementiert. Die Unterseiten sind durch '===' gegliedert.
"""

import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import plotly.express as px
import scipy.optimize as sc
import re

#============================================================================================
#Diese Funktion berechnet den aktuellen CO2 Fußabdruck nach den Eingaben im Rechner 
#Fußabdruckoptimierung. Die Erklärungen der einzelnen Zahlenwerte befindet sich auf
#der Unterseite Hintergrund:Fußabdruckberechnung.
#Input: akt - Array in welchem die Eingaben des Nutzers im Rechner Fußabdruckoptimierung stehen
#Output: 1) akt_abdruck - aktueller CO2 Abdruck in kg
#       2) co2_akt - Array mit den aktuellen CO2 Werten in kg für die fünf Optimierungskategorien
#       3) co2_akt_nach_kat - Array mit aktuellen CO2 Werten in kg für die vier Unterkategorien zum plotten
#       4) faktor_nahrung - CO2 Faktor abhängig von regionalem Lebensmittelkauf (benötigt für spätere Berechnungen)
#       5) faktor_temp - CO2 Faktor abhängig von der Raumtemperatur (benötigt für spätere Berechnungen)
#============================================================================================
def akt_abdruck(akt):
    
    if akt[1] == 'sehr wichtig':
        faktor_nahrung = 0.75
    elif akt[1] == 'manchmal wichtig':
        faktor_nahrung = 0.88
    else:
        faktor_nahrung =1
    if akt[2] == 18:
        faktor_temp = 0.8
    elif akt[2] == 19:
        faktor_temp = 0.9
    elif akt[2] == 20:
        faktor_temp = 1
    elif akt[2] == 21:
        faktor_temp = 1.1
    elif akt[2] == 22:
        faktor_temp = 1.2
    elif akt[2] == 23:
        faktor_temp = 1.25
    else:
        faktor_temp = 1.3
    
    # Berechne die aktuellen co2 werte
    co2_nahrung1 = akt[0]*7.21*53*faktor_nahrung
    co2_nahrung2 = (99.5*0.36+73.6*0.437+159.6*7.34+77.4*0.82+55*3.23+14.5*1.931)*faktor_nahrung
    co2_wohnen_strom = 0.429*1964
    co2_wohnen_temp = 0.27* akt[3] *80*faktor_temp
    co2_wohnen = co2_wohnen_strom + co2_wohnen_temp
    co2_mob1 = 0.2045*akt[4]
    co2_mob2 = (akt[5]*1049.8*0.197)/4
    co2_konsum1 = 8.45 * akt[6]
    
    # Werte zur Rückgabe/ Plotten
    co2_akt_nach_kat = [co2_nahrung1 + co2_nahrung2, co2_wohnen_strom + co2_wohnen_temp, co2_mob1 + co2_mob2, co2_konsum1]
    co2_akt = [co2_nahrung1, co2_wohnen_temp, co2_mob1, co2_mob2, co2_konsum1]
    akt_abdruck = sum(co2_akt_nach_kat)
    
    return akt_abdruck, co2_akt, co2_akt_nach_kat, faktor_nahrung, faktor_temp

#=================================================================================================
#Optimierungsfunktion nach der Eingabe aller Werte/ Präferenzen des Nutzers
#Input: akt (Array in welchem die Eingaben des Nutzers im Rechner Fußabdruckoptimierung stehen); 
#       pref (Array mit Präferenzen des Nutzers); min_vals (Array mit Minimalangaben des Nutzers);
#       jahr (Optimierungsjahr); co2_akt (Array mit den aktuellen CO2 Werten in kg für die fünf Optimierungskategorien);
#       faktor_nahrung/ faktor_temp (s.o.)
#Output:res.x (Werte der Optimierungsvariablen);
#       minfussmitminvals (Minimaler Fußabdruck der mit Eingabe der Minimalwerte des Nutzers möglich ist)
#====================================================================================================

def optimize(akt, pref, min_vals, jahr, co2_akt, faktor_nahrung, faktor_temp):
    
    # zu erreichender fußabdruck
    if jahr<2030:
        max_co2 =  -185*(jahr-2020)+7440
    elif jahr<2040:
        max_co2 =  -176*(jahr-2030)+5590
    else:
        max_co2 =  -184*(jahr-2040)+3830
    #CO2 Basiswert für die Nahrung ohne Fleisch
    co2_nahrung2 = (99.5*0.36+73.6*0.437+159.6*7.34+77.4*0.82+55*3.23+14.5*1.931)*faktor_nahrung
    #prefunterschied
    max_prefdiff = 0
    for i in range(4):
        for j in range(4-i):
            if max_prefdiff < abs(pref[i]-pref[i+1+j]):
                max_prefdiff = abs(pref[i]-pref[i+1+j])
    
    #Berechne minimal möglichen Fußabdruck mit Minimalwerten, um zu schauen, ob Problem überhaupt lösbar
    co2_nahrung1min = min_vals[0]*7.21*53*faktor_nahrung
    co2_nahrung2min = (99.5*0.36+73.6*0.437+159.6*7.34+77.4*0.82+55*3.23+14.5*1.931)*faktor_nahrung
    co2_wohnen_strommin = 0.429*1964
    co2_wohnen_tempmin = 0.27* min_vals[1] *80*faktor_temp
    co2_mob1min = 0.2045*min_vals[2]
    co2_mob2min = (min_vals[3]*1049.8*0.197)/4
    co2_konsum1min = 8.45 * min_vals[4]
    co2_min = [co2_nahrung1min, co2_nahrung2min,co2_wohnen_strommin, co2_wohnen_tempmin, co2_mob1min, co2_mob2min, co2_konsum1min]
    minfussmitminvals = sum(co2_min)
        
    # Generiere Lineares Programm
    c = [-pow(pref[0],2),-pow(pref[1],2),-pow(pref[2],2),-pow(pref[3],2),-pow(pref[4],2),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    A_ub = [[co2_akt[0],(co2_akt[1]-0.27* akt[3] *80*0.8),co2_akt[2],co2_akt[3],co2_akt[4],0.36*99.5,0.437*73.6,7.34*159.6,0.82*77.4,3.23*55,1.931*14.5,0.429*akt[3]*80+0.27* akt[3] *80*0.8+co2_nahrung2,0,0,0,0,0,0,0,0,0,0],
            [-akt[0],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,-(akt[2]-18),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,-akt[4],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,-akt[5],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,-akt[6],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0, 0,0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1],
            [1,-1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0],
            [1,0,-1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0],
            [1,0,0,-1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0],
            [1,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0],
            [0,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0],
            [0,1,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0],
            [0,1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0],
            [0,0,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0],
            [0,0,1,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0],
            [0,0,0,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1],
            [-1,1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0],
            [-1,0,1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0],
            [-1,0,0,1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0],
            [-1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0],
            [0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0],
            [0,-1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0],
            [0,-1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0],
            [0,0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0],
            [0,0,-1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0],
            [0,0,0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1]]
    b_ub = [max_co2,-min_vals[0],-(min_vals[1]-18),-min_vals[2],-min_vals[3],-min_vals[4],pow(max_prefdiff,2),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


    A_eq = [[akt[0]*53*1860*1/6*1/340,0,0,0,0,99.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [akt[0]*53*1860*1/6*1/660,0,0,0,0,0,73.6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [akt[0]*53*1860*1/6*1/1630,0,0,0,0,0,0,159.6,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [akt[0]*53*1860*1/6*1/3040,0,0,0,0,0,0,0,77.4,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [akt[0]*53*1860*1/6*1/860,0,0,0,0,0,0,0,0,55,0,0,0,0,0,0,0,0,0,0,0,0],
            [akt[0]*53*1860*1/6*1/1370,0,0,0,0,0,0,0,0,0,14.5,0,0,0,0,0,0,0,0,0,0,0]]
    b_eq = [akt[0]*53*1860*1/6*1/340,akt[0]*53*1860*1/6*1/660, akt[0]*53*1860*1/6*1/660, akt[0]*53*1860*1/6*1/3040, akt[0]*53*1860*1/6*1/860, akt[0]*53*1860*1/6*1/1370]
    
    #Löse lineares Programm
    res = sc.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=[(0,1),(0,1),(0,1),(0,1),(0,1),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(1,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)], method='simplex')
     
    return res.x, max_co2, minfussmitminvals
       
# Titellines -----------------------------------------------------------------------------------------------------------------------
imagefuss= Image.open('Fuss.PNG')
st.set_page_config(page_title='Fußabdruck der Zukunft', page_icon=imagefuss, layout='wide', initial_sidebar_state='expanded')
c1,c2,c3 = st.beta_columns((0.5,4,3))
c1.image(imagefuss,width = 80,  clamp=False, channels='RGB', output_format='auto')
c2.write("""
        # Fußabdruck der Zukunft
        ## - Optimiere deinen ökologischen Fußabdruck -
    """)
navigation = c3.selectbox('', ["Startseite","Rechner: Fußabdruckoptimierung", "Rechner: Gesellschaftlicher Einfluss","SchülerInnen-Guide","Hintergrund: Fußabdruckberechnung", "Hintergrund: Budgetberechnung", "Hintergrund: Fußabdruckoptimierung","Hintergrund: Datenvalidierung", "Hintergrund: Gesellschaftlicher Einfluss","Quellen & Impressum"])
st.markdown("***")
hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
st.markdown(hide_footer_style, unsafe_allow_html=True)

#==============================================================================================================================
if navigation == 'Startseite':
    c1,c2,c3 = st.beta_columns([1,6,1])
    c2.markdown('<div style="text-align: center"><em> <font size = 6><b> Sei du selbst die Veränderung, die du dir wünschst für diese Welt! </b></font> - Mahatma Gandhi</em></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([2.5,6,2.5])
    imagestart= Image.open('Startseite.png')
    c2.image(imagestart,use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""<font size = 5>
                Willkommen bei „Fußabdruck der Zukunft“. Hier kannst du sowohl deinen persönlichen
                CO<sub>2</sub>-Fußabdruck, als auch eine optimale Verringerung
                deines Abdrucks berechnen lassen. Außerdem findest du hier Infos rund um das Thema 
                CO<sub>2</sub>-Verbrauch und wir erklären dir, wie unser Rechner funktioniert. 
                Unser Guide gibt eine Übersicht, was sich hinter den einzelnen Unterseiten verbirgt.
                Im Allgemeinen kannst du die Homepage aber auch ohne den Guide problemlos verstehen.</font><br><br>
                """, unsafe_allow_html=True)
    guide = st.beta_expander("Guide: Fußabdruck der Zukunft")
    guide.markdown("""
                   <br><b>Startseite</b><br>
                   Die Startseite bietet eine kurze und anschauliche Einführung in das Thema CO2 – Fußabdruck und die Seite „Fußabdruck der Zukunft“. Zur Veranschaulichung, auch im Hinblick auf potenziell jüngere NutzerInnen, wurde ein Video in die Seite eingebettet. 
                   <br><b>SchülerInnen - Guide</b><br>
                   Die Homepage soll auch im Rahmen der Schule Anwendung finden. Wie ein möglicher Einsatz aussehen könnte, soll die Unterseite „SchülerInnen – Guide“ veranschaulichen. Sie soll die SchülerInnen durch die Seite führen und an ausgewählten Stellen durch zusätzliche Fragen und Anregungen zum Verständnis beitragen. Zum jetzigen Zeitpunkt sind die Aufgaben an SchülerInnen aus der Mittelstufe gerichtet, weshalb die Unterseite „Hintergrund: Fußabdruckoptimierung“ nicht bearbeitet wird. 
                   <br><b>Hintergrund: Budgetberechnung</b><br>
                   Zum Erstellen eines Fußabdruck - Rechners muss eine angemessene Datengrundlage geschaffen werden. Dazu wird auf der Unterseite „Hintergrund: Budgetberechnung“ erklärt, wie die Berechnung aktueller und zukünftiger CO2 – Budgets erfolgt. 
                   <br><b>Hintergrund: Fußabdruckberechnung</b><br>
                   Die Unterseite „Hintergrund: Fußabdruckberechnung“ bildet die statistische Grundlage des Rechners. Sie legt die Berechnungen der einzelnen Aspekte Nahrung, Wohnen, Mobilität und Konsum dar und erklärt ihr Zustandekommen.
                   <br><b>Hintergrund: Fußabdruckoptimierung</b><br>
                   Die mathematische Grundlage bildet das Optimierungsmodell auf der Unterseite „Hintergrund: Fußabdruckoptimierung“. Die Verarbeitung der Eingabedaten, die Entstehung der Variablen, der Zielfunktion und der Nebenbedingungen werden dort kleinschrittig erklärt und in dem Optimierungsmodell zusammengeführt.
                   Außerdem wird die computergestützte Berechnung und die dazu nötige Überführung des Modells in die allgemeine Form eines linearen Programms dargestellt.
                   <br><b>Rechner: Fußabdruckoptimierung</b><br>
                   Der eigentliche Fußabdruck – Rechner befindet sich auf der Unterseite „Rechner: Fußabdruckoptimierung“. Die Seite ist durch Checkboxen gegliedert, sodass die Nutzung erleichtert wird. 
                   <br><b>Hintergrund: Datenvalidierung</b><br>
                   Zur Überprüfung der Ergebnisse des Rechners findet ein Vergleich mit einem anderen Rechner und mit bekannten CO2 – Werten aus der Vergangenheit statt. Dabei wird der Rechner des Umweltbundesamtes herangezogen, da er die gleichen Kategorien behandelt und ähnliche Eingaben fordert. Außerdem wurde er vom Umweltministerium veröffentlicht und wird deshalb als seriöse Vergleichsbasis vermutet. Die Validierung ist auf der Unterseite „Hintergrund: Datenvalidierung“ zu finden. 
                   <br><b>Hintergrund: Gesellschaftlicher Einfluss</b><br>
                   Auf der Unterseite „Hintergrund: Gesellschaftlicher Einfluss“ wird kurz die statistische Basis, auf der die Berechnung des „Rechner: Gesellschaftlicher Einfluss“ stattfindet, erklärt. Die Datenbasis bilden die bereits in „Hintergrund: Fußabdruckberechnung“ dargelegten Formeln. 
                   <br><b>Rechner: Gesellschaftlicher Einfluss</b><br>
                   Die Unterseite „Rechner: Gesellschaftlicher Einfluss“ dient der anschaulichen und besseren Vorstellung des abstrakten Themenfeldes durch die Reduktion auf einen kleineren Personenkreis. Die Einflussnahme von bestimmten Bevölkerungsanteilen kann hier erkundet werden. 
                   <br><b>Technische Umsetzung der Homepage</b><br>
                   Zur Implementierung der Homepage verwendet wir Streamlit. Hierbei handelt es sich einerseits um eine Python basierte Bibliothek zur Implementierung von Data Dashboards und andererseits um einen Deployment – Dienst, der den Veröffentlichungsprozess ermöglicht. Weiterhin wurden die Python - Pakete pandas, PIL, numpy, plotly und re verwendet. Zur Lösung des Optimierungsmodells verwenden wir die Softwareumgebung scipy. Genaueres zur computergestützten Berechnung kann auf der Unterseite „Hintergrund: Fußabdruckoptimierung/ Hintergrund: Computergestützte Berechnung“ nachgelesen werden. 
                   Der Code kann unter https://github.com/paulaFlschr/FootprintRed/blob/main/footprintapp.py abgerufen werden. Für das gesamte Projekt siehe https://github.com/paulaFlschr/FootprintRed . 
                   """, unsafe_allow_html=True)
    st.markdown("""<font size = 5> Schau dir
                zum Einstieg gerne das Video „Klimaschutz im Alltag – Welchen Einfluss haben 
                wir?“ an.</font><br><br>
                """, unsafe_allow_html=True)
    c1, c2, c3 = st.beta_columns((1,5,1))
    c2.video(data='https://www.youtube.com/watch?v=0msDfGBiAmQ&ab_channel=Helmholtz-Klima-Initiative', format='video/mp4', start_time=0)
    st.markdown("""<br>
                Im November 2016 beschloss das Bundeskabinett den Klimaschutzplan 2050. Darin
                sind die Klimaschutzziele der Bundesrepublik Deutschland festgelegt, die im
                Einklang mit dem <a href="https://www.bmu.de/gesetz/uebereinkommen-von-paris" target="_blank">Pariser Klimaabkommen</a> stehen. So sollen die 
                Treibhausgasemissionen bis 2050 um 80 bis 95 Prozent reduziert werden im 
                Vergleich zum Wert von 1990. Die Einhaltung dieses Ziels stellt nicht nur die
                Politik und große Unternehmen vor eine große Herausforderung, sondern wird auch 
                großen Einfluss auf die Bevölkerung haben. Jeder Einzelne wird sich auf 
                Einschränkungen einlassen müssen und einen Beitrag zum Klimaschutz 
                leisten müssen. <br> <br> <center><b> Doch wie könnten diese Einschränkungen für die Bevölkerung 
                von Deutschland aussehen? </b></center><br> Unsere Modellierung basiert auf dem 
                bekannten Konzept eines CO<sub>2</sub>-Fußabdruck-Rechners. Allerdings soll darüber 
                hinaus auf der Grundlage des persönlichen jährlichen CO<sub>2</sub>-Verbrauchs eine
                Empfehlung gegeben werden, wie das Verhalten verändert werden könnte, um das CO<sub>2</sub>-Ziel 
                einzuhalten. Zudem bieten wir die Möglichkeit ein Gefühl für den Einfluss von Bevölkerungsteilen
                auf den Gesamtverbrauch zu bekommen.
                """, unsafe_allow_html=True)
                
#=========================================================================================================               
            
elif navigation == "Rechner: Fußabdruckoptimierung":
    st.write("""
             Hier kannst du deinen aktuellen $CO_{2}$-Fußabdruck berechnen. Um dem Klimawandel 
             entgegenzuwirken, muss aber in der Zukunft der $CO_{2}$-Ausstoß sinken. Was das für 
             deinen $CO_{2}$-Fußabdruck heißt, wollen wir dir hier zeigen. Befolge dazu unsere 
             Schritt-für-Schritt-Anleitung. Und los geht’s!
             """)
    c1,c2,c3 = st.beta_columns((1,5,1))
    image1= Image.open('Umweltschutz1.jpg')
    c2.image(image1, width=700, use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("""<font size="5"><b>Schritt 1: Ermittlung deines aktuellen Fußabdrucks</b> </font><br>
                     Fülle alle Fragen im unten stehenden Formular aus.<br> 
                     Beachte, dass du alle Angaben für den genannten Zeitraum mitteln solltest. Isst
                     du also in einer Woche 2 Kilogramm Fleisch &Fisch und in der darauf folgenden
                     kein Fleisch und keinen Fisch so setze den Wert auf 1. Denke außerdem daran, dass auch Unterwäsche
                     und Schuhe Kleidungsstücke sind. Damit dir die Einschätzung etwas einfacher fällt, sind als Platzhalter die
                     Werte einer durchschnittlichen Person in Deutschland angegeben. <br>
                     <font size = 2> Hinweis: Auf der Seite 'Hintergund: Fußabdruckberechnung' findest du
                     Informationen über die Grundlage dieser Berechnung. </font>
            """,unsafe_allow_html=True)
    
   
    col1, col2, col3, col4 = st.beta_columns(4)
    col1.markdown("### Kategorie: Ernährung",unsafe_allow_html=True)
    nahrung1 = col1.text_input(label='Wie viel Kilogramm Fleisch und Fisch konsumierst du wöchentlich?', value=1.37)
    nahrung2 = col1.radio('Wie wichtig ist dir, dass die Lebensmittel regional sind?',['sehr wichtig','manchmal wichtig','garnicht wichtig'], index=1)
    col2.markdown("### Kategorie: Wohnen",unsafe_allow_html=True)
    wohnen1 = col2.slider(label='Auf wie viel Grad heizt du deine Wohnung normalerweise?', min_value=18,max_value=24,step=1, value=21)
    wohnen2 = col2.text_input(label='Wie viel Quadratmeter Wohnfläche hast du zur Verfügung (pro Person)?', value=47)
    col3.markdown("### Kategorie: Mobilität",unsafe_allow_html=True)
    mob1 = col3.text_input(label='Wie viel Kilometer fährst du pro Jahr mit dem Auto (pro Person)?', value=11733)
    mob2 = col3.text_input(label='Wie viele Stunden bist du in den letzten vier Jahren geflogen?', value=12)
    col4.markdown("### Kategorie: Konsum (Kleidung)",unsafe_allow_html=True)
    konsum1 = col4.text_input(label='Wie viele Kleidungsstücke kaufst du im Jahr?', value=56.2)
    col4.markdown('<br><br><br><br><br>',unsafe_allow_html=True)
    nahrung1 = re.sub(r'\,', r'.',nahrung1)
    wohnen2 = re.sub(r'\,', r'.',wohnen2)
    mob1 = re.sub(r'\,', r'.',mob1)
    mob2 = re.sub(r'\,', r'.',mob2)
    konsum1 = re.sub(r'\,', r'.',konsum1)
    
     # Berechne den aktuellen fußabdruck
    akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
    akt_abdruck, co2_akt, co2_akt_nach_kat, faktor_nahrung, faktor_temp = akt_abdruck(akt)
        
    checkbox1 = st.checkbox(label="Schritt 1 abschließen: Fußabdruck berechnen")
    if checkbox1:
        col1,col2,col3 = st.beta_columns((0.7,1.3,2))
        imagefuss = Image.open('Fuss.PNG')
        col1.image(imagefuss, width=700, use_column_width=True, clamp=False, channels='RGB', output_format='auto')
        col2.markdown("""<br>
                <center><font size="4"><b>Dein aktueller Fußabdruck beträgt """+ str(round(akt_abdruck))+""" Kilogramm.</b></font></center><br>
                Zum Vergleich: Der durchnittliche CO<sub>2</sub> Fußabdruck in Deutschland liegt bei ca. 7300 Kilogramm.
                Der durchschnittliche weltweite CO<sub>2</sub> Fußabdruck liegt bei 4800 Kilogramm.<br>
                In dem neben stehenden Diagramm findest du den Vergleich zum durchnittlichen Fußabdruck eines 
                Menschen in Deutschlands zu deinem Fußabdruck, aufgeschlüsselt in die vier Kategorien.
                """,unsafe_allow_html=True)
            
        df = pd.DataFrame(
            [["Nahrung", 1788,co2_akt_nach_kat[0]], ["Wohnen", 1960,co2_akt_nach_kat[1]], ["Mobilität", 3020,co2_akt_nach_kat[2]],["Kleiderkonsum",474,co2_akt_nach_kat[3]]],
            columns=["Kategorie","Durchschnitt CO<sub>2</sub> Deutschland", "Dein CO<sub>2</sub>"])
        fig = px.bar(df, x="Kategorie", y=["Durchschnitt CO<sub>2</sub> Deutschland", "Dein CO<sub>2</sub>"], barmode='group', height=400)
        col3.plotly_chart(fig)
        
        st.markdown("***")
        
        checkboxopt = st.checkbox(label="zur Optimierung")
        if checkboxopt:
            st.markdown("""
                     <font size="5"><b>Schritt 2: Optimierung-Gib Minimalwerte an</b> </font><br>
                              <br> Wir wollen nun deinen Fußabdruck verkleinern, d.h.
                               deinen CO<sub>2</sub>-Ausstoß reduzieren. Das wird zu Veränderungen
                               in einzelnen Kategorien führen. Hier hast du die Möglichkeit
                              Minimalwerte für einzelne Aspekte zu setzen. Möchtest du zum Beispiel deine Zimmertemperatur nicht auf unter 20 Grad Celsius herabsetzen, dann
                              gib in das Eingabefeld eine 20 ein.
                    """,unsafe_allow_html=True)
                    
            
            col1, col2, col3, col4 = st.beta_columns(4)
            min_val_nahrung1 = col1.text_input(label= 'Minimaler Fleisch & Fischkonsum in kg pro Woche',value=0)
            min_val_wohnen = col2.text_input(label='Minimale Zimmertemperatur', value=18)
            min_val_mob1 = col3.text_input(label='Minimale Autokilometer pro Jahr', value=0)
            min_val_mob2 = col3.text_input(label='Minimale Flugstunden in 4 Jahren', value=0)
            min_val_konsum1 = col4.text_input(label='Minimale Anzahl an neuen Kleidungsstücken im Jahr', value=0)
            
            min_val_nahrung1 = re.sub(r'\,', r'.',min_val_nahrung1)
            min_val_wohnen = re.sub(r'\,', r'.',min_val_wohnen)
            min_val_mob1 = re.sub(r'\,', r'.',min_val_mob1)
            min_val_mob2 = re.sub(r'\,', r'.',min_val_mob2)
            min_val_konsum1 = re.sub(r'\,', r'.',min_val_konsum1)
            
            checkbox2 = st.checkbox(label="Schritt 2 abschließen: Minimalwerte setzen")
            if checkbox2:
                st.markdown("""
                            <font size="5"><b>Schritt 3: Optimierung-Gib Präferenzen an</b> </font><br>
                            Wir wollen, dass die Optimierung zu dir passt und für dich angenehm ist. 
                            Teile uns deshalb hier mit, wie wichtig die einzelnen Aspekte in deinem 
                            Leben für dich sind. Dazu kannst du Punkte zwischen 1 und 10 für die 
                            einzelnen Aspekte vergeben. Dabei bedeutet 10 „sehr wichtig“ und 1 
                            „gar nicht wichtig“. 
                    """,unsafe_allow_html=True)
                   
                remaining_prefs=[1,2,3,4,5,6,7,8,9,10]
                col1, col2, col3, col4 = st.beta_columns(4)
                val_nahrung1 = col1.selectbox('Fleisch- & Fischkonsum beibehalten', remaining_prefs)
                val_wohnen = col2.selectbox('Zimmertemperatur beibehalten', remaining_prefs)
                val_mob1 = col3.selectbox('Autokilometer beibehalten',remaining_prefs)
                val_mob2 = col3.selectbox('Flugstunden beibehalten', remaining_prefs)
                val_konsum1 = col4.selectbox('Konsum beibehalten', remaining_prefs)
            
                checkbox3 = st.checkbox(label="Schritt 3 abschließen: Präferenzen setzen")
                if checkbox3:
                    st.markdown("""
                             <font size="5"><b>Schritt 4: Optimierung-Jahr festlegen</b> </font><br>
                                      Jetzt wollen wir gemeinsam in die Zukunft schauen. Hier kannst 
                                      du ein Jahr auswählen, für das du gerne wissen möchtest, wie 
                                      dein Fußabdruck aussehen sollte. Wählst du beispielsweise das 
                                      Jahr 2030, so wird dein CO<sub>2</sub>-Fußabdruck so weit heruntergesetzt,
                                      dass du unter dem Pro-Kopf-CO<sub>2</sub>-Budget von 2030 liegst.<br>
                                      <font size = 2> Hinweis: Auf der Seite 'Hintergund: Budgetberechnung' findest du
                                      Informationen über die Grundlage dieser Berechnung. </font>
                                      """,unsafe_allow_html=True)
                    
                    jahr = st.slider(label='Jahr', min_value=2021,max_value=2050,step=1)
                    
                    checkbox4 = st.checkbox(label="Schritt 4 abschließen: Jahr anwenden")
                    if checkbox4:
                    
                        # Arrays in denen die Benutzereingaben gespeichert werden
                        akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
                        pref = [float(val_nahrung1),float(val_wohnen),float(val_mob1),float(val_mob2),float(val_konsum1)]
                        min_vals = [float(min_val_nahrung1),float(min_val_wohnen), float(min_val_mob1), float(min_val_mob2), float(min_val_konsum1)]
                        
                        
                        solution,maxco2,minfussmitminvals = optimize(akt, pref, min_vals, jahr, co2_akt, faktor_nahrung, faktor_temp)
                        #st.write(solution)
                        #st.write(max_prefdiff)
                    
                        st.markdown("***")
                        st.markdown("""
                                <font size=6><b>Dein Ergebnis</b> </font><br>
                                <font size=5><b> Dein CO<sub>2</sub>-Fußabdruck darf im Jahr """+str(jahr)+"""
                                 nurnoch """+ str(maxco2)+ """ Kilogramm betragen, aktuell beträgt er """
                                 +str(round(akt_abdruck))+""" Kilogramm.</b></font><br>
                                 <font size = 2> Hinweis: Auf der Seite 'Hintergund: Fußabdruckoptimierung' findest du
                                 Informationen über die Grundlage dieser Berechnung. </font><br>
                                """,unsafe_allow_html=True)
                    
                        if minfussmitminvals > maxco2:
                            st.markdown("""
                                        <b><font size = 5>Wir können deinen Fussabdruck mit deinen Minimalangaben nicht weiter reduzieren,
                                        vielleicht denkst du nochmal über deine Minimalangaben nach ;)
                                        </font></b>""",unsafe_allow_html=True)
                        if akt_abdruck <= maxco2:
                            st.markdown("""
                                <b>Super! Dein aktueller Fußabdruck liegt bereits unter der geforderten CO2-Grenze. 
                                Das heißt natürlich nicht, dass du garnichts mehr tun kannst und sollst.</b>
                                """,unsafe_allow_html=True)
                        else:
                            if round(solution[0],4)<1 and not akt[0]==0:
                                reduktion0 = round((1 - solution[0])*100,2)
                                red0 = round(akt[0]*(1-solution[0]),2)
                                c1,c2 = st.beta_columns((1,3))
                                image_fleisch= Image.open('Red_Fleisch.jpg')
                                c1.image(image_fleisch, width=200, clamp=False, channels='RGB', output_format='auto')
                                c2.markdown("""
                                    <b>Reduziere deinen Fleisch- und Fischkonsum um """+str(red0)+""" Kilogramm ("""+str(reduktion0)+ """ %). </b><br>
                                    Suche doch mal im Internet nach vegetarischen Rezepten. Dort gibt es eine rießige Auswahl, da ist
                                    sicher etwas dabei was dir schmecken könnte ;)
                                    """,unsafe_allow_html=True)
                            if round(solution[1],4)<1:
                                reduktion1 = round((1 - solution[1])*100,2)
                                red1 = 18.0 + round((akt[2]-18)*solution[1],1)
                                c1,c2 = st.beta_columns((3,1))
                                image_heizen= Image.open('Red_Heizen.jpg')
                                c2.image(image_heizen, width=100, clamp=False, channels='RGB', output_format='auto')
                                c1.markdown("""
                                    <b>Reduziere deine Zimmerwärme auf """+str(red1)+""" Grad (um """+str(reduktion1)+""" %).</b> <br>
                                    Mit ein paar dicken Socken, einem dicken Pulli und einem leckerer Tee eingekuschelt in eine
                                    flauschige Decke. Klimaschutz muss nicht immer ungemütlich sein.
                                    """,unsafe_allow_html=True)
                            if round(solution[2],4)<1:
                                reduktion2 = round((1 - solution[2])*100,2)
                                red2 = round(akt[4]*(1-solution[2]))
                                c1,c2 = st.beta_columns((1,3))
                                image_fahrrad= Image.open('Red_Auto.jpg')
                                c1.image(image_fahrrad, width=100, clamp=False, channels='RGB', output_format='auto')
                                c2.markdown("""
                                    <b>Reduziere deine Autokilometer um """+str(red2)+""" Kilometer ("""+str(reduktion2)+"""%). </b><br>
                                    Kurze Strecken kannst du mit dem Fahrrad fahren oder zu Fuß gehen. Das hält gleichzeitig noch
                                    fit und gesund. Nimm doch für längere Strecken einfach mal den Bus oder die Bahn. Das kann
                                    manchmal auch viel entspannter sein.
                                    """,unsafe_allow_html=True)
                            if round(solution[3],4)<1 and not akt[5]==0:
                                reduktion3 = round((1 - solution[3])*100,2)
                                red3 = round(akt[5]*(1-solution[3]),1)
                                c1,c2 = st.beta_columns((3,1))
                                image_flieg= Image.open('Red_Fliegen.jpg')
                                c2.image(image_flieg, width=200, clamp=False, channels='RGB', output_format='auto')
                                c1.markdown("""
                                    <b>Reduziere deine Flugstunden um """+str(red3)+""" Stunden ("""+str(reduktion3)+"""%). </b><br>
                                    Fliegen ist besonders klimaschädlich. Natürlich heißt das nicht, dass du garnicht mehr weiter
                                    weg kannst. Aber überlege doch mal ob es vielleicht Alternativen gibt. Urlaubsziele lassen sich
                                    zum Beispiel auch in Deutschland viele schöne finden.
                                    """,unsafe_allow_html=True)
                            if round(solution[4],4)<1:
                                reduktion4 = round((1 - solution[4])*100,2)
                                red4 = round(akt[6]*(1-solution[4]))
                                c1,c2 = st.beta_columns((1,3))
                                image_konsum= Image.open('Red_Konsum.jpg')
                                c1.image(image_konsum, width=150, clamp=False, channels='RGB', output_format='auto')
                                c2.markdown("""
                                    <b>Reduziere deinen Konsum um """+str(red4)+""" Kleidungsstrücke ("""+str(reduktion4)+""" %).</b> <br>
                                    Weniger Kleidungsstücke und dafür hochwertige sind deutlich besser für das Klima. Seien wir mal
                                    ehrlich, viele Sachen die wir einmal kaufen ziehen wir am Ende viel zu selten an...
                                    """,unsafe_allow_html=True)
    
    st.markdown("***")
    st.markdown("""<font size = 2>
                Anmerkung: Alle Berechnungen wurden mit festen CO<sub>2</sub> Werten durchgeführt. Auf mögliche Verbesserungen wurde 
                nicht eingegangen.</font>""",unsafe_allow_html=True)
    
                                    
#====================================================================================================
                                    
elif navigation == "Rechner: Gesellschaftlicher Einfluss":
    st.sidebar.header('Eingabeparameter zur Berechnung gesellschaftlichen Einflusses')
    
    st.sidebar.markdown("***")

    anzahl_einwohner = st.sidebar.text_input(label='Wie viele Einwohner:innen hat dein Ort oder deine Stadt?', value=0)
    st.sidebar.markdown("***")
    anzahl_motivierte = st.sidebar.slider('Wie viel Prozent aller Einwohner:innen kannst du zur Reduktion ihres CO2-Ausstoßes motivieren?',min_value=0,max_value=100,step=10, value=10)
    st.sidebar.markdown("***")
    
    red_fleisch = st.sidebar.text_input('Wie viel kg Fleisch werdet ihr pro Woche pro Person weniger essen?', value=0)
    red_auto = st.sidebar.text_input('Wie viel km Auto werdet ihr pro Jahr pro Person weniger fahren?',value=0)
    red_flug = st.sidebar.text_input('Wie viel Stunden werdet ihr in vier Jahren pro Person weniger fliegen?',value=0)
    red_konsum = st.sidebar.text_input('Wie viel Kleidungsstücke werdet ihr pro Jahr pro Person weniger kaufen?',value=0)
    
    red_fleisch = re.sub(r'\,', r'.',red_fleisch)
    red_auto = re.sub(r'\,', r'.',red_auto)
    red_flug = re.sub(r'\,', r'.',red_flug)
    red_konsum = re.sub(r'\,', r'.',red_konsum)
    
    menschen = round(float(anzahl_einwohner) * (anzahl_motivierte/100))
    einsparen = round((float(red_fleisch) * 7.21*53) + (float(red_auto)*0.2045) + ((float(red_flug)*1049.8*0.197)/4) + (float(red_konsum)*8.45))*menschen
    
    c1,c2,c3 = st.beta_columns([2.5,6,2.5])
    imageeinfluss= Image.open('GEinfluss.jpg')
    c2.image(imageeinfluss,use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    
    st.write("### Fülle die Seitenleiste aus und schaut, was ihr alle zusammen bewirken könnt!!!")
    c1,c2 = st.beta_columns(2)
    imagemensch= Image.open('Menschenkette.PNG')
    c2.image(imagemensch,use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    c1.image(imagemensch,use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    
    c1,c2,c3 = st.beta_columns([3,2,3])
    checkbox_zusammen = c2.checkbox(label="Einfluss ausrechnen")
    if checkbox_zusammen:
        st.markdown("<font size = 5> Wenn du "+str(menschen)+" Menschen motivierst, ihren Fußabdruck mit dir gemeinsam wie angegeben zu reduzieren, dann könnt ihr gemeinsam ungefähr "+str(einsparen/1000)+" Tonnen CO2 einsparen.<font>""",unsafe_allow_html=True)
    
        c1,c2,c3 = st.beta_columns((1,3,1))
        df = pd.DataFrame({'Zeit':['nachher', 'voher'], 'Tonnen CO<sub>2</sub>':[(menschen*7.243)-einsparen/1000, menschen*7.243]})
        
        fig = px.bar(df, x='Tonnen CO<sub>2</sub>', y="Zeit", orientation='h')
        c2.plotly_chart(fig)
        
#===================================================================================================
elif navigation=='SchülerInnen-Guide':
    c1, c2 = st.beta_columns([1, 1])
    c1.write("""
            # SchülerInnen-Guide - Fußabdruck der Zukunft
         """)
    c1.write("Willkommen auf der Schülerseite von „Fußabdruck der Zukunft“. Hier findest du eine Anleitung, die dich durch unsere Seite führt. Los geht’s!")
    image1 = Image.open('Schüler.jpg')
    c2.image(image1, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("***")
    
    checkbox8 = st.beta_expander("Aufgabe 1: Was ist der Treibhauseffekt?")
    checkbox8.write("""
                    ## Aufgabe 1
                Schau dir zum Einstieg in das Thema das Video „$CO_{2}$ und der Treibhauseffekt - einfach erklärt“ an. 
                    """)
    c1, c2, c3 = checkbox8.beta_columns([1, 2, 1])
    c2.video(data='https://www.youtube.com/watch?v=CR3q9vnSlFQ', format='video/mp4', start_time=0)
    
    checkbox1 = st.beta_expander(label="Aufgabe 2: Einführung in das Thema CO2-Fußabdruck")
    checkbox1.write("""
            ## Aufgabe 2
            Wechsele zur Startseite und lies dir alle Informationen durch. Schau dir das Video „Klimaschutz im Alltag – Welchen Einfluss haben wir?“ an. 
            """)
    
    checkbox2 = st.beta_expander(label="Aufgabe 3: Berechnung deines CO2-Fußabdrucks")
    checkbox2.markdown("""
                 ## Aufgabe 3
                Wechsele jetzt zum "Rechner: Fußabdruck-Optimierung". Führe den Schritt 1 durch und schau dir dein Ergebnis an. Stell dir selbst die Fragen: <br>
                <i>„Welcher Bereich in meinem Leben hat den größten Verbrauchswert?“ <br>
                „Habe ich erwartet, dass die Verteilung so aussieht? Wenn ja, wieso?“ <br>
                „Sind meine Werte größer oder kleiner als die durchschnittlichen Werte?“ <br>
                „Ist das gut oder eher schlecht?“</i> """, unsafe_allow_html=True)
    
    
    checkbox3 = st.beta_expander(label="Aufgabe 4: Dein CO2-Fußabdruck in der Zukunft")
    checkbox3.write("""
             ## Aufgabe 4
            Führe jetzt die übrigen Schritte 2 bis 4 durch und schau dir das Ergebnis deines zukünftigen Fußabdrucks an. Verändere gerne deine Eingabe aus den Schritten 3 und 4. Welche Auswirkungen hat das auf dein Ergebnis?
            """)
    
    checkbox4 = st.beta_expander(label="Aufgabe 5: Gesellschaftlicher Einfluss")
    checkbox4.write("""
            ## Aufgabe 5
            Deutschland hat seine Klimaziele im Klimaschutzplan 2050 festgehalten. Was es damit auf sich hat erfährst du im Video "der Klimaschutzplan".
            """)
    c1, c2, c3 = checkbox4.beta_columns([1, 2, 1])
    c2.video(data='https://www.youtube.com/watch?v=OYwC3nkvCUo', format='video/mp4', start_time=0)
    checkbox4.write("""
            Damit das Klimaschutzziel erreicht werden kann, müssen alle mitmachen. Um dir ein Gefühl dafür zu geben, welchen Einfluss das Handeln von dir und den Menschen in deinem Umfeld hat, haben wir den "Rechner: Gesellschaftlicher Einfluss" entwickelt. 
            Wechsele jetzt zum "Rechner: Gesellschaftlicher Einfluss". Führe den Rechner aus und verändere dabei deine Eingabewerte. Was fällt dir auf?
            """)
    
    checkbox5 = st.beta_expander(label="Aufgabe 6: Hintergrund der Berechnung deines CO2-Fußabdrucks")
    checkbox5.write("""
            ## Aufgabe 6
            Wir wollen dir jetzt erklären, wie wir den "Rechner: Fußabdruck-Optimierung" entwickelt haben und welche Überlegungen dahinter stecken.
            Wechsele dazu auf die Seite "Hintergrund: Fußabdruckberechnung". Hier wird dir Schritt für Schritt erklärt, wie der "Rechner: Fußabdruck-Optimierung" deinen persönlichen $CO_{2}$-Fußabdruck berechnet.
            Du wirst durch die einzelnen Kategorien geführt und findest dort auch Verweise auf die Quellen, aus denen unsere Daten stammen.<br>
            <br> Lies dir alles in Ruhe durch. Versuche dann selbst deinen $CO_{2}$-Verbrauch zu berechnen. Verwende dazu die Formeln der Seite und die Daten aus den Tabellen.
            Zur Überprüfung stehen dir deine Werte aus dem "Rechner:Fußabdruck-Optimierung" zur Verfügung.""", unsafe_allow_html=True)
    
    checkbox6 = st.beta_expander(label="Aufgabe 7: Hintergrund der Berechnung deines zukünftigen CO2-Fußabdrucks")
    checkbox6.write("""
            ## Aufgabe 7
            Nachdem du jetzt weißt, wie der $CO_{2}$-Fußabdruck berechnet wird, schauen wir uns als nächstes das $CO_{2}$-Budget an. Wechsele dazu auf die Seite "Hintergrund: Budgetberechnung".
            Lies dir alles in Ruhe durch und schau dir gerne das Video zum Klimaschutzplan noch einmal an, falls es dir hilft.
            Versuche anschließend selbst dein künftiges $CO_{2}$-Budget zu berechnen, indem du dir ein beliebiges Jahr bis 2050 auswählst. Wie wäre es zum Beispiel mit 2033?""", unsafe_allow_html=True)

    
    checkbox7 = st.beta_expander(label="Aufgabe 8: Überprüfung der Daten")
    checkbox7.write("""
                ## Aufgabe 8
                Beim Erstellen unseres Rechners zur Fußabdruck-Optimierung haben wir uns gefragt, ob unsere Ergebnisse glaubhaft sind. Das bedeutet, wie sicher kannst du dir als BenutzerIn sein, dass diese Werte auch stimmen? Um diese Frage zu beantworten haben wir die Seite "Hintergrund: Datenvalidierung" erstellt. 
                Wechsele zu dieser Seite und lies dir alles aufmerksam durch.<br>
                Du siehst in den Tabellen, die Werte, die wir mit den Durchschnittswerten für 2019 berechnet haben. Überprüfe für dich selbst, wie gut die Werte unseres Rechners mit dem Rechner des Umweltbundesamtes übereinstimmen. Führe dazu den $CO_{2}$-Rechner auf der Seite https://uba.co2-rechner.de/de_DE/living-pt#panel-calc aus.
                Vergleiche dann diesen Wert mit dem Fußabdruck, den du auf unserer Seite berechnet hast. Was sagst du zu deinen Ergebnissen?""", unsafe_allow_html=True)
        
        
#========================================================================================================
        
elif navigation == 'Hintergrund: Fußabdruckberechnung':
    st.markdown("""
             ## Berechnung des persönlichen $CO_{2}$-Verbrauchs
             Zur Ermittlung des individuellen CO<sub>2</sub>-Verbrauchs wird der persönliche 
             Gesamtverbrauch in verschiedene Bereiche unterteilt.
             Unser Ziel ist es, die Eingabe für die Benutzerin/ den Benutzer möglichst einfach zu gestalten.
             Deshalb ist es in einigen Bereichen notwendig Verallgemeinerungen zu treffen.
             Zur Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs pro Jahr sollen folgende 
             Bereiche berücksichtig werden:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown("""<ol> <li>Nahrung</li><li>Wohnen</li><li>Mobilität</li><li>Konsum (Kleidung)</li>""",unsafe_allow_html=True)
    st.markdown("""Diese Bereiche wurden ausgewählt, weil sie zum persönlichen CO<sub>2</sub>
             -Gesamtverbrauch den größten Beitrag leisten [12]. Gleiches gilt für die Aspekte, 
             die in den jeweiligen Kategorien vom Benutzer abgefragt werden. 
             Auf der Grundlage des persönlichen Verhaltens wird der individuelle CO<sub>2</sub>-Verbrauch berechnet.""", unsafe_allow_html=True)
    st.markdown("***")
    st.markdown("""
             ## Nahrung
             Die Datengrundlage für die Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs durch die Nahrung bildet die folgende Tabelle.
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image3= Image.open('Tab3_Nahrungswerte.PNG')
    c2.image(image3, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("Zur Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs durch die Nahrung werden von der Benutzerin/ dem Benutzer folgende Aspekte selbst angegeben:",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Verzehrmenge Fleisch pro Woche in kg</li><li>Regionale Lebensmittel</li>', unsafe_allow_html=True)
    st.markdown("""Für die Berechnung des CO<sub>2</sub>-Verbrauchs durch die Nahrung werden die durchschnittlichen 
             jährlichen Verzehrmengen mit den entsprechenden CO<sub>2</sub>-Werten multipliziert und über 
             alle Lebensmittelgruppen aufaddiert, wobei die Verzehrmenge Fleisch von der Benutzerin/ dem Benutzer 
             angegeben wird. Dabei wird nur diese Information von der Benutzerin/ dem Benutzer abgefragt, weil der 
             CO<sub>2</sub>-Wert von Fleisch einen großen Anteil des CO<sub>2</sub>-Wertes der Nahrung ausmacht. Für die
             übrigen Lebensmittelgruppen wurden Durchschnittswerte angenommen, damit die Eingabe 
             übersichtlich bleibt. Entsprechend muss bei der Berechnung diese wöchentliche Angabe 
             durch Multiplikation mit dem Faktor 53 (Anzahl der Wochen pro Jahr) berücksichtigt 
             werden. Damit der Aspekt „2. Regionale und saisonale Lebensmittel“ in die Berechnung 
             einfließen kann, werden gemäß [4] die entsprechenden Faktoren aus Tabelle 4 einbezogen. 
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image4= Image.open('Tab4_regio.PNG')
    c2.image(image4, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""
             Damit wird der CO<sub>2</sub>-Wert der Nahrung gemäß dem folgenden 
             Zusammenhang berechnet:
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image5= Image.open('Formel_Essen.PNG')
    c2.image(image5, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Wohnen")
    st.markdown("""Die Datengrundlage für die Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs
             durch den Aspekt Wohnen bildet die folgende Tabelle. """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image7= Image.open('Tab5_Wohnen.PNG')
    c2.image(image7, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Der berechnete Wert des persönlichen CO<sub>2</sub>-Verbrauchs durch den Aspekt
             Wohnen soll personalisiert werden, indem die Benutzerin/ der Benutzer folgende Angaben macht:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Wohnfläche pro Person</li><li>Eingestellte Raumtemperatur</li>', unsafe_allow_html=True)
    st.markdown("""Die Beschränkung auf diese beiden Aspekte wurde auch hier getroffen, um die Eingabe,
                auch im Hinblick auf jüngere BenutzerInnen, zu erleichtern. Entsprechend der Wohnungsgröße 
                wird dann der jährliche Verbrauch mit entsprechenden Durchschnittswerten ermittelt. 
             Mit diesen beiden Größen wird der CO<sub>2</sub>-Verbrauch der Benutzerin/ des Benutzers für den
             Aspekt Wohnen durch die folgende Beziehung berechnet:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image8= Image.open('Formel_Wohnen.PNG')
    c2.image(image8, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Mobilität")
    st.markdown("""Die Datengrundlage für die Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs 
             durch den Aspekt Mobilität bildet die folgende Tabelle. """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image9= Image.open('Tab6_Mobilität.PNG')
    c2.image(image9, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Außerdem wird der CO<sub>2</sub>-Wert in kgCO<sub>2</sub> pro km für Flugzeuge 
             gemäß [4] mit 0,197 angenommen. 
             Zur Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs unter dem Aspekt
             Mobilität sollen folgende Angaben der Benutzerin/ des Benutzers berücksichtigt werden:
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown("<ol> <li>Gefahrene Autokilometer pro Jahr pro Person</li><li>Flugstunden der letzten vier Jahre <sup>5</sup></li>",unsafe_allow_html=True)
    st.markdown("""Die Auswahl der Aspekte erfolgte auf Grund ihres großen Beitrags zum CO<sub>2</sub>-Wert für den Bereich Mobilität. Unter 
                Berücksichtigung dieser Angaben wird der CO<sub>2</sub>-Wert gemäß dem folgenden
                Zusammenhang berechnet:
                """, unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image20= Image.open('Formel_Mobilität.PNG')
    c2.image(image20, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Konsum")
    st.markdown("""Die Datengrundlage für die Berechnung des persönlichen CO<sub>2</sub>-Verbrauchs 
                durch den Konsum bildet die folgende Tabelle. """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image10= Image.open('Tab7_Konsum.PNG')
    c2.image(image10, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Die Benutzerin/ Der Benutzer soll dabei folgende Angabe zu seinem Konsumverhalten machen:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Anzahl gekaufte Kleidungsstücke pro Jahr</li>', unsafe_allow_html=True)
    st.markdown("""Die Abfrage beschränkt sich auf diesen Bereich, weil die Berücksichtigung weiterer 
             Konsumaspekte schwer abzuschätzen ist und schnell zu einer hohen Komplexität führt.
             Diese Abfrage ermöglicht eine einfache Einbeziehung eines Teilaspekts des Konsums.
             Auch wenn dies hier nur einen kleinen Anteil darstellt, wird dennoch dazu angeregt
             darüber nachzudenken, dass unser Konsum ebenso einen wesentlichen Einfluss auf 
             unseren CO<sub>2</sub>-Fußabdruck hat.
             Unter Berücksichtigung dieser Angabe wird der persönliche CO<sub>2</sub>-Verbrauch 
             durch den Aspekt Konsum durch den folgenden Zusammenhang berechnet.""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image11= Image.open('Formel_Konsum.PNG')
    c2.image(image11, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.markdown("""<font size = 2>
                <sup>2</sup> Die in Tabelle 3 dargestellten Angaben der Kalorien pro kg der 
                entsprechenden Lebensmittelgruppen wurden aus den Daten aus [3] berechnet. 
                Dabei wurde jeweils der Mittelwert aller Angaben einer Lebensmittelgruppe gebildet.<br>
                <sup>3</sup> Die Kategorie beinhaltet hier und im Folgenden auch die Lebensmittelgruppe Fisch
                <sup>4</sup> Der Zeitraum für die Abfrage der Flugstunden wurde auf vier Jahre festgelegt, 
                da davon auszugehen ist, dass nicht jedes Jahr eine Flugreise erfolgt. Die Angabe der Flugstunden soll so vereinfacht werden. 
                </font>""",unsafe_allow_html=True)
    
#======================================================================================================
    
elif navigation == "Hintergrund: Budgetberechnung":
    st.markdown("""
             ## Berechnung des pro Kopf $CO_{2}$-Budgets (Deutschland)
             Zunächst soll der Anteil der Bevölkerung am CO<sub>2</sub>-Gesamtverbrauch von Deutschland 
             bestimmt werden. Dieser ermöglicht es uns im weiteren Verlauf ausgehend von künftigen 
             Klimazielen des Landes das persönliche CO<sub>2</sub>-Budget pro Kopf zu berechnen und 
             Handlungsempfehlungen zur Reduzierung des persönlichen CO<sub>2</sub>-Verbrauchs
             auszusprechen. 
            Die folgende Tabelle bildet die Grundlage der Berechnung des Anteils der Bevölkerung 
            am CO<sub>2</sub>-Gesamtverbrauch von Deutschland.
            """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image12= Image.open('Tab1_Einwohnerzahlen.PNG')
    c2.image(image12, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Zunächst kann nun der gesamte durch die Bevölkerung verursachte CO<sub>2</sub>-Verbrauch 
              A<sub>Bev</sub> für die entsprechenden Jahre aus Tab. 1 berechnet werden.""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([2,3,1])
    image13= Image.open('Formel_Bev1.PNG')
    c2.image(image13, width=300, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Somit kann der prozentuale Anteil der durch die Bevölkerung verursachten Emissionen
             P<sub>Bev</sub> an den bundesweiten Emissionen bestimmt werden.""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([2,3,1])
    image14= Image.open('Formel_Bev2.PNG')
    c2.image(image14, width=300, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Die gemäß dieser Formeln berechneten Werte sind nachfolgend dargelegt.""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image15= Image.open('Tab2_Einwohner.PNG')
    c2.image(image15, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Zuletzt wird der Mittelwert $\overline{P_{Bev}}$ über alle so bestimmten
             Anteile des CO<sub>2</sub>-Verbrauchs der Bevölkerung gebildet.""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([2,3,1])
    image16= Image.open('Wert_Bev.PNG')
    c2.image(image16, width=300, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Dieser Wert sagt aus, dass der durch die Bevölkerung verursachte CO<sub>2</sub>-Verbrauch
             ungefähr 83% ausmacht <sup>1</sup>.
             Er erlaubt es uns für künftige bundesweite CO<sub>2</sub>-Budgets ein pro Kopf Budget 
             vorherzusagen. """,unsafe_allow_html=True)
    st.markdown("***")
    st.write("## Künftige pro Kopf $CO_{2}$-Budgets (Deutschland)")
    st.markdown("""
             Damit künftige pro Kopf CO<sub>2</sub>-Budgets berechnet werden können, soll hier das zu 
             Grunde liegende Modell vorgestellt werden. Die Daten basieren auf dem Klimaschutzplan 
             2050, der vom Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit (BMU)
             veröffentlicht wurde [2].""",unsafe_allow_html=True) 
    c1,c2,c3 = st.beta_columns((1,3,1))
    c2.video(data='https://www.youtube.com/watch?v=OYwC3nkvCUo&ab_channel=Bundesumweltministerium', format='video/mp4', start_time=0)
    st.write("""
             Demnach sollen ausgehend vom Jahr 1990 bis 2030 die CO<sub>2</sub>-Emissionen mindestens um 55%,
             bis 2040 um 70% und bis 2050 um 80%-95% gesenkt werden. Die sich aus diesen Zielen 
             ergebenden CO<sub>2</sub>-Budgets sind in Abbildung 1 dargestellt.  
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image17= Image.open('Emissionsziel.PNG')
    c2.image(image17, width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""Mit dieser Datengrundlage und dem zuvor ermittelten Anteil des CO<sub>2</sub>-Verbrauches
             der Bevölkerung kann der pro Kopf Ausstoß für künftige Szenarien ermittelt werden.
             Zunächst werden die Ziele des Klimaschutzplans in die entsprechenden CO<sub>2</sub>-Budgets pro 
             Kopf überführt. Tabelle 11 zeigt die entsprechenden Werte. """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    imageschutzplan= Image.open('Tab11.PNG')
    c2.image(imageschutzplan, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Auf dieser Grundlage können die folgenden Zusammenhänge, die sich abschnittsweise als lineare Funktionen gemäß den Zielen des Klimaschutzplan ergeben, aufgestellt werden:")
    c1,c2,c3 = st.beta_columns((1,3,1))
    c2.write("Für den Zeitraum von 2020 bis 2030:")
    c1,c2,c3 = st.beta_columns((2,3,2))
    c2.write("$maxco2_{Jahr} = -0.185$ Tonnen $\cdot (Jahr - 2020) + 7.44$ Tonnen")
    c1,c2,c3 = st.beta_columns((1,3,1))
    c2.write("Für den Zeitraum von 2030 bis 2040:")
    c1,c2,c3 = st.beta_columns((2,3,2))
    c2.write("$maxco2_{Jahr} = -0.176$ Tonnen $\cdot (Jahr - 2030) + 5.59$ Tonnen")
    c1,c2,c3 = st.beta_columns((1,3,1))
    c2.write("Für den Zeitraum von 2040 bis 2050:")
    c1,c2,c3 = st.beta_columns((2,3,2))
    c2.write("$maxco2_{Jahr} = -0.184$ Tonnen $\cdot (Jahr - 2040) + 3.83$ Tonnen")
    
    st.markdown("***")
    st.markdown("""<font size = 2>
                <sup>1</sup> In der Literatur wird dieser Wert oft geringer angegeben. Es kommt darauf an, welche Größen beim pro Kopf Verbrauch berücksichtigt werden. Bei den Berechnungen wird davon ausgegangen, dass das Verhältnis zwischen dem Anteil des CO2-Ausstoßes der Bevölkerungen und dem gesamten Ausstoß gleichbleiben. </font>""",unsafe_allow_html=True)
    
    
    
#====================================================================================================

elif navigation == 'Hintergrund: Fußabdruckoptimierung':
    st.markdown("""
                Ziel unserer Optimierung ist es, der Benutzerin/ dem Benutzer individuelle Handlungsempfehlungen 
                über die Verringerung ihres/seines CO<sub>2</sub>-Ausstoßes zu geben. Diese Empfehlungen 
                sollen von den Präferenzen der Nutzerin/ des Nutzers abhängig sein. <br>Unser Modell deckt fünf Bereiche ab, 
                für welche Empfehlungen gegeben werden:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,10,1))
    c2.markdown("""<ol><li>Fleischkonsum</li><li>Heizen</li><li>Autokilometer</li>
                <li>Flugstunden</li><li>Kleiderkonsum</li></ol></div>""",unsafe_allow_html=True)
    st.write("""Dazu erhalten wir als Eingabedaten verschiedene Informationen, 
                die in vier Bereiche unterteilt werden können:""")
    c1,c2,c3 = st.beta_columns((1,10,1))
    c2.markdown("""<ol><li>aktuelle Nutzdaten</li><li>Präferenzen</li><li>Minimalwerte</li>
                <li>Optimierungsjahr</li></ol>""",unsafe_allow_html=True)
    st.markdown("""Auf der Basis dieser Daten erstellen wir das Optimierungsmodell.<br><br>
                <font size = 5><b>Schritt 1: Eingabedaten verarbeiten</b></font><br><br>
                <u>Aktuelle Nutzdaten:</u> Für unser Modell benötigen wir die CO<sub>2</sub>-Emissionen, 
                die durch die einzelnen Handlungen erzeugt werden. Aus diesen berechnen wir 
                die aktuellen CO<sub>2</sub>-Emissionen der einzelnen Komponenten. Wie wir das berechnen
                und welche Daten wir nutzen findest du in Abschnitt 'Hintergrund: 
                Fußabdruckberechnung'.<br>
                Als Ergebnis erhalten wir die Werte""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$co2akt_{i}$ mit $i \in I = \{Fleisch, Heizen, Auto, Flugzeug, Kleidung\}$")
    st.write("sowie")
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$co2ess_{j}$ mit $j \in J = \{Gemüse, Obst, Milchprodukte, Brot, Kartoffeln, Eier\}$")
    st.write("und") 
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$co2strom$ & $co2heizen$,")
    st.write(""" wobei zu beachten ist, dass sich die Gesamtemissionen des Bereichs 'Heizen' aus den Emissionen
                beim Heizen bis zu 18 Grad ($co2heizen$) und den Emissionen, die beim Heizen
                über 18 Grad entstehen $(co2akt_{Heizen})$,
                zusammensetzen.
                """)
    st.markdown("""<u>Optimierungsjahr:</u> Anhand des Optimierungsjahres berechnen wir den maximal 
                möglichen CO<sub>2</sub>-Ausstoß der Nutzerin/ des Nutzers, d.h. ihr/ sein CO<sub>2</sub>-Budget. Wie wir das 
                berechnen und welche Daten wir nutzen findest du in Abschnitt 'Hintergrund: 
                Budgetberechnung'.<br>
                Als Ergebnis erhalten wir den Wert""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$maxco2$.")
    st.markdown("""<font size = 5><b>Schritt 2: Variablen einführen</b></font><br><br>
                Die Handlungsempfehlungen für die Nutzerin/ den Nutzer werden zunächst als Prozentsätze 
                berechnet. Diese geben an, auf wie viel Prozent die Nutzerin/ der Nutzer ihren/ seinen Verbrauch 
                im Vergleich zum vorherigen Verbrauch reduzieren muss, um das CO<sub>2</sub>-Budget 
                einzuhalten. Dazu führen wir die folgenden Variablen ein:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$var_{i}$ mit $i \in I = \{Fleisch, Heizen, Auto, Flugzeug, Kleidung\}$")
    c2.write("$0 \leq var_{i} \leq 1$")
    c2.write("$var_{i}$ $\widehat{=}$ Anteil zu dem Aspekt beibehalten wird")
    st.markdown("""<font size = 5><b>Schritt 3: Zielfunktion</b></font><br><br>
                Die Präferenzen der Nutzerin/ des Nutzers sollen maximiert werden, damit die Reduktion 
                der Emissionen möglichst komfortabel geschieht. Von der Nutzerin/ dem Nutzer erhalten wir direkt
                ihre/ seine Präferenzwerte. Diese liegen zwischen 1 und 10, je höher der Wert desto
                höher auch die Präferenz. Da $var_{i}$ die Beibehaltung der jeweiligen Kategorien 
                angibt, erhalten wir durch Multiplikation mit den passenden Präferenzwerten 
                den Gesamtkomfort. Um höhere Präferenzwerte deutlicher von niedrigen abzugrenzen
                quadrieren wir die Präferenzwerte. Wir erhalten:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("maximize $\displaystyle\sum\limits_{i \in I} pref_{i}^{2} \cdot var_{i}$")
    st.markdown("""<font size = 5><b>Schritt 4: Nebenbedingungen - Budget einhalten</b></font><br><br>
               Die CO<sub>2</sub>-Emissionen der Nutzerin/ des Nutzers sollen so weit herabgesetzt werden, dass sie ihr/er sein
               CO<sub>2</sub>-Budget $maxco2$ einhält (siehe Schritt1). Der CO<sub>2</sub>-Ausstoß setzt sich aus
               den Werten für die fünf Optimierungskategorien, sowie Essen, Strom und dem 
               Basisheizwert zusammen 
               (siehe Schritt 1). Durch Multiplikation der $var_{i}$ mit den passenden co2akt$_{i}$ 
               erhalten wir die neuen Emissionswerte.<br>
               Nun gilt es zu beachten, dass eine Reduktion des Fleischkonsums zwingend zu einem 
               höheren Konsum anderer Lebensmittel führt, um den Kalorienhaushalt zu decken. Daher 
               führen wir Variablen""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$var_{j}$ für $j \in J$ mit $var_{j}  \geq 0$  $j \in J$")
    c2.write("$var_{j} \widehat{=}$ Vervielfachung der Lebensmittelgruppe $j$ in kg")
    st.write("""ein, die diesen Austauschprozess simulieren.""")
    st.markdown(""" Um eine möglichst realistische Einschätzung zu geben, wird der tägliche 
               Kalorienbedarf ausgehend von der angegebenen Verzehrmenge Fleisch und den 
               durchschnittlichen Verzehrmengen der übrigen Lebensmittelgruppen berechnet.
               Dies geschieht auf Basis der Daten die in Tabelle 12 zu finden sind.
                   """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,2,1))
    imagekal2= Image.open('Tab12.PNG')
    c2.image(imagekal2, use_column_width=True,width=700, clamp=False, channels='RGB', output_format='auto')
    st.markdown(""" Zu der vorgeschlagenen Reduzierung der Verzehrmenge Fleisch wird die entsprechende
               Kalorienangabe ermittelt"""
               ,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$(1-var_{Fleisch}) \cdot akt_{Fleisch} \cdot 53 \cdot 1860$")
    st.markdown(""" und gleichmäßig auf die anderen Lebensmittelgruppen verteilt:"""
               ,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$(1-var_{Fleisch}) \cdot akt_{Fleisch} \cdot 53 \cdot 1860 \cdot 1/6$")
    st.write("""Abschließend wird der zusätzliche Kalorienwert in Kilogramm umgerechnet. Dies geschieht
             durch Division durch die Kilokalorien pro Kilogramm des entsprechenden Lebensmittels. Wir erhalten
             die zusätzliche Verzehrmenge
                """)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$var_{j} \cdot menge_{j} = (1-var_{Fleisch}) \cdot akt_{Fleisch} \cdot 53 \cdot 1860 \cdot 1/6 \cdot 1/kalorien_{j}$  $j \in J$")
    st.write("""wobei $menge_{j}$ der ursprünglichen Verzehrmenge der Lebensmittelgruppe $j$ entspricht.
                """)
    st.markdown("""Für den Gesamtausstoß addieren wir zu den bereits genannten Summen noch die 
                CO<sub>2</sub>-Emissionen für Strom und den Heiz- sowie den Nahrungsbasiswert. Wir erhalten damit die Budget-Bedingung:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$\displaystyle\sum\limits_{i \in I} var_{i} \cdot co2akt_{i} + \displaystyle\sum\limits_{j \in J} var_{j} \cdot co2ess_{j} + co2strom + co2heizen + co2nahrung \leq maxco2$")
    st.markdown("""<font size = 5><b>Schritt 5: Nebenbedingung - Minimalwerte einhalten</b></font><br><br>
                Unser Rechner bietet die Möglichkeit, Minimalwerte für einzelne Kategorien 
                zu setzen. Um diese einzuhalten muss garantiert sein, dass der von unserer 
                Handlungsempfehlung empfohlene Wert nicht unter dieser Minimalgrenze liegt.
                Da der neue Wert sich aus der Multiplikation des alten Werts $akt_{i}$ mit 
                dem optimierten Prozentsatz $var_{i}$ zusammensetzt, muss gelten:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$var_{i} \cdot akt_{i} \geq minval_{i}$  $i \in I \setminus \{Heizen\}$")
    st.markdown(""" Dabei ist zu beachten, dass die Variable $var_{Heizen}$ nur die Werte über
                18 Grad Celsius beeinflussen kann. Daher ensteht eine leichte Abwandlung dieser
                Nebenbedingung für den Bereich 'Heizen':
                """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$18 + var_{Heizen} \cdot (akt_{Heizen}-18) \geq minval_{Heizen}$")
    st.markdown("""<font size = 5><b>Schritt 6: Nebenbedingung - Ausgeglichene Optimierung</b></font><br><br>
                Das aktuelle Optimierungsmodell würde die Variablen $var_{i}$ nacheinander 
                auf 0 setzen (bzw. auf den Minimalwert). Bei unterschiedlichen Präferenzwerten
                würde dies in aufsteigender Reihenfolge bezüglich der Präferenzwerte geschehen,
                bei gleichen Präferenzwerten in Abhängigkeit des höchsten Wertes 
                co2akt$_{i}$. Das ist für das alltägliche Leben allerdings wenig plausibel. 
                Daher streben wir eine möglichst ausgeglichene Optimierung im Sinne der 
                gesetzten Präferenzwerte an. Das bedeutet, dass die Optimierung je 
                ausgeglichener sein soll, desto ausgeglichener die Präferenzwerte sind.
                Dazu betrachten wir die Summe über die Beträge aller Optimierungsvariablen
                $var_{i}$, d.h. die Summe über die Unterschiede. Als Schranke für diese 
                Summe wählen wir den quadrierten maximalen Unterschied zweier Präferenzwerte.
                Diese hat sich in Modellierungsversuchen als besonders effektiv erwiesen. 
                Wir erhalten damit die Nebenbedingung:""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$\displaystyle\sum\limits_{i_{1}=1}^{5} \displaystyle\sum\limits_{i_{2}=i_{1}}^{5} |var_{i_{1}} - var_{i_{2}}| \leq \max\limits_{i\prime, i\prime\prime \in I} |pref_{i\prime} - pref_{i\prime\prime}|^{2}$ $i_{1}, i_{2} \in I$")
    st.markdown("""Anmerkung: An dieser Stelle wird erstmals klar, warum die Unterscheidung
                in den Heizbasiswert und die weiteren Heizemissionen getroffen wurde. 
                Aufgrund unserer Datenbasis [4] können nur Heizwerte über 18 Grad Celsius 
                beachtet werden. Eine Möglichkeit wäre es nun, lediglich über den Minimalwert
                (siehe Schritt 5) zu arbeiten und diesen auf 18 zu setzen. Das würde allerdings
                dazu führen, dass der Prozentsatz sich nur in einem sehr kleinen Bereich
                bewegen kann, was einer ausgeglichenen Optimierung wiederspricht.""",unsafe_allow_html=True)
    
    st.markdown("""<font size = 5><b>Zusammenfassend ergibt sich damit das folgende 
                Optimierungsmodell:</b></font><br>""",unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    imageopt= Image.open('Optimierungsmodell.PNG')
    c2.image(imageopt, width=700, use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    
    lpumformung = st.beta_expander("Hintergrund: Computergestützte Berechnung - Lösung des Optimierungsmodells")
    lpumformung.markdown("""<font size = 5><b>Computergestützte Berechnung - Lösung des Optimierungsmodells</b></font><br><br>
                         Für die Implementierung der Berechnung verwenden wir die Programmiersprache
                         <i> python </i>. Diese bietet viele hilfreiche Pakete und Softwareumgebungen. Zur Lösung unseres
                         Optimierungsmodells verwenden wir die Softwareumgebung <i>scipy</i>.
                         Die dort implementierte Methode <i> scipy.optimize.linprog</i> bietet die
                         Möglichkeit, verschiedene Algorithmen zur Lösung von Linearen Programmen
                         zu verwenden (mehr dazu siehe: <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html" target="_blank">hier</a>).
                         Wir verwenden in unserer Berechnung die Simplex-Methode. <br>
                         Dazu muss das obige Optimierungsmodell in die Allgemeine Form für Lineare Programme
                         überführt werden:
                     """,unsafe_allow_html=True)
    c1,c2,c3 = lpumformung.beta_columns((1,4,1))
    lpsf= Image.open('LP_Sf.PNG')
    c2.image(lpsf, width=300, clamp=False, channels='RGB', output_format='auto')
    
    lpumformung.markdown("""
                         <b>Überführung in LP-Standardform</b><br>
                         <u>Schritt 1 - Nebenbediungen Ungleichheit:</u>
                         Die Nebenbedingung zur Budgeteinhaltung ist bereits in der geforderten Form.
                         Durch eine Multiplikation mit (-1) ist dies auch die Nebenbedingung zur Einhaltung
                         der Minimalwerte. Die Nebenbedingung der ausgeglichenen Optimierung beinhaltet eine
                         Betragsfunktion. Zur Auflösung dieser definieren wir uns die Variablen
                     """,unsafe_allow_html=True)
    c1,c2,c3 = lpumformung.beta_columns((1,4,1))
    c2.write("$var_{diffij} = |var_{i} - var_{j}|$  für  $i,j \in J$ .")
    lpumformung.markdown("""
                         Daraus ergibt sich
                     """,unsafe_allow_html=True)
    c1,c2,c3 = lpumformung.beta_columns((1,4,1))
    c2.write("$var_{diffij} - |var_{i} - var_{j}| = 0$  für  $i,j \in J$")
    lpumformung.markdown("""
                         und damit
                     """,unsafe_allow_html=True)
    c1,c2,c3 = lpumformung.beta_columns((1,4,1))
    c2.write(" 1) $var_{diffij} - var_{i} + var_{j} \leq 0$  für  $i,j \in J$")
    c2.write(" 2) $var_{diffij} + var_{i} - var_{j} \leq 0$  für  $i,j \in J$")
    lpumformung.markdown("""
                         Die Nebenbedigung der Ungleichung ist folglich
                     """,unsafe_allow_html=True)
    lpnb2= Image.open('LP_Nb2.PNG')
    lpumformung.image(lpnb2, width=1000, clamp=False, channels='RGB', output_format='auto')
    lpumformung.markdown("""
                         <u>Schritt 2 - Nebenbedingung Gleichheit:</u>
                         Unser Optimierungsmodell beinhaltet eine Nebenbedingung mit Gleichheit, 
                         die Kalorienausgleichsbedingung. Diese müssen wir so umstellen, dass
                         der Vektor auf der rechten Seite b<sub>eq</sub> und die Matrix A<sub>eq</sub>
                         auf der linken Seite lediglich Konstanten enthalten. Dazu stellen wir um
                         und erhalten
                     """,unsafe_allow_html=True)
    c1,c2,c3 = lpumformung.beta_columns((1,4,1))
    c2.write("$var_{j} + var_{Fleisch} \cdot akt_{Fleisch} \cdot 53 \cdot 1860 \cdot 1/6 \cdot 1/kalorien_{j} = menge_{j} \cdot 365 + akt_{Fleisch} \cdot 53 \cdot 1860 \cdot 1/6 \cdot 1/kalorien_{j}$  $j \in J$ .")
    lpumformung.markdown("""
                         Daraus ergibt sich die Gleichung
                     """,unsafe_allow_html=True)
    lpnb1= Image.open('LP_Nb1.PNG')
    lpumformung.image(lpnb1, width=1000, clamp=False, channels='RGB', output_format='auto')
    lpumformung.markdown("""
                         <u>Schritt 3 - Zielfunktion:</u>
                         Um die Maximierung zu einer Minimierung umzuformen multiplizieren wir die quadrierten
                         Präferenzwerte mit (-1). Wir erhalten die Zielfunktion
                     """,unsafe_allow_html=True)
    lpzf= Image.open('LP_Zf.PNG')
    lpumformung.image(lpzf, width=1000, clamp=False, channels='RGB', output_format='auto')
    
    lpumformung.markdown("""
                         Mit den Definitionen von c, A<sub>ub</sub>, b<sub>ub</sub>, A<sub>eq</sub> und b<sub>eq</sub>
                         und <i>scipy</i> erhalten wir die optimierten Variablen var<sub>Fsch</sub>, var<sub>Heizen</sub>, var<sub>Auto</sub>, var<sub>Flugzeug</sub> und var<sub>Konsum</sub>.
                         """,unsafe_allow_html=True)
    
    st.markdown("***")
    st.markdown("""<font size = 2>
                <sup>3</sup> Die Kategorie beinhaltet hier und im Folgenden auch die Lebensmittelgruppe Fisch.
                </font>""",unsafe_allow_html=True)
    
    
    
#======================================================================================================          
                
elif navigation == "Hintergrund: Datenvalidierung":
    st.markdown("""Nach dem Aufstellen des Modells ist es notwendig, die mit unserer Modellierung berechneten CO<sub>2</sub>-Verbrauchswerte auf ihre Sinnhaftigkeit zu überprüfen. 
             Die CO<sub>2</sub>-Werte, die das Modell in den einzelnen Kategorien berechnet, sollen mit dem CO<sub>2</sub>-Rechner des Umweltbundesamtes [6] verglichen werden. 
             Außerdem soll die mit dem Modell berechnete gesamte CO<sub>2</sub>-Verbrauch überprüft werden. Hierzu wird der pro Kopf Verbrauch aus dem Jahr 2019 [1.1] mit den entsprechenden Durchschnittswerten aus diesem Jahr simuliert.
             """,unsafe_allow_html=True)
    st.markdown("""
             Tabelle 9 vergleicht die laut „Fußabdruck der Zukunft“ berechneten CO<sub>2</sub>-Werte
             der jeweiligen verwendeten Kategorien mit den entsprechenden Werten des „CO<sub>2</sub>-Rechners 
             des Umweltbundesamtes“ [6]. Die Grundlage für die berechneten CO<sub>2</sub>-Werte bilden 
             die Durchschnittswerte aus Tabelle 8. Man kann aus den Werten in Tabelle 9 ablesen, 
             dass für die Kategorien Nahrung und Mobilität die Werte der beiden Rechner sehr gut
             übereinstimmen. Eine etwas größere Abweichung zeigt sich im Bereich Wohnen.
             Auffällig sind die großen Unterschiede der CO<sub>2</sub>-Werte in der Kategorie Konsum, 
             die auch zu einer großen Abweichung bei den Gesamtwerten führen. Der Wert des 
             „CO<sub>2</sub>-Rechners des Umweltbundesamtes“ ist sehr viel größer, da bei der Berechnung
             laut „Fußabdruck der Zukunft“ nur die gekauften Kleidungsstücke berücksichtigt
             werden. In diesem Bereich fließen also beim „CO<sub>2</sub>-Rechner des Umweltbundesamtes“ 
             weitere Aspekte mit ein, die den größeren CO<sub>2</sub>-Wert erklären.   
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab8= Image.open('Tab8.PNG')
    c2.image(image_tab8, use_column_width=True,width=700, clamp=False, channels='RGB', output_format='auto')
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab9= Image.open('Tab9.PNG')
    c2.image(image_tab9,use_column_width=True, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("""
             Tabelle 10 vergleicht die Werte laut „Fußabdruck der Zukunft“ berechneten CO<sub>2</sub>-Gesamtwerte
             mit dem pro Kopf CO<sub>2</sub>-Verbrauch aus dem Jahr 2019 laut „Statistica“. 
             Auch bilden die Werte aus Tabelle 8 die Grundlage der Berechnung laut „Fußabdruck der 
             Zukunft“. Die beiden Gesamtwerte stimmen fast überein. Das zeigt, dass der CO<sub>2</sub>
             -Wert aus dem Jahr 2019 sehr gut mit dem Rechner reproduziert werden konnte. 
             Die Abweichungen zu anderen Rechnern können damit erklärt werden, dass „Fußabdruck 
             der Zukunft“ keine öffentlichen Emissionen einbezieht. Außerdem werden oft im Bereich
             Konsum noch weitere Aspekte abgefragt und berücksichtigt.  
             Insgesamt hat die Validierung gezeigt, dass die durch „Fußabdruck der Zukunft“ 
             berechneten CO<sub>2</sub>-Werte zu den Werten aus anderen Rechnern passen. 
             Der Gesamtwert kann frühere CO<sub>2</sub>-Werte sehr gut nachbilden. Somit kann 
             angenommen werden, dass er für die Zukunft gute Vorhersagen treffen wird. 
             """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab10= Image.open('Tab10.PNG')
    c2.image(image_tab10, use_column_width=True,width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.markdown("""<font size = 2>
                <sup>6</sup> Dieser Wert wurde von uns geschätzt und entspricht einer Flugreise nach Mallorca im Jahr ;)</font>""",unsafe_allow_html=True)
    
elif navigation == "Hintergrund: Gesellschaftlicher Einfluss":
    st.markdown("""
                In einem ersten Schritt wird auf Basis der Angabe der Anzahl der EinwohnerInnen
                ein Ausgangswert der CO<sub>2</sub>-Emmissionen <i><b>CO2_Emissionen_Alt</b></i> in einem kleineren, besser vorstellbaren Rahmen
                bestimmt. Dazu verwenden wir den durchschnittlichen CO<sub>2</sub>-Emmissionswert des Rechners "Fußabdruck der Zukunft" mit Angaben aus dem
                Jahr 2019.<br>
                """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$CO2\_Emissionen\_Alt = AnzahlEinwohner \cdot 7243 kg$")
    st.markdown("""
                Im Folgenden kann eingegeben werden, welcher Anteil dieser EinwohnerInnengruppe <i><b>AnzahlEinwohner</b></i>
                sein Verhalten ändert und wie diese Veränderungen <i><b>(CO2Red_Fleisch, CO2Red_Auto, CO2Red_Flugzeug, CO2Red_Konsum)</b></i> aussehen sollen. Die entsprechenden Abfragen
                sind an die Kategorien des "Rechner: Fußabdruckoptimierung" angelehnt und werden analog berechnet.<br>
                """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$CO2\_Einsparen = AnzahlEinwohner \cdot (CO2Red\_Fleisch + CO2Red\_Auto + CO2Red\_Flugzeug + CO2Red\_Konsum)$")
    st.markdown("""
                Daraus ergibt sich der neue Wert der CO<sub>2</sub>-Emmissionen <i><b>CO2_Emissionen_Neu</b></i>
                """,unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns((1,4,1))
    c2.write("$CO2\_Emissionen_Neu = CO2\_Emissionen\_Alt - CO2\_Einsparen$")
    st.markdown("""
                Zur Veranschaulichung werden der Ursprungsausstoß und der geänderte Ausstoß in einem 
                Diagramm gegenübergestellt.
                """,unsafe_allow_html=True)
    

    
else:
    
    st.markdown("<font size = 5><b> Literaturverzeichnis </b></font>",unsafe_allow_html=True)
    st.markdown("""
                [1]: Statistica (2021). Bevölkerung: Einwohnerzahl von Deutschland von 1990 bis 2020. Verfügbar über: https://de.statista.com/statistik/daten/studie/2861/umfrage/entwicklung-der-gesamtbevoelkerung-deutschlands/#professional (letzter Zugriff: 07.07.2021)
                <br>[1.0]: Statistica (2021). Höhe der Treibhausgas-Emissionen in Deutschland in den Jahren 1990 bis 2020. Verfügbar über: https://de.statista.com/statistik/daten/studie/76558/umfrage/entwicklung-der-treibhausgas-emissionen-in-deutschland/ (letzter Zugriff: 07.07.2021)
                <br>[1.1]: Statistica (2021). Entwicklung der Pro-Kopf-CO2-Emissionen in Deutschland in den Jahren 1990 bis 2019. Verfügbar über: https://de.statista.com/statistik/daten/studie/153528/umfrage/co2-ausstoss-je-einwohner-in-deutschland-seit-1990/ (letzter Zugriff: 07.07.2021)
                <br>[1.2]: Statistica (2021). Pro-Kopf-Konsum von Obst in Deutschland in den Wirtschaftsjahren 2004/05 bis 2018/19. Verfügbar über: https://de.statista.com/statistik/daten/studie/6300/umfrage/pro-kopf-verbrauch-von-obst-in-deutschland/ (letzter Zugriff: 07.07.2021)
                <br>[1.3]: Statistica (2021). Pro-Kopf-Konsum von Gemüse in Deutschland in den Jahren 1950/51 bis 2019/20. Verfügbar über: https://de.statista.com/statistik/daten/studie/176731/umfrage/pro-kopf-verbrauch-von-gemuese-in-deutschland/ (letzter Zugriff: 07.07.2021)
                <br>[1.4]: Statistica (2021). Pro-Kopf-Konsum von Milch und Milcherzeugnissen in Deutschland nach Art in den Jahren 2017 bis 2019. Verfügbar über: https://de.statista.com/statistik/daten/studie/318237/umfrage/pro-kopf-konsum-von-milch-und-milcherzeugnissen-in-deutschland-nach-art/ (letzter Zugriff: 07.07.2021)
                <br>[1.5]: Statistica (2021). Pro-Kopf-Konsum von Kartoffeln in Deutschland in den Jahren 1950/51 bis 2019/20. Verfügbar über: https://de.statista.com/statistik/daten/studie/175422/umfrage/pro-kopf-verbrauch-von-kartoffeln-in-deutschland/ (letzter Zugriff: 07.07.2021)
                <br>[1.6]: Statistica (2021). Pro-Kopf-Konsum von Eiern in Deutschland in den Jahren 2004 bis 2020. Verfügbar über: https://de.statista.com/statistik/daten/studie/180345/umfrage/eier---nahrungsverbrauch-pro-kopf-seit-2004/ (letzter Zugriff: 07.07.2021)
                <br>[1.7]: Statistica (2021). Pro-Kopf-Konsum von Brotgetreide in Deutschland in den Jahren 1951/51 bis 2019/20. Verfügbar über: https://de.statista.com/statistik/daten/studie/175411/umfrage/pro-kopf-verbrauch-von-brotgetreide-in-deutschland-seit-1935/ (letzter Zugriff: 07.07.2021)
                <br>[1.8]: Statistica (2021). Fleischverbrauch in Deutschland pro Kopf in den Jahren 1991 bis 2020. Verfügbar über: https://de.statista.com/statistik/daten/studie/36573/umfrage/pro-kopf-verbrauch-von-fleisch-in-deutschland-seit-2000/ (letzter Zugriff: 07.07.2021)
                <br>[1.9]: Statistica (2021). Pro-Kopf-Konsum von Fisch und Fischerzeugnissen in Deutschland in den Jahren 1980 bis 2019. Verfügbar über: https://de.statista.com/statistik/daten/studie/1905/umfrage/entwicklung-des-pro-kopf-verbrauchs-an-fisch-in-deutschland/ (letzter Zugriff: 07.07.2021)
                <br>[2]: Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit (BMU) (2019).  Klimaschutzplan 2050: Klimapolitische Grundsätze und Ziele der Bundesregierung (2.Auflage). BMU. Verfügbar über: https://www.bmu.de/fileadmin/Daten_BMU/Download_PDF/Klimaschutz/klimaschutzplan_2050_bf.pdf (letzter Zugriff: 22.06.2021)
                <br>[3]: Fütterer, E. (2021). Kalorientabelle für Lebensmittel: Von Gemüse bis Fast Food. Verfügbar über: https://www.fitforfun.de/abnehmen/kalorientabelle-fuer-lebensmittel-307736.html (letzter Zugriff: 22.06.2021)
                <br>[4]: Kleinhückelkotten, S. & Neitzke, H.-P. (2016). Berechnung individueller Pro-Kopf-Verbräuche natürlicher Ressourcen nach Konsumbereichen. Umweltbundesamt. Verfügar über: https://www.umweltbundesamt.de/sites/default/files/medien/378/publikationen/texte_39_2016_anlagen_repraesentative_erhebung_von_pro-kopf-verbraeuchen_natuerlicher_ressourcen.pdf (letzter Zugriff: 07.07.2021)
                <br>[5]: Statistica (2021). Maximale Geschwindigkeit der weltweit schnellsten Passagierflugzeuge der Welt. Verfügbar über https://de.statista.com/statistik/daten/studie/1056126/umfrage/schnellste-passagierflugzeuge-der-welt-nach-maximaler-geschwindigkeit/ (letzter Zugriff: 07.07.2021)
                <br>[6]: Umweltbundesamt. Co2-Rechner des Umweltbundesamtes. Verfügbar über: https://uba.co2-rechner.de/de_DE/start#panel-calc (letzter Zugriff: 07.07.2021) 
                <br>[7]: Fußabdruck der Zukunft (2021). Verfügbar über https://share.streamlit.io/paulaflschr/footprintred/main/footprintapp.py (letzter Zugriff: 07.07.2021)
                <br>[8]: Statistica (2021). Wohnfläche je Einwohner in Wohnungen in Deutschland von 1991 bis 2019. Verfügbar über: https://de.statista.com/statistik/daten/studie/36495/umfrage/wohnflaeche-je-einwohner-in-deutschland-von-1989-bis-2004/ (letzter Zugriff: 07.07.2021)
                <br>[9]: Statistica (2021). Durchschnittliche Raumtemperatur in Haushalten in Deutschland, Österreich und der Schweiz im Jahr 2019. Verfügbar über: https://de.statista.com/statistik/daten/studie/1072340/umfrage/raumtemperatur-in-haushalten-in-deutschland-oesterreich-und-der-schweiz/ (letzter Zugriff: 07.07.2021)
                <br>[10]: Zippmann, V. (2020): In Mecklenburg-Vorpommern fahren Autofahrer am weitesten. Verfügbar über: https://www.autozeitung.de/jaehrliche-fahrleistung-197899.html (letzter Zugriff: 07.07.2021)
                <br>[11]: Statistica (2021). Die Welt kauft in der Pandemie weniger Kleidung. Verfügbar über: https://de.statista.com/infografik/24066/geschaetzter-durchschnittlicher-pro-kopf-absatz-von-kleidungsstuecken/ (letzter Zugriff: 07.07.2021)
                <br>[12]: Umweltbundesamt. Treibhausgasaustoß pro Kopf in Deutschland nach Konsumbereichen. Verfügbar über: https://www.umweltbundesamt.de/bild/treibhausgas-ausstoss-pro-kopf-in-deutschland-nach (letzter Zugriff: 09.07.2021) 
                <br>[13]: StromBoB. Durchschnittlicher Stromverbrauch in Deutschland. Verfügbar über: https://www.strombob.de/ratgeber/durchschnittlicher-stromverbrauch/ (letzter Zugriff: 11.07.2021)
                """, unsafe_allow_html=True)
    st.markdown("<font size = 5><b> Abbildungsverzeichnis </b></font>",unsafe_allow_html=True)
    st.markdown(""" Alle verwendeten Abbildung wurden von uns erstellt oder sind lizenzfreie Bilder, 
                welche von den Seiten <a href="https://pixabay.com/de/" target="_blank">Pixabay</a> und <a href="https://www.pexels.com/de-de/" target="_blank">Pexels</a>.
                """,unsafe_allow_html=True)
    st.markdown("***")
    st.markdown("<font size = 5><b> Impressum </b></font>",unsafe_allow_html=True)
    st.markdown(""" 
                Erstellt von Lena Bill & Paula Fleischer <br>
                Im Rahmen von der Veranstaltung Moderne Mathematik der Technischen Universität Kaiserslautern<br>
                Im Sommersemester 2021<br>
                Betreut von Dr. Matrin Bracke & Prof. Dr. Stefan Ruzika""",unsafe_allow_html=True)
    
        
