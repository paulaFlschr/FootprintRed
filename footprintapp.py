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
    co2_nahrung1 = akt[0]*4.85*53*faktor_nahrung
    co2_nahrung2 = (99.5*0.153+73.6*0.437+159.6*1.795+77.4*0.836+55*0.199+14.5*1.931)*faktor_nahrung
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
        
    co2_essen = [0.153*faktor_nahrung, 0.437*faktor_nahrung, 1.795*faktor_nahrung, 0.836*faktor_nahrung, 0.199*faktor_nahrung, 1.931*faktor_nahrung]
    
    # Generiere Lineares Programm------------------------------------------------
    c = [-pref[0],-pref[1],-pref[2],-pref[3],-pref[4],0,0,0,0,0,0,0]
    
    A_ub = [[co2_akt[0],co2_akt[1],co2_akt[2],co2_akt[3],co2_akt[4],co2_essen[0],co2_essen[1],co2_essen[2],co2_essen[3],co2_essen[4],co2_essen[5],0.429*akt[3]*80],
            [-akt[0],0,0,0,0,0,0,0,0,0,0,0],
            [0,-akt[2],0,0,0,0,0,0,0,0,0,0],
            [0,0,-akt[4],0,0,0,0,0,0,0,0,0],
            [0,0,0,-akt[5],0,0,0,0,0,0,0,0],
            [0,0,0,0,-akt[6],0,0,0,0,0,0,0]]
    b_ub = [max_co2,min_vals[0],min_vals[1],min_vals[2],min_vals[3],min_vals[4]]
    A_eq = [[1,0,0,0,0,akt[0]*53*1860*1/6*1/340,0,0,0,0,0,0],
            [1,0,0,0,0,0,akt[0]*53*1860*1/6*1/660,0,0,0,0,0],
            [1,0,0,0,0,0,0,akt[0]*53*1860*1/6*1/1630,0,0,0,0],
            [1,0,0,0,0,0,0,0,akt[0]*53*1860*1/6*1/3040,0,0,0],
            [1,0,0,0,0,0,0,0,0,akt[0]*53*1860*1/6*1/860,0,0],
            [1,0,0,0,0,0,0,0,0,0,akt[0]*53*1860*1/6*1/1370,0]]
    b_eq = [0.273*365+akt[0]*53*1860*1/6*1/340, 0.202*365+akt[0]*53*1860*1/6*1/660, 0.427*365+akt[0]*53*1860*1/6*1/660, 0.212*365+akt[0]*53*1860*1/6*1/3040, 0.151*365+akt[0]*53*1860*1/6*1/860, 0.04*365+akt[0]*53*1860*1/6*1/1370]
    
    #Löse lineares Programm
    res = sc.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=None, method='simplex')
        
    print(res.x)
    return res.x
       
# 

st.set_page_config(page_title='Fußabdruck', page_icon=None, layout='wide', initial_sidebar_state='expanded')

st.write("""
    # Fußabdruck - Optimierung
    ## Optimiere deinen ökologischen Fußabdruck
""")

# Sidebar sind Abfragen nach aktuellem Zustand
st.sidebar.header('Eingabeparameter zur Berechnung deines aktuellen CO2-Fußabdrucks')

st.sidebar.markdown("***")
st.sidebar.write("""
    ### Kategorie: Ernährung
""")
nahrung1 = st.sidebar.text_input(label='Wie viel Kilogramm Fleisch und Fisch konsumierst du wöchentlich?', value=0)
nahrung2 = st.sidebar.radio('Wie wichtig ist dir, dass die Lebensmittel regional sind?',['sehr wichtig','manchmal wichtig','garnicht wichtig'])
st.sidebar.markdown("***")
st.sidebar.write("""
    ### Kategorie: Wohnen
""")
wohnen1 = st.sidebar.slider(label='Auf wie viel Grad heizt du deine Wohnung normalerweise?', min_value=18,max_value=24,step=1)
wohnen2 = st.sidebar.text_input(label='Wie viel Quadratmeter Wohnfläche hast du zur Verfügung (pro Person)?', value=0)
st.sidebar.markdown("***")
st.sidebar.write("""
    ### Kategorie: Mobilität
""")
mob1 = st.sidebar.text_input(label='Wie viel Kilometer fährst du pro Jahr mit dem Auto (pro Person)?', value=0)
mob2 = st.sidebar.text_input(label='Wie viele Stunden bist du in den letzten vier Jahren geflogen?', value=0)
st.sidebar.markdown("***")
st.sidebar.write("""
    ### Kategorie: Konsum
""")
konsum1 = st.sidebar.text_input(label='Wie viele Kleidungsstücke kaufst du im Jahr?', value=0)

c1,c2,c3 = st.beta_columns((1,5,1))
image1= Image.open('Umweltschutz1.jpg')
c2.image(image1, width=700, clamp=False, channels='RGB', output_format='auto')

# Berechne den aktuellen fußabdruck
akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
akt_abdruck, co2_akt, co2_akt_nach_kat, faktor_nahrung = akt_abdruck(akt)

