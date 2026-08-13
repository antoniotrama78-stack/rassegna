import streamlit as st
import pandas as pd
from newspaper import Article

# 1. Caricamento Dati
@st.cache_data
def load_data():
    return pd.read_excel('rassegna_stampa_rally_preparata.xlsx')

df = load_data()

st.title("📰 Rassegna Stampa Rally")

# Inseriamo un piccolo stile CSS per forzare il salto pagina netto quando si stampa
st.markdown("""
    <style>
    @media print {
        .articolo-stampa {
            page-break-before: always !important;
            break-before: page !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Inizializziamo lo stato per la vista normale o stampa globale
if 'modalita_stampa' not in st.session_state:
    st.session_state.modalita_stampa = False

# Pulsante in alto per attivare la vista di stampa globale di tutti gli articoli
if not st.session_state.modalita_stampa:
    if st.button("🖨️ Apri vista completa per la stampa (tutti gli articoli)", use_container_width=True):
        st.session_state.modalita_stampa = True
        st.rerun()
else:
    if st.button("⬅️ Torna alla navigazione normale", use_container_width=True):
        st.session_state.modalita_stampa = False
        st.rerun()

st.divider()

# SEZIONE 1: VISTA STAMPA GLOBALE
if st.session_state.modalita_stampa:
    st.info("💡 **Istruzioni per salvare in PDF:** Premi **Ctrl + P**, seleziona **Salva come PDF** e assicurati di spuntare **'Grafiche di sfondo'** nelle impostazioni di stampa.")
    st.markdown("---")
    
    for i, row in df.iterrows():
        # Contenitore con la classe CSS dedicata al salto pagina
        st.markdown(f'<div class="articolo-stampa"></div>', unsafe_allow_html=True)
        
        # Titolo dell'articolo
        st.markdown(f"### Articolo {i+1} di {len(df)} - {row['Testata']} ({row['Data'].strftime('%d/%m/%Y')})")
        
        if pd.notna(row['Link']):
            try:
                art = Article(row['Link'])
                art.download()
                art.parse()
                
                card_html = f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background-color: #f9f9f9; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <img src="{art.top_image}" style="width: 100%; max-height: 350px; object-fit: cover;">
                    <div style="padding: 20px;">
                        <p style="color: #666; font-size: 12px; margin: 0; text-transform: uppercase;">{row['Testata']}</p>
                        <h3 style="color: #111; font-size: 20px; margin: 5px 0 15px 0;">{art.title}</h3>
                        <div style="color: #333; font-size: 14px; line-height: 1.5;">{art.text.replace(chr(10), '<br>')}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
            except Exception:
                st.warning(f"Impossibile caricare i contenuti multimediali per l'articolo {i+1}.")
        
        st.markdown("<br>", unsafe_allow_html=True)

# SEZIONE 2: NAVIGAZIONE STANDARD CON SFOGLIATORE
else:
    if 'indice_articolo' not in st.session_state:
        st.session_state.indice_articolo = 0

    totale_articoli = len(df)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Precedente", use_container_width=True):
            if st.session_state.indice_articolo > 0:
                st.session_state.indice_articolo -= 1
    with col3:
        if st.button("Successivo ➡️", use_container_width=True):
            if st.session_state.indice_articolo < totale_articoli - 1:
                st.session_state.indice_articolo += 1
    with col2:
        opzioni = [f"{i+1}. {row.Data.strftime('%d/%m')} - {row.Testata}" for i, row in df.iterrows()]
        scelta_corrente = st.selectbox("Vai a:", opzioni, index=st.session_state.indice_articolo, label_visibility="collapsed")
        st.session_state.indice_articolo = opzioni.index(scelta_corrente)

    st.divider()

    articolo = df.iloc[st.session_state.indice_articolo]
    st.subheader(f"Testata: {articolo['Testata']}")
    st.write(f"📅 **Data:** {articolo['Data'].strftime('%d/%m/%Y')} (Articolo {st.session_state.indice_articolo + 1} di {totale_articoli})")

    if pd.notna(articolo['Link']):
        with st.spinner("Caricamento contenuto in corso..."):
            try:
                art = Article(articolo['Link'])
                art.download()
                art.parse()
                
                card_html = f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background-color: #f9f9f9; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <img src="{art.top_image}" style="width: 100%; max-height: 300px; object-fit: cover;">
                    <div style="padding: 15px;">
                        <p style="color: #666; font-size: 12px; margin: 0; text-transform: uppercase;">{articolo['Testata']}</p>
                        <h3 style="color: #111; font-size: 18px; margin: 5px 0 10px 0;">{art.title}</h3>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                if art.text:
                    st.markdown("### Contenuto dell'articolo")
                    st.write(art.text)
                
            except Exception:
                st.warning("Impossibile estrarre automaticamente il testo per questo link.")

        st.link_button("🔗 Apri l'articolo originale", articolo['Link'], use_container_width=True)