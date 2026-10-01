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

def recalar_item(item):
    val_bruto = item["Valor Bruto"]
    pct_parc = item["Parceiro (%)"]
    captador = item["Captador"]
    
    val_parc = val_bruto * (pct_parc / 100.0)
    base_esc = val_bruto - val_parc
    caixa = base_esc * 0.10
    captacao = base_esc * 0.20
    saldo_div = base_esc * 0.70
    cota = saldo_div / 3.0
    
    return {
        "Especificação": item["Especificação"],
        "Valor Bruto": val_bruto,
        "Parceiro (%)": pct_parc,
        "Nome Parceiro": item.get("Nome Parceiro", ""),
        "Valor Parceiro": val_parc,
        "Base Escritório": base_esc,
        "Caixa (10%)": caixa,
        "Captador": captador,
        "Cota (1/3)": cota,
        "Renan": cota + (captacao if captador == "Renan" else 0.0),
        "Marcus": cota + (captacao if captador == "Marcus" else 0.0),
        "Letícia": cota + (captacao if captador == "Letícia" else 0.0)
    }

def gerar_pdf_balancete(df, totais):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1a2a3a'), alignment=1, spaceAfter=5)
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748b'), alignment=1, spaceAfter=15)

    elements.append(Paragraph("LOBATO · ARAÚJO · ALENCAR ADVOCACIA", title_style))
    elements.append(Paragraph("DEMONSTRATIVO E BALANCETE MENSAL DE HONORÁRIOS", subtitle_style))

    headers = ["Especificação", "Valor Bruto", "Parceiro", "Base Esc.", "Caixa (10%)", "Captador", "Renan", "Marcus", "Letícia"]
    table_data = [headers]

    for _, row in df.iterrows():
        table_data.append([
            str(row["Especificação"]),
            fmt_moeda(row["Valor Bruto"]),
            fmt_moeda(row["Valor Parceiro"]),
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
        fmt_moeda(totais["parceiro"]),
        fmt_moeda(totais["base"]),
        fmt_moeda(totais["caixa"]),
        "-",
        fmt_moeda(totais["renan"]),
        fmt_moeda(totais["marcus"]),
        fmt_moeda(totais["leticia"])
    ])

    t = Table(table_data, colWidths=[180, 75, 75, 75, 70, 65, 75, 75, 75])
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

if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# -----------------------------------------------------------------------------
# FORMULÁRIO LATERAL DE CADASTRO / EDIÇÃO
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📝 Lançar / Editar Honorário")

is_editing = st.session_state.edit_index is not None
if is_editing:
    item_edit = st.session_state.honorarios[st.session_state.edit_index]
    default_esp = item_edit["Especificação"]
    default_val = float(item_edit["Valor Bruto"])
    default_parc_pct = float(item_edit["Parceiro (%)"])
    default_parc_nome = item_edit.get("Nome Parceiro", "")
    default_capt = item_edit["Captador"]
    st.sidebar.info(f"✏️ Editando Lançamento #{st.session_state.edit_index + 1}")
else:
    default_esp = ""
    default_val = 0.0
    default_parc_pct = 0.0
    default_parc_nome = ""
    default_capt = "Renan"

with st.sidebar.form("form_honorario"):
    especificacao = st.text_input("Especificação / Processo", value=default_esp, placeholder="Ex: Sucumbência - Ação X")
    valor_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0, value=default_val, step=500.0, format="%.2f")
    pct_parceiro = st.number_input("Comissão Parceiro (%)", min_value=0.0, max_value=100.0, value=default_parc_pct, step=1.0)
    nome_parceiro = st.text_input("Nome do Parceiro", value=default_parc_nome, placeholder="Opção (Ex: Dr. Fulano)")
    
    captador_opts = ["Renan", "Marcus", "Letícia"]
    capt_idx = captador_opts.index(default_capt) if default_capt in captador_opts else 0
    captador = st.selectbox("Sócio Captador (20%)", captador_opts, index=capt_idx)
    
    btn_label = "💾 Salvar Alterações" if is_editing else "➕ Lançar Honorário"
    btn_salvar = st.form_submit_button(btn_label)

if is_editing:
    if st.sidebar.button("❌ Cancelar Edição"):
        st.session_state.edit_index = None
        st.rerun()

