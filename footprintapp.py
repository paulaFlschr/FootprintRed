# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 17:18:44 2021

@author: Paula
"""

import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import plotly.express as px
import scipy.optimize as sc

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
    co2_wohnen_strom = 0.429*akt[3]*80
    co2_wohnen_temp = 0.27* akt[3] *80*faktor_temp
    co2_wohnen = co2_wohnen_strom + co2_wohnen_temp
    co2_mob1 = 0.2045*akt[4]
    co2_mob2 = (akt[5]*1049.8*0.197)/4
    co2_konsum1 = 8.45 * akt[6]
    co2_akt_nach_kat = [co2_nahrung1 + co2_nahrung2, co2_wohnen_strom + co2_wohnen_temp, co2_mob1 + co2_mob2, co2_konsum1]
    co2_akt = [co2_nahrung1, co2_wohnen_temp, co2_mob1, co2_mob2, co2_konsum1]
    akt_abdruck = sum(co2_akt_nach_kat)
    
    return akt_abdruck, co2_akt, co2_akt_nach_kat, faktor_nahrung


def optimize(akt, pref, min_vals, jahr, co2_akt, faktor_nahrung):
    #akt = [1.1, 'machmal wichtig', 21, 50, 100, 12,60]
    #pref=[1,10,10,10,10]
    #min_vals = [0,21,100,12,60]
    
    
    # zu erreichender fußabdruck ----------------------------------------------------
    if jahr<2030:
        max_co2 =  -185*(jahr-2020)+7440
    elif jahr<2040:
        max_co2 =  -176*(jahr-2030)+5509
    else:
        max_co2 =  -184*(jahr-2040)+3830
        
    co2_essen = [0.36*faktor_nahrung, 0.437*faktor_nahrung, 7.34*faktor_nahrung, 0.82*faktor_nahrung, 3.23*faktor_nahrung, 1.931*faktor_nahrung]
    #prefunterschied
    max_prefdiff = 0
    for i in range(4):
        for j in range(4-i):
            if max_prefdiff < abs(pref[i]-pref[i+1+j]):
                max_pref_diff = abs(pref[i]-pref[i+1+j])
        
    # Generiere Lineares Programm------------------------------------------------
# =============================================================================
#     c = [-pref[0],-pref[1],-pref[2],-pref[3],-pref[4],0,0,0,0,0,0,0]
#     
#     A_ub = [[co2_akt[0],co2_akt[1],co2_akt[2],co2_akt[3],co2_akt[4],co2_essen[0],co2_essen[1],co2_essen[2],co2_essen[3],co2_essen[4],co2_essen[5],0.429*akt[3]*80],
#             [-akt[0],0,0,0,0,0,0,0,0,0,0,0],
#             [0,-akt[2],0,0,0,0,0,0,0,0,0,0],
#             [0,0,-akt[4],0,0,0,0,0,0,0,0,0],
#             [0,0,0,-akt[5],0,0,0,0,0,0,0,0],
#             [0,0,0,0,-akt[6],0,0,0,0,0,0,0]]
#     b_ub = [max_co2,-min_vals[0],-min_vals[1],-min_vals[2],-min_vals[3],-min_vals[4]]
#     A_eq = [[-akt[0]*53*1860*1/6*1/340,0,0,0,0,1,0,0,0,0,0,0],
#             [-akt[0]*53*1860*1/6*1/660,0,0,0,0,0,1,0,0,0,0,0],
#             [-akt[0]*53*1860*1/6*1/1630,0,0,0,0,0,0,1,0,0,0,0],
#             [-akt[0]*53*1860*1/6*1/3040,0,0,0,0,0,0,0,1,0,0,0],
#             [-akt[0]*53*1860*1/6*1/860,0,0,0,0,0,0,0,0,1,0,0],
#             [-akt[0]*53*1860*1/6*1/1370,0,0,0,0,0,0,0,0,0,1,0]]
#     b_eq = [0.273*365+akt[0]*53*1860*1/6*1/340, 0.202*365+akt[0]*53*1860*1/6*1/660, 0.427*365+akt[0]*53*1860*1/6*1/660, 0.212*365+akt[0]*53*1860*1/6*1/3040, 0.151*365+akt[0]*53*1860*1/6*1/860, 0.04*365+akt[0]*53*1860*1/6*1/1370]
#     
# =============================================================================
    c = [-pow(pref[0],2),-pow(pref[1],2),-pow(pref[2],2),-pow(pref[3],2),-pow(pref[4],2),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    A_ub = [[co2_akt[0],co2_akt[1],co2_akt[2],co2_akt[3],co2_akt[4],co2_essen[0],co2_essen[1],co2_essen[2],co2_essen[3],co2_essen[4],co2_essen[5],0.429*akt[3]*80,0,0,0,0,0,0,0,0,0,0],
            [-akt[0],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,-akt[2],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
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
            [-1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
            [-1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
            [-1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
            [-1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
            [0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
            [0,-1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
            [0,-1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
            [0,0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
            [0,0,-1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
            [0,0,0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]]
    b_ub = [max_co2,-min_vals[0],-min_vals[1],-min_vals[2],-min_vals[3],-min_vals[4],max_prefdiff^2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    A_eq = [[-akt[0]*53*1860*1/6*1/340,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/660,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/1630,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/3040,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/860,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/1370,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0]]
    b_eq = [0.273*365+akt[0]*53*1860*1/6*1/340, 0.202*365+akt[0]*53*1860*1/6*1/660, 0.427*365+akt[0]*53*1860*1/6*1/660, 0.212*365+akt[0]*53*1860*1/6*1/3040, 0.151*365+akt[0]*53*1860*1/6*1/860, 0.04*365+akt[0]*53*1860*1/6*1/1370]
    
    #Löse lineares Programm
    res = sc.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=[(0,1),(0,1),(0,1),(0,1),(0,1),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)], method='simplex')
       
    return res.x
       
# 
# Titellines -----------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Fußabdruck der Zukunft', page_icon=None, layout='wide', initial_sidebar_state='collapsed')
#st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
c1,c2 = st.beta_columns((7,2))
c1.write("""
        # Fußabdruck der Zukunft
        ## Optimiere deinen ökologischen Fußabdruck
    """)
navigation = c2.selectbox('', ["Startseite","Rechner: Fußabdruck-Optimierung", "Hintergrund: Fußabdruckberechnung", "Hintergrund: Budgetberechnung", "Hintergrund: Fußabdruck-Optimierung","Hintergrund: Datenvalidierung", "Rechner: Gesellschaftlicher Einfluss","Quellen & Impressum"])
st.markdown("***")
hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
st.markdown(hide_footer_style, unsafe_allow_html=True)

#==============================================================================================================================
# Motivation --------------------------------------------------------------------------------------------------------------------
if navigation == 'Startseite':
    c1,c2,c3 = st.beta_columns([1,6,1])
    c2.markdown('<div style="text-align: center"><em> <font size = 6><b> Sei du selbst die Veränderung, die du dir wünschst für diese Welt! </b></font> - Mahatma Gandhi</em></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.beta_columns([2.5,6,2.5])
    imagestart= Image.open('Startseite.png')
    c2.image(imagestart,use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    st.markdown("""<font size = 5>
                Willkommen bei „Fußabdruck der Zukunft“. Hier kannst du deinen persönlichen
                CO2-Fußabdruck berechnen. Außerdem findest du hier Infos rund um das Thema 
                CO2-Verbrauch und wir erklären dir, wie unser Rechner funktioniert. Schau dir
                zum Einstieg gerne das Video „Klimaschutz im Alltag – Welchen Einfluss haben 
                wir?“ an.</font><br><br>
                """, unsafe_allow_html=True)
    c1, c2 = st.beta_columns(2)
    c1.video(data='https://www.youtube.com/watch?v=0msDfGBiAmQ&ab_channel=Helmholtz-Klima-Initiative', format='video/mp4', start_time=0)
    c2.video(data='https://www.youtube.com/watch?v=CR3q9vnSlFQ&ab_channel=StadtwerkeT%C3%BCbingen', format='video/mp4', start_time=0)
    st.markdown("""<br>
                Im November 2016 beschloss das Bundeskabinett den Klimaschutzplan 2050. Darin
                sind die Klimaschutzziele der Bundesrepublik Deutschland festgelegt, die im
                Einklang mit dem Pariser Übereinkommen stehen. So sollen die 
                Treibhausgasemissionen bis 2050 um 80 bis 95 Prozent reduziert werden im 
                Vergleich zum Wert von 1990. Die Einhaltung dieses Ziels stellt nicht nur die
                Politik und große Unternehmen vor eine große Herausforderung, sondern wird auch 
                großen Einfluss auf die Bevölkerung haben. Jeder Einzelne wird sich auf 
                Einschränkungen einlassen müssen und einen Beitrag zum Klimaschutz 
                leisten müssen. <center><b> Doch wie könnten diese Einschränkungen für die Bevölkerung 
                von Deutschland aussehen? </b></center> Unsere Modellierung basiert auf dem 
                bekannten Konzept eines CO2-Fußabdruck-Rechners. Allerdings soll darüber hinaus auf der Grundlage des persönlichen jährlichen CO2-Verbrauchs eine Empfehlung gegeben werden, wie das Verhalten verändert werden könnte, um das CO2-Ziel einzuhalten. 
                """, unsafe_allow_html=True)

elif navigation == 'Hintergrund: Fußabdruck-Optimierung':
    st.write("""Ziel unserer Optimierung ist es, dem Benutzer individuelle Handlungsempfehlungen 
                über die Verringerung seines $CO_{2}$-Ausstoßes zu geben. Diese Empfehlungen 
                sollen von den Präferenzen des Nutzers abhängig sein.
                """)
    st.markdown("""
                Unser Modell deckt fünf Bereiche ab, für welche Empfehlungen gegeben werden:<br>
                <ol><li>Fleischkonsum</li><li>Heizen</li><li>Autokilometer</li><li>Flugstunden</li><li>Kleiderkonsum</li></ol><br>
                Dazu erhalten wir als Eingabedaten verschiedene Informationen, 
                die in vier Bereiche unterteilt werden können:<br>
                <ol><li>aktuelle Nutzdaten</li><li>Präferenzen</li><li>Minimalwerte</li><li>Optimierungsjahr</li></ol><br>
                Aus diesen Daten erstellen wir ein Optimierungsmodell.<br>""",unsafe_allow_html=True)
    st.write("""Schritt 1: Eingabedaten verarbeiten<br>
                Aktuelle Nutzdaten: Für unser Modell benötigen wir die $CO_{2}$-Emissionen, 
                die durch die einzelnen Handlungen erzeugt werden. Aus diesen berechnen wir 
                die aktuellen $CO_{2}$-Emissionen der einzelnen Komponenten. Wie wir das berechnen
                und welche Daten wir nutzen findest du in Abschnitt 'Hintergrund: 
                Fußabdruckberechnung'.""")
    st.write("""Als Ergebnis erhalten wir die Werte co2akt$_{i}$ mit $i \in$ I = 
                \{Fleisch, Heizen, Auto, Flugzeug, Kleidung\}, sowie co2ess$_{j}$ mit 
                $j \in$ J = \{Gemüse, Obst, Milchprodukte, Brot, Kartoffeln, Eier\} und 
                co2strom.""")
    st.write("""Optimierungsjahr: Anhand des Optimierungsjahres berechnen wir den maximal 
                möglichen $CO_{2}$-Ausstoß des Nutzers, d.h. sein $CO_{2}$-Budget. Wie wir das 
                berechnen und welche Daten wir nutzen findest du in Abschnitt 'Hintergrund: 
                    Budgetberechnung'.""")
    st.write("""Als Ergebnis erhalten wir den Wert maxco2.
                Schritt 2: Variablen einführen<br>
                Die Handlungsempfehlungen für den Nutzer werden zunächst als Prozentsätze 
                berechnet. Diese geben an, auf wie viel Prozent der Nutzer seinen Verbrauch 
                im Vergleich zum vorherigen Verbrauch reduzieren muss, um das $CO_{2}$-Budget 
                einzuhalten. Dazu führen wir die folgenden Variablen ein:
                var$$_{i}$$ mit $$i \in I$$ = \{Fleisch, Heizen, Auto, Flugzeug, Kleidung\}""")
           
                
      
