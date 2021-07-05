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
    
    # Generiere Lineares Programm------------------------------------------------
    c = [-pref[0],-pref[1],-pref[2],-pref[3],-pref[4],0,0,0,0,0,0,0]
    
    A_ub = [[co2_akt[0],co2_akt[1],co2_akt[2],co2_akt[3],co2_akt[4],co2_essen[0],co2_essen[1],co2_essen[2],co2_essen[3],co2_essen[4],co2_essen[5],0.429*akt[3]*80],
            [-akt[0],0,0,0,0,0,0,0,0,0,0,0],
            [0,-akt[2],0,0,0,0,0,0,0,0,0,0],
            [0,0,-akt[4],0,0,0,0,0,0,0,0,0],
            [0,0,0,-akt[5],0,0,0,0,0,0,0,0],
            [0,0,0,0,-akt[6],0,0,0,0,0,0,0]]
    b_ub = [max_co2,-min_vals[0],-min_vals[1],-min_vals[2],-min_vals[3],-min_vals[4]]
    A_eq = [[-akt[0]*53*1860*1/6*1/340,0,0,0,0,1,0,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/660,0,0,0,0,0,1,0,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/1630,0,0,0,0,0,0,1,0,0,0,0],
            [-akt[0]*53*1860*1/6*1/3040,0,0,0,0,0,0,0,1,0,0,0],
            [-akt[0]*53*1860*1/6*1/860,0,0,0,0,0,0,0,0,1,0,0],
            [-akt[0]*53*1860*1/6*1/1370,0,0,0,0,0,0,0,0,0,1,0]]
    b_eq = [0.273*365+akt[0]*53*1860*1/6*1/340, 0.202*365+akt[0]*53*1860*1/6*1/660, 0.427*365+akt[0]*53*1860*1/6*1/660, 0.212*365+akt[0]*53*1860*1/6*1/3040, 0.151*365+akt[0]*53*1860*1/6*1/860, 0.04*365+akt[0]*53*1860*1/6*1/1370]
    
    #Löse lineares Programm
    res = sc.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=[(0,1),(0,1),(0,1),(0,1),(0,1),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None)], method='simplex')
        
    return res.x
       
# 
# Titellines -----------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Fußabdruck', page_icon=None, layout='wide', initial_sidebar_state='expanded')
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
c1,c2 = st.beta_columns((7,2))
c1.write("""
        # Fußabdruck - Optimierung
        ## Optimiere deinen ökologischen Fußabdruck
    """)
navigation = c2.selectbox('', ["Startseite","Fußabdruck-Rechner", "Umsetzung & Mathematischer Hintergrund", "Persönlicher Fußabdruck", "Budget Berechnung", "Impressum"])
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
    imagestart= Image.open('Startseite.png')
    c2.image(imagestart,width=1000, clamp=False, channels='RGB', output_format='auto')
    

elif navigation == 'Umsetzung & Mathematischer Hintergrund':
    st.write("""
             ## Umsetzung und Grundsätze der Modellierung
             Neben der Auskunft über den persönlichen CO2-Verbrauch pro Jahr soll mit der Modellierung eine Handlungsempfehlung gegeben werden, wie das Verhalten verändert könnte, um das CO2-Ziel einzuhalten. Unser Ziel ist es, die Eingabe für den Benutzer möglichst einfach zu gestalten. Deshalb ist es in einigen Bereichen notwendig Verallgemeinerungen zu treffen. Zur Berechnung des persönlichen CO2-Verbrauchs pro Jahr sollen folgende Bereiche berücksichtig werden:
             """)
    st.write("1.	Nahrung")
    st.write("2.	Wohnen")
    st.write("3.	Mobilität")
    st.write("4.	Konsum")
    st.write("""
             Dabei werden zu diesen Bereichen vom Benutzer bestimmte Angaben abgefragt, die die Höhe des Verbrauchs bestimmen. 
             Damit die Empfehlungen für das künftige Verhalten zu den Bedürfnissen des Benutzers passen, können ebenfalls Angaben dazu gemacht werden, wie wichtig es dem Benutzer ist, bestimmte Aspekte beizubehalten. So soll sichergestellt werden, dass der Vorschlag zur Anpassung des persönlichen Verhaltens auch umgesetzt werden kann. 
             """)
    
    
