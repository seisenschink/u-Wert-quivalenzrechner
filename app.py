import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

def berechne_u_wert(schichtdicken, lambda_werte, r_uebergang):
    """
    Berechnet den U-Wert einer Konstruktion basierend auf den Schichtdicken, Wärmeleitfähigkeiten und Übergangswiderständen.
    """
    r_gesamt = sum(d / l for d, l in zip(schichtdicken, lambda_werte))
    r_gesamt += r_uebergang  # Wärmeübergangswiderstände
    return 1 / r_gesamt

def plot_u_wert(daemmstoffe, schichtdicken, lambda_werte, daemmstärken, r_uebergang, u_zielwerte, farbpalette, hintergrundfarbe):
    """
    Erstellt eine moderne grafische Darstellung des U-Werts mit Plotly und Farbwahl.
    """
    fig = go.Figure()
    
    for name, lambda_daemmung in daemmstoffe.items():
        u_werte = [berechne_u_wert(schichtdicken + [d], lambda_werte + [lambda_daemmung], r_uebergang) for d in daemmstärken]
        fig.add_trace(go.Scatter(x=daemmstärken, y=u_werte, mode='lines', name=name))
    
    for u in u_zielwerte:
        fig.add_hline(y=u, line_dash='dash', annotation_text=f'U = {u} W/m²K')
    
    fig.update_layout(
        title="U-Wert in Abhängigkeit der Dämmstärke",
        xaxis_title="Dämmstärke [m]",
        yaxis_title="U-Wert [W/m²K]",
        template=farbpalette,
        plot_bgcolor=hintergrundfarbe
    )
    
    return fig

def erstelle_tabelle(daemmstoffe, schichtdicken, lambda_werte, r_uebergang):
    """
    Erstellt eine tabellarische Darstellung der U-Werte in 2 cm Schritten.
    """
    daemmstärken = np.arange(0.02, 0.52, 0.02)  # 2 cm Schritte bis 50 cm
    daten = {"Dämmstärke [m]": daemmstärken}
    
    for name, lambda_daemmung in daemmstoffe.items():
        daten[name] = [berechne_u_wert(schichtdicken + [d], lambda_werte + [lambda_daemmung], r_uebergang) for d in daemmstärken]
    
    return pd.DataFrame(daten)

# Streamlit App
st.title("U-Wert Rechner")
st.sidebar.image("https://www.jung-ebs.de/wp-content/themes/ipj/icons/ipj-svg-130.png")
# Eingaben für Tragkonstruktion
st.sidebar.header("Tragkonstruktion")
tragkonstruktion_name = st.sidebar.text_input("Name der Tragkonstruktion", "Bitte Namen der Tragschicht eingeben")
tragkonstruktion_dicke = st.sidebar.slider("Dicke der Tragkonstruktion (m)", 0.1, 0.5, 0.24, 0.01)
tragkonstruktion_lambda = st.sidebar.number_input("Wärmeleitfähigkeit der Tragkonstruktion (W/mK)", 0.1, 2.0, 0.18, 0.01)
putz_dicke = st.sidebar.slider("Dicke des Putzes (m)", 0.005, 0.05, 0.015, 0.001)
putz_lambda = st.sidebar.number_input("Wärmeleitfähigkeit des Putzes (W/mK)", 0.1, 2.0, 0.8, 0.01)

# Übergangswiderstände
st.sidebar.header("Übergangswiderstände")
uebergang_option = st.sidebar.radio("Bauteilart wählen", ["Wand", "Boden", "Dach"], index=0)

r_uebergang = 0.13 + 0.04  # Standard für Wand
if uebergang_option == "Boden":
    r_uebergang = 0.17 + 0.04
elif uebergang_option == "Dach":
    r_uebergang = 0.10 + 0.04

# Eigene Eingabe von Dämmstoffen
st.sidebar.header("Benutzerdefinierte Dämmstoffe")
daemmstoff_name = st.sidebar.text_input("Name des Dämmstoffs")
daemmstoff_lambda = st.sidebar.number_input("Wärmeleitfähigkeit des Dämmstoffs (W/mK)", 0.01, 1.0, 0.035, 0.001)

# Standard-Dämmmaterialien
daemmstoffe = {
    "Mineralwolle": 0.035,
    "EPS": 0.032,
    "Holzfaser": 0.045,
    "PU": 0.028
}

# Falls benutzerdefinierter Dämmstoff eingegeben wurde, hinzufügen
if daemmstoff_name and daemmstoff_lambda:
    daemmstoffe[daemmstoff_name] = daemmstoff_lambda

# Auswahl der Dämmmaterialien
st.sidebar.header("Dämmmaterialien")
waehle_daemmstoffe = {material: lambda_wert for material, lambda_wert in daemmstoffe.items() if st.sidebar.checkbox(material, True)}

# Auswahl der U-Wert Äquivalenzlinien
st.sidebar.header("Äquivalenzlinien")
u_zielwerte = st.sidebar.text_input("U-Werte als Komma-separierte Liste eingeben", "0.3, 0.24, 0.2, 0.15")
u_zielwerte = [float(x.strip()) for x in u_zielwerte.split(",") if x.strip()]

# Farbpaletten für Darstellung
st.sidebar.header("Darstellung")
farbpalette = st.sidebar.selectbox("Farbpalette wählen", ["plotly", "ggplot2", "seaborn", "simple_white", "plotly_dark"])
hintergrundfarbe = st.sidebar.color_picker("Hintergrundfarbe des Plots", "#ffffff")

# Auswahl der Dämmstärke
daemmstärken = np.linspace(0.01, 0.5, 50)  # Mehr Punkte für glatteren Verlauf

# Berechnung
schichtdicken = [tragkonstruktion_dicke, putz_dicke]
lambda_werte = [tragkonstruktion_lambda, putz_lambda]

fig = plot_u_wert(waehle_daemmstoffe, schichtdicken, lambda_werte, daemmstärken, r_uebergang, u_zielwerte, farbpalette, hintergrundfarbe)
st.plotly_chart(fig)

# Tabellarische Ausgabe
tabelle = erstelle_tabelle(waehle_daemmstoffe, schichtdicken, lambda_werte, r_uebergang)
st.write("### Tabellarische U-Werte")
st.dataframe(tabelle)
