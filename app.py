import streamlit as st
import pandas as pd

# 1. Configurazione della pagina web
st.set_page_config(
    page_title="Gestione Scaffali Biblioteca",
    page_icon="📚",
    layout="wide"
)

# 2. Inizializzazione dello stato della memoria (Session State)
# Serve a non perdere i dati quando l'utente clicca sui pulsanti o rinfresca la pagina
if 'matrice_dati' not in st.session_state:
    # Dimensioni di default: 4 ripiani x 3 moduli
    st.session_state.ripiani = 4
    st.session_state.moduli = 3
    
    # Creazione struttura vuota
    st.session_state.matrice_dati = [
        [["Vuoto", 0.0] for _ in range(st.session_state.moduli)]
        for _ in range(st.session_state.ripiani)
    ]
    
    # Prepopolamento dati di esempio
    st.session_state.matrice_dati[3][0] = ["Tipologia A (Enciclopedie)", 40.0] # Ripiano 4, Modulo 1
    st.session_state.matrice_dati[3][1] = ["Tipologia B (Riviste)", 25.0]       # Ripiano 4, Modulo 2
    st.session_state.matrice_dati[1][2] = ["Tipologia E (Fascicoli)", 120.0]     # Ripiano 2, Modulo 3
    st.session_state.matrice_dati[0][1] = ["Tipologia H (Archivio)", 300.0]      # Ripiano 1, Modulo 2

# 3. BARRA LATERALE (Sidebar) per le configurazioni globali
st.sidebar.header("⚙️ Configurazione Globale")
nome_scaffale = st.sidebar.text_input("Nome dello Scaffale", 'Scaffale "Libri Storici"')
lunghezza_modulo = st.sidebar.number_input("Lunghezza singolo modulo (m)", min_value=0.5, value=2.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Calcolo Flotta Scaffali")
num_scaffali_totali = st.sidebar.number_input("Numero di scaffali totali", min_value=1, value=5, step=1)
tara_singolo_scaffale = st.sidebar.number_input("Tara singolo scaffale (kg)", min_value=0, value=80, step=5)

# 4. CORPO PRINCIPALE della pagina
st.title("📚 Sistema di Gestione Scaffalature Biblioteca")
st.subheader(f"Mappa attuale: {nome_scaffale}")
st.write(f"Dimensioni: {st.session_state.ripiani} Ripiani × {st.session_state.moduli} Moduli (Campata da {lunghezza_modulo}m)")

# Creazione delle schede (Tab) per separare la visualizzazione dalla modifica
tab_mappa, tab_modifica = st.tabs(["👁️ Visualizza Mappa & Report", "✏️ Modifica Dati Matrice"])

with tab_mappa:
    # Costruzione della tabella visuale in stile matrice di stoccaggio
    righe_tabella = []
    # Scorre al contrario per mostrare il ripiano più alto in cima alla pagina web
    for r in range(st.session_state.ripiani - 1, -1, -1):
        info_riga = {}
        for m in range(st.session_state.moduli):
            tipologia, peso = st.session_state.matrice_dati[r][m]
            info_riga[f"Modulo {m+1}"] = f"[{tipologia}] {peso} kg"
        righe_tabella.append(info_riga)
    
    # Creazione degli indici verticali (Ripiano 4, Ripiano 3...)
    indici_verticali = [f"Ripiano {i}" for i in range(st.session_state.ripiani, 0, -1)]
    df_visivo = pd.DataFrame(righe_tabella, index=indici_verticali)
    
    # Stampa la tabella HTML stilizzata sulla pagina web
    st.dataframe(df_visivo, use_container_width=True)
    
    # --- CALCOLO DEI PESI REPORT ---
    peso_singolo_scaffale = 0.0
    for riga in st.session_state.matrice_dati:
        for cella in riga:
            peso_singolo_scaffale += cella[1]
            
    peso_tutti_scaffali_merce = peso_singolo_scaffale * num_scaffali_totali
    tara_totale = tara_singolo_scaffale * num_scaffali_totali
    peso_complessivo_finale = peso_tutti_scaffali_merce + tara_totale
    
    st.markdown("---")
    st.header("📊 Report Calcolo Pesi Complessivi")
    
    # Visualizzazione pulita tramite metriche web affiancate
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Peso Merce Singolo Scaffale", value=f"{peso_singolo_scaffale:,.1f} kg")
    col2.metric(label=f"Carico Totale Merce ({num_scaffali_totali} Scaffali)", value=f"{peso_tutti_scaffali_merce:,.1f} kg")
    
    # Box colorato per il peso complessivo finale di strutture + merci
    with col3:
        st.markdown(
            f"""
            <div style="background-color:#d4edda; padding:15px; border-radius:10px; border-left:5px solid #28a745;">
                <h5 style="margin:0; color:#155724;">PESO COMPLESSIVO FINALE</h5>
                <p style="margin:5px 0 0 0; font-size:24px; font-weight:bold; color:#155724;">{peso_complessivo_finale:,.1f} kg</p>
                <small style="color:#6c757d;">Inclusa tara strutture: {tara_totale} kg</small>
            </div>
            """, 
            unsafe_allow_html=True
        )

with tab_modifica:
    st.write("Seleziona il punto preciso dello scaffale per aggiornare il materiale stoccato:")
    
    # Layout a due colonne per scegliere le coordinate
    col_r, col_m = st.columns(2)
    with col_r:
        ripiano_scelto = st.selectbox("Seleziona Ripiano (Altezza)", list(range(1, st.session_state.ripiani + 1)), index=st.session_state.ripiani-1)
    with col_m:
        modulo_scelto = st.selectbox("Seleziona Modulo (Colonna)", list(range(1, st.session_state.moduli + 1)))
        
    # Indici reali della matrice in Python
    r_idx = ripiano_scelto - 1
    m_idx = modulo_scelto - 1
    
    # Recupera i dati attuali del punto selezionato
    tipo_att, peso_att = st.session_state.matrice_dati[r_idx][m_idx]
    
    st.markdown(f"**Modifica della cella corrente:** Ripiano `{ripiano_scelto}`, Modulo `{modulo_scelto}`")
    
    # Form web di inserimento dati
    with st.form("form_modifica"):
        nuovo_tipo = st.text_input("Tipologia di materiale / Categoria Libri", value=tipo_att)
        nuovo_peso = st.number_input("Peso stimato del materiale (kg)", min_value=0.0, value=float(peso_att), step=5.0)
        
        pulsante_salva = st.form_submit_button("Salva ed Elabora Modifiche")
        
        if pulsante_salva:
            # Aggiorna la memoria interna dello stato della pagina
            st.session_state.matrice_dati[r_idx][m_idx] = [nuovo_tipo, nuovo_peso]
            st.success(f"✓ Cella [{ripiano_scelto}, {modulo_scelto}] aggiornata con successo!")
            # Forza l'applicazione a rinfrescare lo schermo per aggiornare i calcoli nella prima scheda
            st.rerun
          