elif navigation == 'Fußabdruck-Rechner':
    st.write("""
             Im November 2016 beschloss das Bundeskabinett den Klimaschutzplan 2050. Darin sind die Klimaschutzziele der Bundesrepublik Deutschland festgelegt, die im Einklang mit dem Pariser Übereinkommen stehen. So sollen die Treibhausgasemissionen bis 2050 um 80 bis 95 Prozent reduziert werden im Vergleich zum Wert von 1990. Die Einhaltung dieses Ziels stellt nicht nur die Politik und große Unternehmen vor eine große Herausforderung, sondern wird auch großen Einfluss auf die Bevölkerung haben. Jeder Einzelne wird sich auf Einschränkungen einlassen müssen und einen Beitrag zum Klimaschutz leisten müssen. Doch wie könnten diese Einschränkungen für die Bevölkerung von Deutschland aussehen? 
             Unsere Modellierung basiert auf dem bekannten Konzept eines CO2-Fußabdruck-Rechners. Allerdings soll darüber hinaus auf der Grundlage des persönlichen jährlichen CO2-Verbrauchs eine Empfehlung gegeben werden, wie das Verhalten verändert werden könnte, um das CO2-Ziel einzuhalten. """)
             
    # Sidebar ----------------------------------------------------------------------------------------------------------------------
    # Sidebar sind Abfragen nach aktuellem Zustand
    st.sidebar.header('Eingabeparameter zur Berechnung deines aktuellen CO2-Fußabdrucks')
    
    st.sidebar.markdown("***")
    st.sidebar.write("""
        ### Kategorie: Ernährung
    """)
    nahrung1 = st.sidebar.text_input(label='Wie viel Kilogramm Fleisch und Fisch konsumierst du wöchentlich?', value=1.1)
    nahrung2 = st.sidebar.radio('Wie wichtig ist dir, dass die Lebensmittel regional sind?',['sehr wichtig','manchmal wichtig','garnicht wichtig'])
    st.sidebar.markdown("***")
    st.sidebar.write("""
        ### Kategorie: Wohnen
    """)
    wohnen1 = st.sidebar.slider(label='Auf wie viel Grad heizt du deine Wohnung normalerweise?', min_value=18,max_value=24,step=1)
    wohnen2 = st.sidebar.text_input(label='Wie viel Quadratmeter Wohnfläche hast du zur Verfügung (pro Person)?', value=47)
    st.sidebar.markdown("***")
    st.sidebar.write("""
        ### Kategorie: Mobilität
    """)
    mob1 = st.sidebar.text_input(label='Wie viel Kilometer fährst du pro Jahr mit dem Auto (pro Person)?', value=11888)
    mob2 = st.sidebar.text_input(label='Wie viele Stunden bist du in den letzten vier Jahren geflogen?', value=12)
    st.sidebar.markdown("***")
    st.sidebar.write("""
        ### Kategorie: Konsum
    """)
    konsum1 = st.sidebar.text_input(label='Wie viele Kleidungsstücke kaufst du im Jahr?', value=60)
    #-------------------------------------------------------------------------------------------------------------------------
    
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
    #chart_data = pd.DataFrame(data=d, index=['Nahrung', 'Wohnen', 'Mobilität', 'Konsum (Kleidung)'])
    
    #st.write(chart_data)
    #st.bar_chart(chart_data)
    
    df = pd.DataFrame(
        [["Nahrung", 1704,co2_akt_nach_kat[0]], ["Wohnen", 2730,co2_akt_nach_kat[1]], ["Mobilität", 3125,co2_akt_nach_kat[2]],["Konsum (Kleidung)",507,co2_akt_nach_kat[3]]],
        columns=["Kategorie","Durschnitt CO2 Deutschland", "Dein CO2"])
    fig = px.bar(df, x="Kategorie", y=["Durschnitt CO2 Deutschland", "Dein CO2"], barmode='group', height=400)
    st.plotly_chart(fig)
    
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
    min_val_mob1 = col3.text_input(label='Minimale Autokilometer pro Jahr', value=0)
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

    
    st.write('Reduziere deinen ökologischen Fußabdruck, indem du deinen Verbrauch auf die folgenden Prozente reduzierst:')
    st.write('Reduziere deinen Fleischkonsum auf    '+str(round(solution[0],4)*100)+'%.')
    st.write('Reduziere deinen Zimmerwärme auf    '+str(round(solution[1],4)*100)+'%.')
    st.write('Reduziere deine Autokilometer auf    '+str(round(solution[2],4)*100)+'%.')
    st.write('Reduziere deine Flugstunden auf    '+str(round(solution[3],4)*100)+'%.')
    st.write('Reduziere deinen gekauften Kleidungsstücke auf    '+str(round(solution[4],4)*100)+'%.')
    
    
