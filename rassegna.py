import streamlit as st
import pandas as pd
import os
from newspaper import Article

# Configurazione della pagina
st.set_page_config(page_title="Rassegna Stampa 3° Rally Valle del Belìce", page_icon="🏎️", layout="wide")

# Funzione per caricare i dati dal file Excel corretto
@st.cache_data
def load_data():
    file_name = "rassegna_stampa_rally_preparata.xlsx"
    if os.path.exists(file_name):
        return pd.read_excel(file_name, engine='openpyxl')
    return None

df = load_data()

if df is not None:
    # Pulizia nomi colonne
    df.columns = df.columns.str.strip()
    
    # Titolo principale
    st.markdown("<h1>🏎️ Rassegna Stampa 3° Rally Valle del Belìce</h1>", unsafe_allow_html=True)
    
    # Pulsante superiore "Apri vista completa per la stampa"
    if st.button("🖨️ Apri vista completa per la stampa (tutti gli articoli)"):
        st.session_state['vista_stampa_rally'] = not st.session_state.get('vista_stampa_rally', False)

    st.markdown("---")

    # Funzione per estrarre titolo, testo e immagine in automatico
    @st.cache_data
    def get_article_details(url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            img = article.top_image
            if not img and article.meta_img:
                img = article.meta_img
                
            return {
                'titolo': article.title if article.title else "Senza Titolo",
                'testo': article.text if article.text else "Nessun contenuto disponibile.",
                'immagine': img if img else None
            }
        except Exception:
            return {
                'titolo': "Titolo non disponibile",
                'testo': "Impossibile estrarre il contenuto dal link.",
                'immagine': None
            }

    # Vista completa per la stampa
    if st.session_state.get('vista_stampa_rally', False):
        st.markdown("### Vista Completa per la Stampa")
        for idx, row in df.iterrows():
            url = row.get('Link')
            data = str(row.get('Data', ''))[:10]
            testata = row.get('Testata', '')
            
            info = get_article_details(url) if pd.notna(url) else {'titolo': 'N/D', 'testo': '', 'immagine': None}
            
            st.markdown(f"### {info['titolo']}")
            st.markdown(f"**Data:** {data} | **Testata:** {testata}")
            
            if info['immagine']:
                try:
                    st.image(info['immagine'], width=500)
                except Exception:
                    pass

            st.markdown(f"{info['testo']}")
            if pd.notna(url):
                st.markdown(f"[🔗 Leggi l'articolo originale]({url})")
            st.markdown("---")
            
        if st.button("⬅️ Torna alla visualizzazione normale"):
            st.session_state['vista_stampa_rally'] = False
            st.rerun()

    else:
        # Inizializzazione stato scorrimento
        if 'current_index_rally' not in st.session_state:
            st.session_state['current_index_rally'] = 0

        total_articoli = len(df)
        
        # Creazione opzioni menu a tendina
        selectbox_options = []
        for i, r in df.iterrows():
            d = str(r.get('Data', ''))[:10]
            t = str(r.get('Testata', 'Testata'))
            selectbox_options.append(f"{i+1}. {d} - {t}")

        # Navigazione
        col_prec, col_select, col_succ = st.columns([1, 3, 1])

        with col_prec:
            if st.button("⬅️ Precedente", use_container_width=True):
                if st.session_state['current_index_rally'] > 0:
                    st.session_state['current_index_rally'] -= 1

        with col_select:
            selected_option = st.selectbox(
                "Seleziona articolo",
                options=selectbox_options,
                index=st.session_state['current_index_rally'],
                label_visibility="collapsed"
            )
            selected_index = selectbox_options.index(selected_option)
            if selected_index != st.session_state['current_index_rally']:
                st.session_state['current_index_rally'] = selected_index

        with col_succ:
            if st.button("Successivo ➡️", use_container_width=True):
                if st.session_state['current_index_rally'] < total_articoli - 1:
                    st.session_state['current_index_rally'] += 1

        st.markdown("---")

        # Estrazione riga corrente
        current_row = df.iloc[st.session_state['current_index_rally']]
        testata_corr = str(current_row.get('Testata', 'N/D'))
        data_val = current_row.get('Data')
        data_corr = str(data_val)[:10] if pd.notna(data_val) else 'N/D'
        link_corr = current_row.get('Link')

        # Estrazione automatica
        article_info = get_article_details(link_corr) if pd.notna(link_corr) else {'titolo': 'N/D', 'testo': '', 'immagine': None}

        # Intestazione
        st.markdown(f"<h2>Testata: {testata_corr}</h2>", unsafe_allow_html=True)
        st.markdown(f"📅 **Data:** {data_corr} (Articolo {st.session_state['current_index_rally'] + 1} di {total_articoli})")

        # Box contenuto con layout a due colonne (Foto a sinistra, Testo a destra)
        with st.container():
            col_img, col_text = st.columns([2, 3])

            with col_img:
                if article_info['immagine']:
                    try:
                        st.image(article_info['immagine'], use_container_width=True)
                    except Exception:
                        st.write("*(Immagine non disponibile)*")
                else:
                    st.write("*(Nessuna anteprima immagine)*")

            with col_text:
                st.markdown(f"<h3>{article_info['titolo']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 15px; line-height: 1.5;'>{article_info['testo']}</p>", unsafe_allow_html=True)
                
                if pd.notna(link_corr):
                    st.markdown(f"[🔗 Leggi l'articolo originale]({link_corr})")

else:
    st.warning("⚠️ File `rassegna_stampa_rally_preparata.xlsx` non trovato nella cartella.")