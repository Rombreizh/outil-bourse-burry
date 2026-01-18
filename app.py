import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Burry Hunter Tool", layout="wide")
st.title("🦅 Chasser les Oiseaux Rares")
st.caption("D'après la méthodologie du Docteur Burry")

# --- PARAMÈTRES DANS LA BARRE LATÉRALE ---
st.sidebar.header("Configuration")
seuil_ev_ebitda = st.sidebar.slider("Seuil EV/EBITDA max", 0.0, 15.0, 8.0)
rendement_voulu = st.sidebar.slider("Rendement voulu (%)", 5, 20, 10) / 100

# --- FONCTIONS TECHNIQUES ---
def analyser_secteurs_deprimes():
    secteurs_etfs = {
        "Technologie": "XLK", "Finance": "XLF", "Santé": "XLV", 
        "Energie": "XLE", "Consommation": "XLY", "Industrie": "XLI",
        "Utilities": "XLU", "Immobilier": "XLRE", "Matériaux": "XLB"
    }
    secteur_data = []
    for nom, ticker in secteurs_etfs.items():
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period="1y")
            perf_1an = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
            secteur_data.append({"Secteur": nom, "Perf 1 An (%)": round(perf_1an, 2)})
        except: continue
    return pd.DataFrame(secteur_data).sort_values(by="Perf 1 An (%)")

# --- ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🔍 Scanner & Secteurs", "💎 Valeur Intrinsèque", "📊 Portefeuille"])

with tab1:
    st.subheader("🕵️ Identification des Secteurs Déprimés")
    if st.button("Analyser la psychologie du marché"):
        df_secteurs = analyser_secteurs_deprimes()
        st.dataframe(df_secteurs.style.background_gradient(cmap='RdYlGn', subset=['Perf 1 An (%)']))
        st.info(f"💡 Conseil : Cherche tes actions dans le secteur **{df_secteurs.iloc[0]['Secteur']}**.")

    st.divider()
    st.subheader("🚀 Scanner EV/EBITDA")
    tickers_input = st.text_input("Liste de tickers (ex: VALE, TTE, STNE, BABA)", "VALE, TTE, STNE, BABA, GME")
    if st.button("Lancer le Scan"):
        results = []
        for t in [x.strip().upper() for x in tickers_input.split(",")]:
            s = yf.Ticker(t)
            ev_ebitda = s.info.get('enterpriseToEbitda')
            if ev_ebitda and ev_ebitda < seuil_ev_ebitda:
                results.append({"Ticker": t, "Nom": s.info.get('shortName'), "EV/EBITDA": round(ev_ebitda, 2), "Prix": s.info.get('currentPrice')})
        st.dataframe(pd.DataFrame(results))

with tab2:
    st.subheader("💎 Calculateur DCF (Étape 3)")
    target = st.text_input("Ticker à analyser", "VALE")
    if target:
        try:
            stock = yf.Ticker(target)
            fcf = stock.cashflow.loc['Free Cash Flow'].iloc[0]
            price = stock.info.get('currentPrice')
            shares = stock.info.get('sharesOutstanding')
            term_val = (fcf * (1.05)**10) / (rendement_voulu - 0.02)
            intr_val = (term_val / (1 + rendement_voulu)**10) / shares
            upside = ((intr_val / price) - 1) * 100
            st.metric("Potentiel (Upside)", f"{round(upside, 2)}%", delta=f"{round(upside, 2)}%")
        except: st.error("Données indisponibles.")

with tab3:
    st.subheader("📊 Suivi (Étape 4 & 5)")
    st.write("Ici s'afficheront vos 12 à 18 valeurs et les alertes de vente à +50%.")