# Pro Kopf Budget ---------------------------------------------------------------------------------------------------------
elif navigation == 'Persönlicher Fußabdruck':
    st.write("""
             ## Berechnung des persönlichen CO2-Verbrauchs
             Zur Ermittlung des pro Kopf CO2-Verbrauch wird der persönliche Gesamtverbrauch in verschiedene Bereiche unterteilt. Auf der Grundlage des persönlichen Verhaltens wird der individuelle CO2-Verbrauch berechnet. Darüber hinaus wird eine Handlungsempfehlung ausgegeben, die die Reduzierung gewisser Aspekte vorschlägt, um das persönliche CO2-Budget einhalten zu können. 
             """)
    st.markdown("***")
    st.write("""
             ## Nahrung
             Die Datengrundlage für die Berechnung des persönlichen CO2-Verbrauchs durch die Nahrung bildet die folgende Tabelle.
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image3= Image.open('Tab3_Nahrungswerte.PNG')
    c2.image(image3, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zur Berechnung des persönlichen CO2-Verbrauchs durch die Nahrung werden vom Benutzer folgende Aspekte selbst angegeben:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.write("1. Verzehrmenge Fleisch pro Woche in kg 2")
    c2.write("2. Regionale Lebensmittel")
    st.write("""Die Berechnung des CO2-Verbrauchs durch die Nahrung werden die durchschnittlichen jährlichen Verzehrmengen mit den entsprechenden CO2-Werten multipliziert und über alle Lebensmittelgruppen aufaddiert, wobei die Verzehrmenge Fleisch vom Benutzer angegeben wird. Entsprechend muss bei der Berechnung diese wöchentliche Angabe durch Multiplikation mit dem Faktor 53 (Anzahl der Wochen pro Jahr) berücksichtigt werden. Damit der Aspekt „2. Regionale und saisonale Lebensmittel“ in die Berechnung einfließen kann, werden gemäß [] die entsprechenden Faktoren aus Tabelle 4 einbezogen. 
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image4= Image.open('Tab4_regio.PNG')
    c2.image(image4, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("""
             Zunächst wird so der CO2-Wert durch die Nahrung berechnet gemäß dem folgenden Zusammenhang.
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image5= Image.open('Formel_Essen.PNG')
    c2.image(image5, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("""
             Es soll nicht nur der persönliche CO2-Verbrauch berechnet werden, sondern darüber hinaus soll dem Benutzer vorgeschlagen werden, wie er sein Verhalten verändern kann, um zu einem bestimmten Zeitpunkt unter dem pro Kopf CO2-Budget zu bleiben. In Bezug auf die Nahrung soll dabei, falls nötig und erwünscht die Verzehrmenge Fleisch reduziert werden, da ihr gemäß Tabelle 3 ein hoher CO2-Wert zugeordnet wird. Dabei soll eine Reduzierung der Fleischmenge nicht dazu führen, dass der Benutzer insgesamt weniger isst. Aus diesem Grund wird die reduzierte Menge auf die andren Lebensmittelgruppe verteilt. Um eine möglichst realistische Einschätzung hierzu zu geben, wird der tägliche Kalorien bedarf ausgehend von der angegebenen Verzehrmenge Fleisch und den durchschnittlichen Verzehrmengen der übrigen Lebensmittelgruppen berechnet. Zu der vorgeschlagenen Reduzierung der Verzehrmenge Fleisch wird die entsprechende Kalorienangabe ermittelt und auf die anderen Lebensmittelgruppen verteilt. Grundlage für diese Berechnungen bilden die folgenden Zusammenhänge. 
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image6= Image.open('Formel_Fleischersatz.PNG')
    c2.image(image6, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Wohnen")
    st.write("Die Datengrundlage für die Berechnung des persönlichen CO2-Verbrauchs durch den Aspekt Wohnen bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image7= Image.open('Tab5_Wohnen.PNG')
    c2.image(image7, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Der berechnete Wert des persönlichen CO2-Verbrauchs durch den Aspekt Wohnen soll personalisiert werden, indem der Benutzer folgende Angaben macht:")
    c1,c2,c3 = st.beta_columns([1,10,1])
    c2.write("1. Wohnfläche pro Person")
    c2.write("2. Eingestellte Raumtemperatur")
    st.write("""Mit diesen beiden Größen wird der CO2-Verbrauch des Benutzers für den Aspekt Wohnen durch die folgende Beziehung berechnet.""")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image8= Image.open('Formel_Wohnen.PNG')
    c2.image(image8, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Mobilität")
    st.write("Die Datengrundlage für die Berechnung des persönlichen CO2-Verbrauchs durch den Aspekt Mobilität bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image9= Image.open('Tab6_Mobilität.PNG')
    c2.image(image9, width=700, clamp=False, channels='RGB', output_format='auto')
    
    st.markdown("***")
    st.write("## Konsum")
    st.write("Die Datengrundlage für die Berechnung des persönlichen CO2-Verbrauchs durch den Konsum bildet die folgende Tabelle. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image10= Image.open('Tab7_Konsum.PNG')
    c2.image(image10, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Der Benutzer soll dabei folgende Angabe zu seinem Konsumverhalten machen:")
    st.write("1. Anzahl gekaufte Kleidungsstücke pro Jahr.")
    st.write("Unter Berücksichtigung dieser Angabe wird der persönliche CO2-Verbrauch durch den Aspekt Konsum durch den folgenden Zusammenhang berechnet.")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image11= Image.open('Formel_Konsum.PNG')
    c2.image(image11, width=700, clamp=False, channels='RGB', output_format='auto')
    
elif navigation == "Budget Berechnung":
    st.write("""
             ## Berechnung des pro Kopf Budgets (Deutschland)
             Zunächst soll der Anteil der Bevölkerung am CO2-Gesamtverbrauch von Deutschland bestimmt werden. Dieser ermöglicht es uns im weiteren Verlauf ausgehend von künftigen Klimazielen des Landes das persönliche CO2-Budget pro Kopf zu berechnen und Handlungsempfehlungen zur Reduzierung des persönlichen CO2-Verbrauchs auszusprechen. 
            Die folgende Tabelle bildet die Grundlage der Berechnung des Anteils der Bevölkerung am CO2-Gesamtverbrauch von Deutschland.
            """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image12= Image.open('Tab1_Einwohnerzahlen.PNG')
    c2.image(image12, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zunächst kann nun der gesamte durch die Bevölkerung verursachte CO2-Verbrauch (A_{Bev}) für die entsprechenden Jahre aus Tab. 1 berechnet werden. ")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image13= Image.open('Formel_Bev1.PNG')
    c2.image(image13, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("Somit kann der prozentuale Anteil der durch die Bevölkerung verursachten Emissionen (P_{Bev}) an den bundesweiten Emissionen bestimmt werden.")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image14= Image.open('Formel_Bev2.PNG')
    c2.image(image14, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("Die gemäß dieser Formeln berechneten Werte sind nachfolgend dargelegt. ")
    c1,c2,c3 = st.beta_columns([1,3,1])
    image15= Image.open('Tab2_Einwohner.PNG')
    c2.image(image15, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Zuletzt wird der Mittelwert (\bar{P_{Bev}}) gebildet über alle so bestimmten Anteile des CO2-Verbrauchs der Bevölkerung. ")
    c1,c2,c3 = st.beta_columns([2,3,1])
    image16= Image.open('Wert_Bev.PNG')
    c2.image(image16, width=300, clamp=False, channels='RGB', output_format='auto')
    st.write("""Dieser Wert sagt aus, dass der durch die Bevölkerung verursachte CO2-Verbrauch ungefähr 83% ausmacht. 
             Er erlaubt es uns, für künftige bundesweite CO2-Budgets ein pro Kopf Budget vorherzusagen. """)
    st.markdown("***")
    st.write("""
             ## Künftige CO2-Budgets
             Damit künftige pro Kopf CO2-Budgets berechnet werden können, soll hier das zu Grunde liegende Modell vorgestellt werden. Die Daten basieren auf dem Klimaschutzplan 2050, der vom Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit (BMU) veröffentlicht wurde. Demnach sollen ausgehend vom Jahr 1990 bis 2030 die CO2-Emissionen mindestens um 55%, bis 2040 um 70% und bis 2050 um 80%-95% gesenkt werden. Die sich aus diesen Zielen ergebenden CO2-Budgets sind in Abbildung 1 dargestellt.  
             """)
    c1,c2,c3 = st.beta_columns([1,3,1])
    image17= Image.open('Emissionsziel.PNG')
    c2.image(image17, width=700, clamp=False, channels='RGB', output_format='auto')
    st.write("Mit dieser Datengrundlage und dem zuvor ermittelten Anteil des CO2-Verbrauches der Bevölkerung kann der pro Kopf Ausstoß für künftige Szenarien ermittelt werden. ")
    
else:
    
    #link = '[GitHub](http://github.com)'
    #st.markdown(link, unsafe_allow_html=True)
    st.write("von Lena Bill & Paula Fleischer")
    
    
        