elif navigation == "Rechner: Fußabdruck-Optimierung":
    st.write("""
             Hier kannst du deinen aktuellen CO2-Fußabdruck berechnen. Um dem Klimawandel 
             entgegenzuwirken, muss aber in der Zukunft der CO2-Ausstoß sinken. Was das für 
             deinen CO2-Fußabdruck heißt, wollen wir dir hier zeigen. Befolge dazu unsere 
             Schritt-für-Schritt-Anleitung. Und los geht’s!
             """)
    c1,c2,c3 = st.beta_columns((1,5,1))
    image1= Image.open('Umweltschutz1.jpg')
    c2.image(image1, width=700, use_column_width=True, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("""<font size="5"><b>Schritt 1: Ermittlung deines aktuellen Fußabdrucks</b> </font><br>
                     Fülle alle Fragen im unten stehenden Formular aus.<br> 
                     Beachte, dass du alle Angaben für den genannten Zeitraum mitteln solltest. Isst
                     du also in einer Woche 2 Kilogramm Fleisch und Fisch und in der darauf folgenden
                     kein Fleisch so setze den Wert auf 1. Denke außerdem daran, dass auch Unterwäsche
                     und Schuhe Kleidungsstücke sind. Damit dir die Einschätzung etwas einfacher fällt, sind als Platzhalter die
                     Werte einer durchschnittlichen Person in Deutschland angegeben.  
            """,unsafe_allow_html=True)
    
   
    col1, col2, col3, col4 = st.beta_columns(4)
    col1.markdown("### Kategorie: Ernährung",unsafe_allow_html=True)
    nahrung1 = col1.text_input(label='Wie viel Kilogramm Fleisch und Fisch konsumierst du wöchentlich?', value=1.1)
    nahrung2 = col1.radio('Wie wichtig ist dir, dass die Lebensmittel regional sind?',['sehr wichtig','manchmal wichtig','garnicht wichtig'], index=1)
    col2.markdown("### Kategorie: Wohnen",unsafe_allow_html=True)
    wohnen1 = col2.slider(label='Auf wie viel Grad heizt du deine Wohnung normalerweise?', min_value=18,max_value=24,step=1, value=21)
    wohnen2 = col2.text_input(label='Wie viel Quadratmeter Wohnfläche hast du zur Verfügung (pro Person)?', value=47)
    col3.markdown("### Kategorie: Mobilität",unsafe_allow_html=True)
    mob1 = col3.text_input(label='Wie viel Kilometer fährst du pro Jahr mit dem Auto (pro Person)?', value=11888)
    mob2 = col3.text_input(label='Wie viele Stunden bist du in den letzten vier Jahren geflogen?', value=12)
    col4.markdown("### Kategorie: Konsum (Kleidung)",unsafe_allow_html=True)
    konsum1 = col4.text_input(label='Wie viele Kleidungsstücke kaufst du im Jahr?', value=60)
    col4.markdown('<br><br><br><br><br>',unsafe_allow_html=True)
    
     # Berechne den aktuellen fußabdruck
    akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
    akt_abdruck, co2_akt, co2_akt_nach_kat, faktor_nahrung = akt_abdruck(akt)
        
    checkbox1 = st.checkbox(label="Schritt 1 abschließen: Fußabdruck berechnen")
    if checkbox1:
        col1,col2,col3 = st.beta_columns((0.7,1.3,2))
        imagefuss = Image.open('Fuss.PNG')
        col1.image(imagefuss, width=700, use_column_width=True, clamp=False, channels='RGB', output_format='auto')
        col2.markdown("""<br>
                <center><font size="4"><b>Dein aktueller Fußabdruck beträgt """+ str(round(akt_abdruck))+""" Kilogramm.</b></font></center><br>
                Zum Vergleich: Der durchnittliche CO2 Fußabdruck in Deutschland im Jahr 2019 lag bei ca 7900 Kilogramm.
                Der durchschnittliche weltweite CO2 Fußabdruck liegt bei 4800 Kilogramm.<br>
                In dem neben stehenden Diagramm findest du den Vergleich zum durchnittlichen Fußabdruck eines 
                Menschen in Deutschlands zu deinem Fußabdruck, aufgeschlüsselt in die vier Kategorien.
                """,unsafe_allow_html=True)
            
        df = pd.DataFrame(
            [["Nahrung", 1704,co2_akt_nach_kat[0]], ["Wohnen", 2730,co2_akt_nach_kat[1]], ["Mobilität", 3051,co2_akt_nach_kat[2]],["Konsum (Kleidung)",507,co2_akt_nach_kat[3]]],
            columns=["Kategorie","Durschnitt CO2 Deutschland", "Dein CO2"])
        fig = px.bar(df, x="Kategorie", y=["Durschnitt CO2 Deutschland", "Dein CO2"], barmode='group', height=400)
        col3.plotly_chart(fig)
        
        st.markdown("***")
    
        st.markdown("""
                 <font size="5"><b>Schritt 2: Optimierung-Gib Minimalwerte an</b> </font><br>
                          <br> Wir wollen nun deinen Fußabdruck verkleinern, d.h.
                           deinen $CO_{2}$-Ausstoß reduzieren. Das wird zu Veränderungen
                           in einzelnen Kategorien führen. Hier hast du die Möglichkeit
                          Minimalwerte für einzelne Aspekte zu setzen. Möchtest du zum Beispiel deine Zimmertemperatur nicht auf unter 20 Grad Celsius herabsetzen, dann
                          gib in das Eingabefeld eine 20 ein.
                """,unsafe_allow_html=True)
                
        
        col1, col2, col3, col4 = st.beta_columns(4)
        min_val_nahrung1 = col1.text_input(label= 'Minimaler Fleisch- und Fischkonsum in kg pro Woche',value=0)
        min_val_wohnen = col2.text_input(label='Minimale Zimmertemperatur', value=18)
        min_val_mob1 = col3.text_input(label='Minimale Autokilometer pro Jahr', value=0)
        min_val_mob2 = col3.text_input(label='Minimale Flugstunden in 4 Jahren', value=0)
        min_val_konsum1 = col4.text_input(label='Minimale Anzahl an neuen Kleidungsstücken im Jahr', value=0)
        
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
            val_nahrung1 = col1.selectbox('Fleisch- und Fischkonsum beibehalten', remaining_prefs)
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
                                  Jahr 2030, so wird dein CO2-Fußabdruck so weit heruntergesetzt,
                                  dass du unter dem Pro-Kopf-CO2-Budget von 2030 liegst.
                                  """,unsafe_allow_html=True)
                
                jahr = st.slider(label='Jahr', min_value=2021,max_value=2050,step=1)
                
                checkbox4 = st.checkbox(label="Schritt 4 abschließen: Jahr anwenden")
                if checkbox4:
                
                    # Arrays in denen die Benutzereingaben gespeichert werden
                    akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
                    pref = [float(val_nahrung1),float(val_wohnen),float(val_mob1),float(val_mob2),float(val_konsum1)]
                    min_vals = [float(min_val_nahrung1),float(min_val_wohnen), float(min_val_mob1), float(min_val_mob2), float(min_val_konsum1)]
                    
                    
                    solution = optimize(akt, pref, min_vals, jahr, co2_akt, faktor_nahrung)
                    st.write(solution)
                
                    st.markdown("***")
                    st.markdown("""
                            <font size="5"><b>Dein Ergebnis</b> </font><br>
                            """,unsafe_allow_html=True)
                
                    if round(solution[0])==1 and round(solution[1])==1 and round(solution[2])==1 and round(solution[3])==1 and round(solution[4])==1:
                        st.markdown("""
                            <b>Super! Dein aktueller Fußabdruck liegt bereits unter der geforderten CO2-Grenze. 
                            Das heißt natürlich nicht, dass du garnichts mehr tun kannst und sollst.</b>
                            """,unsafe_allow_html=True)
                    if round(solution[0],4)<1:
                        reduktion0 = round((1 - solution[0])*100,2)
                        c1,c2 = st.beta_columns((1,3))
                        image_fleisch= Image.open('Red_Fleisch.JPG')
                        c1.image(image_fleisch, width=100, clamp=False, channels='RGB', output_format='auto')
                        c2.markdown("""
                            <b>Reduziere deinen Fleisch- und Fischkonsum um """+str(reduktion0)+""" %. </b><br>
                            Suche doch mal im Internet nach vegetarischen Rezepten. Dort gibt es eine rießige Auswahl, da ist
                            sicher etwas dabei was dir schmecken könnte ;)
                            """,unsafe_allow_html=True)
                    if round(solution[1],4)<1:
                        reduktion1 = round((1 - solution[1])*100,2)
                        c1,c2 = st.beta_columns((3,1))
                        image_heizen= Image.open('Red_Heizen.JPG')
                        c2.image(image_heizen, width=100, clamp=False, channels='RGB', output_format='auto')
                        c1.markdown("""
                            <b>Reduziere deine Zimmerwärme um """+str(reduktion1)+""" %.</b> <br>
                            Mit ein paar dicken Socken, einem dicken Pulli und einem leckerer Tee eingekuschtel in eine
                            flauschige Decke. Klimaschutz muss nicht immer ungemütlich sein.
                            """,unsafe_allow_html=True)
                    if round(solution[2],4)<1:
                        reduktion2 = round((1 - solution[2])*100,2)
                        st.markdown("""
                            <b>Reduziere deine Autokilometer um """+str(reduktion2)+""" %. </b><br>
                            Kurze Strecken kannst du mit dem Fahrrad fahren oder zu Fuß gehen. Das hält gleichzeitig noch
                            fit und gesund. Nimm doch für längere Strecken einfach mal den Bus oder die Bahn. Das kann
                            manchmal auch viel entspannter sein.
                            """,unsafe_allow_html=True)
                    if round(solution[3],4)<1:
                        reduktion3 = round((1 - solution[3])*100,2)
                        c1,c2 = st.beta_columns((1,3))
                        image_flieg= Image.open('Red_Fliegen.JPG')
                        c1.image(image_flieg, width=100, clamp=False, channels='RGB', output_format='auto')
                        c2.markdown("""
                            <b>Reduziere deine Flugstunden um """+str(reduktion3)+""" %. </b><br>
                            Fliegen ist besonders klimaschädlich. Natürlich heißt das nicht, dass du garnicht mehr weiter
                            weg kannst. Aber überlege doch mal ob es vielleicht Alternativen gibt. Urlaubsziele lassen sich
                            zum Beispiel auch in Deutschland viele schöne finden.
                            """,unsafe_allow_html=True)
                    if round(solution[4],4)<1:
                        reduktion4 = round((1 - solution[4])*100,2)
                        st.markdown("""
                            <b>Reduziere deinen Konsum um """+str(reduktion4)+""" %.</b> <br>
                            Weniger Kleidungsstücke und dafür hochwertige sind deutlich besser für das Klima. Seien wir mal
                            ehrlich, viele Sachen die wir einmal kaufen ziehen wir am Ende viel zu selten an...
                            """,unsafe_allow_html=True)
    
    
# Pro Kopf Budget ---------------------------------------------------------------------------------------------------------
elif navigation == 'Hintergrund: Fußabdruckberechnung':
    st.write("""
             ## Berechnung des persönlichen $CO_{2}$-Verbrauchs
             Zur Ermittlung des individuellen $CO_{2}$-Verbrauchs wird der persönliche Gesamtverbrauch in verschiedene Bereiche unterteilt.
             Unser Ziel ist es, die Eingabe für den Benutzer möglichst einfach zu gestalten. Deshalb ist es in einigen Bereichen notwendig Verallgemeinerungen zu treffen.
             Zur Berechnung des persönlichen $CO_{2}$-Verbrauchs pro Jahr sollen folgende Bereiche berücksichtig werden:""")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Nahrung</li><li>Wohnen</li><li>Mobilität</li><li>Konsum(Kleidung)</li>', unsafe_allow_html=True)
    st.write("""Auf der Grundlage des persönlichen Verhaltens wird der individuelle $CO_{2}$-Verbrauch berechnet.  
             """)
    st.markdown("***")
    st.write("""
             ## Nahrung
             Die Datengrundlage für die Berechnung des persönlichen $CO_{2}$-Verbrauchs durch die Nahrung bildet die folgende Tabelle.
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image3= Image.open('Tab3_Nahrungswerte.PNG')
    c2.image(image3, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zur Berechnung des persönlichen $CO_{2}$-Verbrauchs durch die Nahrung werden vom Benutzer folgende Aspekte selbst angegeben:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Verzehrmenge Fleisch pro Woche in kg</li><li>Regionale Lebensmittel</li>', unsafe_allow_html=True)
    st.write("""Die Berechnung des $CO_{2}$-Verbrauchs durch die Nahrung werden die durchschnittlichen jährlichen Verzehrmengen mit den entsprechenden $CO_{2}$-Werten multipliziert und über alle Lebensmittelgruppen aufaddiert, wobei die Verzehrmenge Fleisch vom Benutzer angegeben wird. Entsprechend muss bei der Berechnung diese wöchentliche Angabe durch Multiplikation mit dem Faktor 53 (Anzahl der Wochen pro Jahr) berücksichtigt werden. Damit der Aspekt „2. Regionale und saisonale Lebensmittel“ in die Berechnung einfließen kann, werden gemäß [4] die entsprechenden Faktoren aus Tabelle 4 einbezogen. 
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image4= Image.open('Tab4_regio.PNG')
    c2.image(image4, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("""
             Zunächst wird so der $CO_{2}$-Wert durch die Nahrung berechnet gemäß dem folgenden Zusammenhang.
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image5= Image.open('Formel_Essen.PNG')
    c2.image(image5, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("""
             Es soll nicht nur der persönliche $CO_{2}$-Verbrauch berechnet werden, sondern darüber hinaus soll dem Benutzer vorgeschlagen werden, wie er sein Verhalten verändern kann, um zu einem bestimmten Zeitpunkt unter dem pro Kopf $CO_{2}$-Budget zu bleiben. In Bezug auf die Nahrung soll dabei, falls nötig und erwünscht die Verzehrmenge Fleisch reduziert werden, da ihr gemäß Tabelle 3 ein hoher $CO_{2}$-Wert zugeordnet wird. Dabei soll eine Reduzierung der Fleischmenge nicht dazu führen, dass der Benutzer insgesamt weniger isst. Aus diesem Grund wird die reduzierte Menge auf die andren Lebensmittelgruppe verteilt. Um eine möglichst realistische Einschätzung hierzu zu geben, wird der tägliche Kalorien bedarf ausgehend von der angegebenen Verzehrmenge Fleisch und den durchschnittlichen Verzehrmengen der übrigen Lebensmittelgruppen berechnet. Zu der vorgeschlagenen Reduzierung der Verzehrmenge Fleisch wird die entsprechende Kalorienangabe ermittelt und auf die anderen Lebensmittelgruppen verteilt. Grundlage für diese Berechnungen bilden die folgenden Zusammenhänge. 
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image6= Image.open('Formel_Fleischersatz.PNG')
    c2.image(image6, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Wohnen")
    st.write("Die Datengrundlage für die Berechnung des persönlichen $CO_{2}$-Verbrauchs durch den Aspekt Wohnen bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image7= Image.open('Tab5_Wohnen.PNG')
    c2.image(image7, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Der berechnete Wert des persönlichen $CO_{2}$-Verbrauchs durch den Aspekt Wohnen soll personalisiert werden, indem der Benutzer folgende Angaben macht:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Wohnfläche pro Person</li><li>Eingestellte Raumtemperatur</li>', unsafe_allow_html=True)
    st.write("""Mit diesen beiden Größen wird der $CO_{2}$-Verbrauch des Benutzers für den Aspekt Wohnen durch die folgende Beziehung berechnet.""")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image8= Image.open('Formel_Wohnen.PNG')
    c2.image(image8, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Mobilität")
    st.write("Die Datengrundlage für die Berechnung des persönlichen $CO_{2}$-Verbrauchs durch den Aspekt Mobilität bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image9= Image.open('Tab6_Mobilität.PNG')
    c2.image(image9, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("""Außerdem wird der $CO_{2}$-Wert in kg$CO_{2}$ pro km für Flugzeuge gemäß [4] mit 0,197 angenommen. 
             Zur Berechnung des persönlichen $CO_{2}$-Verbrauchs unter dem Aspekt Mobilität sollen folgende Angaben des Benutzers berücksichtigt werden:
             """)
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Gefahrene Autokilometer pro Jahr pro Person</li><li>Flugstunden der letzten vier Jahre</li>', unsafe_allow_html=True)
    st.write("Unter Berücksichtigung dieser Angaben wird der $CO_{2}$-Wert gemäß dem folgenden Zusammenhang berechnet. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image20= Image.open('Formel_Mobilität.PNG')
    c2.image(image20, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Konsum")
    st.write("Die Datengrundlage für die Berechnung des persönlichen $CO_{2}$-Verbrauchs durch den Konsum bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image10= Image.open('Tab7_Konsum.PNG')
    c2.image(image10, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Der Benutzer soll dabei folgende Angabe zu seinem Konsumverhalten machen:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.markdown('<ol> <li>Anzahl gekaufte Kleidungsstücke pro Jahr</li>', unsafe_allow_html=True)
    st.write("Unter Berücksichtigung dieser Angabe wird der persönliche $CO_{2}$-Verbrauch durch den Aspekt Konsum durch den folgenden Zusammenhang berechnet.")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image11= Image.open('Formel_Konsum.PNG')
    c2.image(image11, width=700, clamp=False, channels='RGB', output_format='auto')
    
    
elif navigation == "Hintergrund: Budgetberechnung":
    st.write("""
             ## Berechnung des pro Kopf Budgets (Deutschland)
             Zunächst soll der Anteil der Bevölkerung am $CO_{2}$-Gesamtverbrauch von Deutschland bestimmt werden. Dieser ermöglicht es uns im weiteren Verlauf ausgehend von künftigen Klimazielen des Landes das persönliche $CO_{2}$-Budget pro Kopf zu berechnen und Handlungsempfehlungen zur Reduzierung des persönlichen $CO_{2}$-Verbrauchs auszusprechen. 
            Die folgende Tabelle bildet die Grundlage der Berechnung des Anteils der Bevölkerung am $CO_{2}$-Gesamtverbrauch von Deutschland.
            """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image12= Image.open('Tab1_Einwohnerzahlen.PNG')
    c2.image(image12, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zunächst kann nun der gesamte durch die Bevölkerung verursachte $CO_{2}$-Verbrauch $A_{Bev}$ für die entsprechenden Jahre aus Tab. 1 berechnet werden. ")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image13= Image.open('Formel_Bev1.PNG')
    c2.image(image13, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("Somit kann der prozentuale Anteil der durch die Bevölkerung verursachten Emissionen $P_{Bev}$ an den bundesweiten Emissionen bestimmt werden.")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image14= Image.open('Formel_Bev2.PNG')
    c2.image(image14, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("Die gemäß dieser Formeln berechneten Werte sind nachfolgend dargelegt. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image15= Image.open('Tab2_Einwohner.PNG')
    c2.image(image15, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zuletzt wird der Mittelwert $\overline{P_{Bev}}$ gebildet über alle so bestimmten Anteile des $CO_{2}$-Verbrauchs der Bevölkerung. ")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image16= Image.open('Wert_Bev.PNG')
    c2.image(image16, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("""Dieser Wert sagt aus, dass der durch die Bevölkerung verursachte $CO_{2}$-Verbrauch ungefähr 83% ausmacht. 
             Er erlaubt es uns, für künftige bundesweite $CO_{2}$-Budgets ein pro Kopf Budget vorherzusagen. """)
    st.markdown("***")
    st.write("""
             ## Künftige $CO_{2}$-Budgets
             Damit künftige pro Kopf $CO_{2}$-Budgets berechnet werden können, soll hier das zu Grunde liegende Modell vorgestellt werden. Die Daten basieren auf dem Klimaschutzplan 2050, der vom Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit (BMU) veröffentlicht wurde [2]. Demnach sollen ausgehend vom Jahr 1990 bis 2030 die CO2-Emissionen mindestens um 55%, bis 2040 um 70% und bis 2050 um 80%-95% gesenkt werden. Die sich aus diesen Zielen ergebenden $CO_{2}$-Budgets sind in Abbildung 1 dargestellt.  
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image17= Image.open('Emissionsziel.PNG')
    c2.image(image17, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Mit dieser Datengrundlage und dem zuvor ermittelten Anteil des $CO_{2}$-Verbrauches der Bevölkerung kann der pro Kopf Ausstoß für künftige Szenarien ermittelt werden. ")
    

elif navigation == "Hintergrund: Datenvalidierung":
    st.write("""Nach dem Aufstellen des Modells ist es notwendig, die mit unserer Modellierung berechneten CO2-Verbrauchswerte auf ihre Sinnhaftigkeit zu überprüfen. 
             Die $CO_{2}$-Werte, die das Modell in den einzelnen Kategorien berechnet, sollen mit dem CO2-Rechner des Umweltbundesamtes [6] verglichen werden. 
             Außerdem soll die mit dem Modell berechnete gesamte CO2-Verbrauch überprüft werden. Hierzu wird der pro Kopf Verbrauch aus dem Jahr 2019 [1.1] mit den entsprechenden Durchschnittswerten aus diesem Jahr simuliert.
             """)
    st.write("""
             Tabelle 9 vergleicht die laut „Fußabdruck der Zukunft“ berechneten $CO_{2}$-Werte
             der jeweiligen verwendeten Kategorien mit den entsprechenden Werten des „$CO_{2}$-Rechners 
             des Umweltbundesamtes“ [6]. Die Grundlage für die berechneten $CO_{2}$-Werte bilden 
             die Durchschnittswerte aus Tabelle 8. Man kann aus den Werten in Tabelle 9 ablesen, 
             dass für die Kategorien Nahrung und Mobilität die Werte der beiden Rechner sehr gut
             übereinstimmen. Eine etwas größere Abweichung zeigt sich im Bereich Wohnen.
             Auffällig sind die großen Unterschiede der $CO_{2}$-Werte in der Kategorie Konsum, 
             die auch zu einer großen Abweichung bei den Gesamtwerten führen. Der Wert des 
             „$CO_{2}$-Rechners des Umweltbundesamtes“ ist sehr viel größer, da bei der Berechnung
             laut „Fußabdruck der Zukunft“ nur die gekauften Kleidungsstücke berücksichtigt
             werden. In diesem Bereich fließen also beim „$CO_{2}$-Rechner des Umweltbundesamtes“ 
             weitere Aspekte mit ein, die den größeren $CO_{2}$-Wert erklären.   

             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab8= Image.open('Tab8.PNG')
    c2.image(image_tab8, use_column_width=True,width=700, clamp=False, channels='RGB', output_format='auto')
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab9= Image.open('Tab9.PNG')
    c2.image(image_tab9,use_column_width=True, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.write("""
             Tabelle 10 vergleicht die Werte laut „Fußabdruck der Zukunft“ berechneten $CO_{2}$-Gesamtwerte mit dem pro Kopf $CO_{2}$-Verbrauch aus dem Jahr 2019 laut „Statistica“. Auch bilden die Werte aus Tabelle 8 die Grundlage der Berechnung laut „Fußabdruck der Zukunft“. Die beiden Gesamtwerte stimmen fast überein. Das zeigt, dass der $CO_{2}$-Wert aus dem Jahr 2019 sehr gut mit dem Rechner reproduziert werden konnte. 
             Die Abweichungen zu anderen Rechnern können damit erklärt werden, dass „Fußabdruck der Zukunft“ keine öffentlichen Emissionen einbezieht. Außerdem werden oft im Bereich Konsum noch weitere Aspekte abgefragt und berücksichtigt.  
             Insgesamt hat die Validierung gezeigt, dass die durch „Fußabdruck der Zukunft“ berechneten $CO_{2}$-Werte zu den Werten aus anderen Rechnern passen. Der Gesamtwert kann frühere $CO_{2}$-Werte sehr gut nachbilden. Somit kann angenommen werden, dass er für die Zukunft gute Vorhersagen treffen wird. 

             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image_tab10= Image.open('Tab10.PNG')
    c2.image(image_tab10, use_column_width=True,width=700, clamp=False, channels='RGB', output_format='auto')
    
    
else:
    
    #link = '[GitHub](http://github.com)'
    #st.markdown(link, unsafe_allow_html=True)
    st.markdown("<font size = 4> Quellen </font>",unsafe_allow_html=True)
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
                """, unsafe_allow_html=True)
    st.write("von Lena Bill & Paula Fleischer")
    
    
        