if btn_salvar:
    if valor_bruto > 0 and especificacao.strip() != "":
        novo_item = {
            "Especificação": especificacao,
            "Valor Bruto": valor_bruto,
            "Parceiro (%)": pct_parceiro,
            "Nome Parceiro": nome_parceiro,
            "Captador": captador
        }
        item_calculado = recalar_item(novo_item)
        
        if is_editing:
            st.session_state.honorarios[st.session_state.edit_index] = item_calculado
            st.session_state.edit_index = None
            st.sidebar.success("Lançamento atualizado com sucesso!")
        else:
            st.session_state.honorarios.append(item_calculado)
            st.sidebar.success("Lançamento adicionado com sucesso!")
        st.rerun()
    else:
        st.sidebar.error("Informe a especificação e um valor bruto maior que zero.")

# -----------------------------------------------------------------------------
# DASHBOARD E CONFERÊNCIA/EDIÇÃO DOS LANÇAMENTOS
# -----------------------------------------------------------------------------
if st.session_state.honorarios:
    df = pd.DataFrame(st.session_state.honorarios)
    
    tot_bruto = df["Valor Bruto"].sum()
    tot_parc = df["Valor Parceiro"].sum()
    tot_base = df["Base Escritório"].sum()
    tot_caixa = df["Caixa (10%)"].sum()
    tot_renan = df["Renan"].sum()
    tot_marcus = df["Marcus"].sum()
    tot_leticia = df["Letícia"].sum()

    totais_dict = {
        "bruto": tot_bruto, "parceiro": tot_parc,
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
            label="📄 BAIXAR RELATÓRIO PDF (FINAL)",
            data=pdf_file,
            file_name="Balancete_Honorarios_Escritorio.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("### 📊 Balancete do Mês (Conferência e Ajustes)")
    st.caption("Passe o olho na lista abaixo. Caso identifique qualquer erro em algum lançamento, clique em **Editar** ou **Excluir** ao lado da linha correspondente.")

    for idx, row in df.iterrows():
        col_info, col_b1, col_b2 = st.columns([8, 1, 1])
        with col_info:
            text_lin = f"**#{idx+1} - {row['Especificação']}** | Bruto: **{fmt_moeda(row['Valor Bruto'])}** | Parc: {fmt_moeda(row['Valor Parceiro'])} ({row['Parceiro (%)']}%) | Base: **{fmt_moeda(row['Base Escritório'])}** | Caixa: {fmt_moeda(row['Caixa (10%)'])} | Captador: **{row['Captador']}**"
            st.markdown(text_lin)
        with col_b1:
            if st.button("✏️ Editar", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
                st.rerun()
        with col_b2:
            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                st.session_state.honorarios.pop(idx)
                if st.session_state.edit_index == idx:
                    st.session_state.edit_index = None
                st.rerun()

    st.markdown("---")

    st.markdown("### 📋 Visão Completa em Tabela")
    df_exibicao = df.copy()
    cols_moeda = ["Valor Bruto", "Valor Parceiro", "Base Escritório", "Caixa (10%)", "Cota (1/3)", "Renan", "Marcus", "Letícia"]
    for col in cols_moeda:
        df_exibicao[col] = df_exibicao[col].apply(fmt_moeda)

    st.dataframe(df_exibicao[["Especificação", "Valor Bruto", "Valor Parceiro", "Base Escritório", "Caixa (10%)", "Captador", "Renan", "Marcus", "Letícia"]], use_container_width=True)

    st.markdown("### 💰 Repasse Final por Sócio no Mês")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Renan</div><div class="kpi-value">{fmt_moeda(tot_renan)}</div></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Marcus</div><div class="kpi-value">{fmt_moeda(tot_marcus)}</div></div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Letícia</div><div class="kpi-value">{fmt_moeda(tot_leticia)}</div></div>', unsafe_allow_html=True)

    if st.button("🗑️ Limpar Todos os Lançamentos"):
        st.session_state.honorarios = []
        st.session_state.edit_index = None
        st.rerun()

else:
    st.info("Nenhum honorário cadastrado neste mês. Utilize o painel lateral à esquerda para realizar o primeiro lançamento.")