st.write("""
    ### Zunächst ein paar Informationen zu deinem aktuellen Fußabdruck.
""")
st.write('Dein Fußabdruck beträgt    '+str(round(akt_abdruck))+"""    Kilogramm. Im Vergleich dazu lag der durchschnittliche CO2 Fußabdruck
         in Deutschland im Jahr 2019 bei ca. 7900 Kilogramm. Der weltweite Fußabdruck bemisst sogar nur 4800 Kilogramm.""")


d = {'Durchschnitt Deutschland CO2': [640,2730,3125,507], 'Dein CO2':co2_akt_nach_kat}
#chart_data = pd.DataFrame(data=d, index=['Nahrung', 'Wohnen', 'Mobilität', 'Konsum (Kleidung)'], columns=['Durchschnitt CO2 Deutschland', 'Dein CO2'])
chart_data = pd.DataFrame(data=d, index=['Nahrung', 'Wohnen', 'Mobilität', 'Konsum (Kleidung)'])

st.write(chart_data)
st.bar_chart(chart_data)

# df = pd.DataFrame(
#     [["Nahrung", 640,co2_akt_nach_kat[0]], ["Wohnen", 2730,co2_akt_nach_kat[1]], ["Mobilität", 3125,co2_akt_nach_kat[2]],["Konsum (Kleidung)",507,co2_akt_nach_kat[3]]],
#     columns=["Kategorie","Durschnitt CO2 Deutschland", "Dein CO2"])
# fig = px.bar(df, x="Kategorie", y=["Durschnitt CO2 Deutschland", "Dein CO2"], barmode='group', height=400)
# # st.dataframe(df) # if need to display dataframe
# st.plotly_chart(fig)

st.write("""
    ### Hier kannst du angeben, wie wichtig dir die folgenden Aspekte sind (je höher der Wert desto wichtiger):
""")
remaining_prefs=[1,2,3,4,5,6]
col1, col2, col3, col4 = st.beta_columns(4)
val_nahrung1 = col1.selectbox('Fleisch- und Fischkonsum beibehalten', remaining_prefs)
val_wohnen = col2.selectbox('Wohnbedingungen beibehalten', remaining_prefs)
val_mob1 = col3.selectbox('Autokilometer beibehalten',remaining_prefs)
val_mob2 = col3.selectbox('Flugstunden beibehalten', remaining_prefs)
val_konsum1 = col4.selectbox('Konsum beibehalten', remaining_prefs)

st.write("""
    ### Hier kannst du Minimalwerte für die einzelnen Aspekte setzen:
""")
col1, col2, col3, col4 = st.beta_columns(4)
min_val_nahrung1 = col1.text_input(label= 'Minimaler Fleisch- und Fischkonsum in kg pro Woche',value=0)
min_val_wohnen = col2.text_input(label='Minimale Zimmertemperatur', value=18)
min_val_mob1 = col3.text_input(label='Minimale Autokilometer pro Woche', value=0)
min_val_mob2 = col3.text_input(label='Minimale Flugstunden in 4 Jahren', value=0)
min_val_konsum1 = col4.text_input(label='Minimale Anzahl an neuen Kleidungsstücken im Jahr', value=0)

st.write("""
    Nun kannst du schauen, auf wie viel Prozent du deinen Verbrauch in den genannten Kategorien senken musst, sodass dein CO2 Fußabdruck
    unter der von der Pariser Klimakonferenz geforderten Menge ist. 
    ### Auf welches Jahr soll dein Fußabdruck minimiert werden?
""")

jahr = st.slider(label='Jahr', min_value=2021,max_value=2050,step=1)



# Arrays in denen die Benutzereingaben gespeichert werden
akt = [float(nahrung1),nahrung2,wohnen1,float(wohnen2),float(mob1),float(mob2),float(konsum1)]
pref = [float(val_nahrung1),float(val_wohnen),float(val_mob1),float(val_mob2),float(val_konsum1)]
min_vals = [float(min_val_nahrung1),float(min_val_wohnen), float(min_val_mob1), float(min_val_mob2), float(min_val_konsum1)]


solution = optimize(akt, pref, min_vals, jahr, co2_akt, faktor_nahrung)
print(solution)



st.write('Reduziere deinen ökologischen Fußabdruck, indem du deinen Verbrauch auf die folgenden Prozente reduzierst:', solution, round(akt_abdruck))
st.write('Reduziere deinen Fleischkonsum auf    '+str(round(solution[0],4)*100)+'%.')
st.write('Reduziere deinen Zimmerwärme auf    '+str(round(solution[1],4)*100)+'%.')
st.write('Reduziere deine Autokilometer auf    '+str(round(solution[2],4)*100)+'%.')
st.write('Reduziere deine Flugstunden auf    '+str(round(solution[3],4)*100)+'%.')
st.write('Reduziere deinen gekauften Kleidungsstücke auf    '+str(round(solution[4],4)*100)+'%.')




