import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Lobato · Araújo · Alencar Advocacia",
    page_icon="⚖️",
    layout="wide"
)

# Estilo executivo Dark & Gold
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #f0f6fc; }
    .stApp { background-color: #0b0e14; }
    .title-header { text-align: center; color: #d4af37; font-family: 'Cinzel', serif; font-size: 26px; font-weight: bold; margin-bottom: 5px; }
    .subtitle-header { text-align: center; color: #8b949e; font-size: 14px; margin-bottom: 25px; }
    .stButton>button { background-color: #d4af37; color: #000; font-weight: bold; border-radius: 5px; border: none; }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho do Escritório
st.markdown('<div class="title-header">LOBATO · ARAÚJO · ALENCAR</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-header">A D V O C A C I A — SISTEMA DE BALANCETE E HONORÁRIOS</div>', unsafe_allow_html=True)

# Tentar exibir logo se existir
try:
    st.image("logo_escritorio.jpeg", use_container_width=True)
except:
    pass

# Memória temporária para guardar os honorários do mês
if 'honorarios' not in st.session_state:
    st.session_state.honorarios = []

# Formulário Simplificado
with st.form("form_honorario"):
    st.markdown("### 📝 Cadastro de Honorário")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        especificacao = st.text_input("Especificação do Honorário / Processo", placeholder="Ex: Honorários Sucumbenciais - Processo X")
        parceiro = st.text_input("Nome do Parceiro Indicador (se houver)", placeholder="Ex: Dr. Advogado Parceiro")
    with col2:
        valor_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0, step=100.0, format="%.2f")
        pct_imposto = st.number_input("Imposto / Taxas (%)", min_value=0.0, max_value=100.0, value=10.0)
        pct_parceiro = st.number_input("Comissão do Parceiro (%)", min_value=0.0, max_value=100.0, value=0.0)
        captador = st.selectbox("Sócio Captador", ["Renan", "Marcus", "Letícia"])
        
    btn_salvar = st.form_submit_button("Lançar e Calcular")

if btn_salvar and valor_bruto > 0:
    val_imp = valor_bruto * (pct_imposto / 100)
    pos_imp = valor_bruto - val_imp
    val_parc = pos_imp * (pct_parceiro / 100)
    base_esc = pos_imp - val_parc
    caixa = base_esc * 0.10
    captacao = base_esc * 0.20
    saldo_div = base_esc * 0.70
    cota = saldo_div / 3.0
    
    st.session_state.honorarios.append({
        "Especificação": especificacao,
        "Valor Bruto": valor_bruto,
        "Imposto": val_imp,
        "Parceiro": val_parc,
        "Base Escritório": base_esc,
        "Caixa (10%)": caixa,
        "Captador": captador,
        "Cota (1/3)": cota,
        "Renan": cota + (captacao if captador == "Renan" else 0.0),
        "Marcus": cota + (captacao if captador == "Marcus" else 0.0),
        "Letícia": cota + (captacao if captador == "Letícia" else 0.0)
    })
    st.success("Lançamento efetuado com sucesso!")

# Exibição do Balancete
if st.session_state.honorarios:
    df = pd.DataFrame(st.session_state.honorarios)
    st.markdown("---")
    st.markdown("### 📊 Balancete do Mês")
    st.dataframe(df, use_container_width=True)
