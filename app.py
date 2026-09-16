import streamlit as st
import pandas as pd
from io import BytesIO

# Imports para geração de PDF com ReportLab
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lobato · Araújo · Alencar Advocacia",
    page_icon="⚖️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    .title-header { text-align: center; color: #d4af37; font-family: 'Georgia', serif; font-size: 28px; font-weight: bold; letter-spacing: 2px; }
    .subtitle-header { text-align: center; color: #8b949e; font-size: 13px; letter-spacing: 1px; margin-bottom: 25px; }
    .kpi-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center; }
    .kpi-title { font-size: 11px; font-weight: bold; color: #8b949e; text-transform: uppercase; }
    .kpi-value { font-size: 20px; font-weight: bold; color: #d4af37; font-family: 'Courier New', monospace; margin-top: 5px; }
    .stButton>button { background: linear-gradient(135deg, #d4af37 0%, #aa820a 100%); color: #000000 !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÕES DE SUPORTE
# -----------------------------------------------------------------------------
def fmt_moeda(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_pdf_balancete(df, totais):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1a2a3a'), alignment=1, spaceAfter=5)
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748b'), alignment=1, spaceAfter=15)

    elements.append(Paragraph("LOBATO · ARAÚJO · ALENCAR ADVOCACIA", title_style))
    elements.append(Paragraph("DEMONSTRATIVO E BALANCETE MENSAL DE HONORÁRIOS", subtitle_style))

    headers = ["Especificação", "Valor Bruto", "Imposto", "Parceiro", "Base Esc.", "Caixa (10%)", "Captador", "Renan", "Marcus", "Letícia"]
    table_data = [headers]

    for _, row in df.iterrows():
        table_data.append([
            str(row["Especificação"]),
            fmt_moeda(row["Valor Bruto"]),
            fmt_moeda(row["Imposto"]),
            fmt_moeda(row["Parceiro"]),
            fmt_moeda(row["Base Escritório"]),
            fmt_moeda(row["Caixa (10%)"]),
            str(row["Captador"]),
            fmt_moeda(row["Renan"]),
            fmt_moeda(row["Marcus"]),
            fmt_moeda(row["Letícia"])
        ])

    table_data.append([
        "TOTAIS CONSOLIDADOS",
        fmt_moeda(totais["bruto"]),
        fmt_moeda(totais["imposto"]),
        fmt_moeda(totais["parceiro"]),
        fmt_moeda(totais["base"]),
        fmt_moeda(totais["caixa"]),
        "-",
        fmt_moeda(totais["renan"]),
        fmt_moeda(totais["marcus"]),
        fmt_moeda(totais["leticia"])
    ])

    t = Table(table_data, colWidths=[160, 70, 60, 60, 70, 65, 60, 70, 70, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a2a3a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))

    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# CABEÇALHO DA TELA
# -----------------------------------------------------------------------------
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    try:
        st.image("logo_escritorio.jpeg", use_container_width=True)
    except:
        st.markdown('<div class="title-header">LOBATO · ARAÚJO · ALENCAR</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-header">A D V O C A C I A</div>', unsafe_allow_html=True)

if 'honorarios' not in st.session_state:
    st.session_state.honorarios = []

# -----------------------------------------------------------------------------
# FORMULÁRIO LATERAL DE CADASTRO
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📝 Novo Honorário")
with st.sidebar.form("form_honorario", clear_on_submit=True):
    especificacao = st.text_input("Especificação / Processo", placeholder="Ex: Sucumbência - Ação X")
    valor_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0, step=500.0, format="%.2f")
    pct_imposto = st.number_input("Impostos / Taxas (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
    pct_parceiro = st.number_input("Comissão Parceiro (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    parceiro = st.text_input("Nome do Parceiro", placeholder="Opção (Ex: Dr. Fulano)")
    captador = st.selectbox("Sócio Captador (20%)", ["Renan", "Marcus", "Letícia"])
    
    btn_salvar = st.form_submit_button("➕ Lançar e Calcular")

if btn_salvar:
    if valor_bruto > 0 and especificacao.strip() != "":
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
        st.sidebar.success("Lançamento adicionado com sucesso!")

# -----------------------------------------------------------------------------
# DASHBOARD E TABELA PRINCIPAL
# -----------------------------------------------------------------------------
if st.session_state.honorarios:
    df = pd.DataFrame(st.session_state.honorarios)
    
    tot_bruto = df["Valor Bruto"].sum()
    tot_imp = df["Imposto"].sum()
    tot_parc = df["Parceiro"].sum()
    tot_base = df["Base Escritório"].sum()
    tot_caixa = df["Caixa (10%)"].sum()
    tot_renan = df["Renan"].sum()
    tot_marcus = df["Marcus"].sum()
    tot_leticia = df["Letícia"].sum()

    totais_dict = {
        "bruto": tot_bruto, "imposto": tot_imp, "parceiro": tot_parc,
        "base": tot_base, "caixa": tot_caixa, "renan": tot_renan,
        "marcus": tot_marcus, "leticia": tot_leticia
    }

    # Cards KPI
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Faturamento Bruto</div><div class="kpi-value">{fmt_moeda(tot_bruto)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Base Líquida Escritório</div><div class="kpi-value">{fmt_moeda(tot_base)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Caixa Escritório (10%)</div><div class="kpi-value" style="color: #2ea043;">{fmt_moeda(tot_caixa)}</div></div>', unsafe_allow_html=True)
    with c4:
        pdf_file = gerar_pdf_balancete(df, totais_dict)
        st.download_button(
            label="📄 BAIXAR RELATÓRIO PDF",
            data=pdf_file,
            file_name="Balancete_Honorarios_Escritorio.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("### 📊 Balancete Detalhado do Mês")

    df_exibicao = df.copy()
    cols_moeda = ["Valor Bruto", "Imposto", "Parceiro", "Base Escritório", "Caixa (10%)", "Cota (1/3)", "Renan", "Marcus", "Letícia"]
    for col in cols_moeda:
        df_exibicao[col] = df_exibicao[col].apply(fmt_moeda)

    st.dataframe(df_exibicao, use_container_width=True)

    st.markdown("### 💰 Repasse Final por Sócio")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Renan</div><div class="kpi-value">{fmt_moeda(tot_renan)}</div></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Marcus</div><div class="kpi-value">{fmt_moeda(tot_marcus)}</div></div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Letícia</div><div class="kpi-value">{fmt_moeda(tot_leticia)}</div></div>', unsafe_allow_html=True)

    if st.button("🗑️ Limpar Lançamentos do Mês"):
        st.session_state.honorarios = []
        st.rerun()

else:
    st.info("Nenhum honorário cadastrado neste mês. Utilize o painel lateral à esquerda para realizar o primeiro lançamento.")
