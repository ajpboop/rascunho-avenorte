import streamlit as st

# Configuração da página (deve ser a primeira linha de comando do Streamlit)
st.set_page_config(
    page_title="Painel FV vs Subestações", page_icon="⚡", layout="centered"
)

# Banco de dados simulado (Distâncias em metros e compatibilidade)
dados_projeto = {
    "SE 1": {
        "Arranjo 1": {"distancia": 145, "suporta": True},
        "Arranjo 2": {"distancia": 230, "suporta": False},
        "Arranjo 3": {"distancia": 310, "suporta": True},
        "Arranjo 4": {"distancia": 95, "suporta": True},
        "Arranjo 5": {"distancia": 420, "suporta": False},
        "Arranjo 6": {"distancia": 180, "suporta": True},
    },
    "SE 2": {
        "Arranjo 1": {"distancia": 210, "suporta": True},
        "Arranjo 2": {"distancia": 115, "suporta": True},
        "Arranjo 3": {"distancia": 280, "suporta": False},
        "Arranjo 4": {"distancia": 350, "suporta": True},
        "Arranjo 5": {"distancia": 190, "suporta": True},
        "Arranjo 6": {"distancia": 240, "suporta": False},
    },
    "SE 3": {
        "Arranjo 1": {"distancia": 320, "suporta": False},
        "Arranjo 2": {"distancia": 190, "suporta": True},
        "Arranjo 3": {"distancia": 120, "suporta": True},
        "Arranjo 4": {"distancia": 210, "suporta": True},
        "Arranjo 5": {"distancia": 85, "suporta": True},
        "Arranjo 6": {"distancia": 300, "suporta": False},
    },
    "SE 4": {
        "Arranjo 1": {"distancia": 90, "suporta": True},
        "Arranjo 2": {"distancia": 250, "suporta": True},
        "Arranjo 3": {"distancia": 340, "suporta": False},
        "Arranjo 4": {"distancia": 160, "suporta": True},
        "Arranjo 5": {"distancia": 210, "suporta": True},
        "Arranjo 6": {"distancia": 110, "suporta": True},
    },
    "SE 5": {
        "Arranjo 1": {"distancia": 270, "suporta": True},
        "Arranjo 2": {"distancia": 180, "suporta": False},
        "Arranjo 3": {"distancia": 95, "suporta": True},
        "Arranjo 4": {"distancia": 310, "suporta": False},
        "Arranjo 5": {"distancia": 140, "suporta": True},
        "Arranjo 6": {"distancia": 220, "suporta": True},
    },
    "SE 6": {
        "Arranjo 1": {"distancia": 150, "suporta": True},
        "Arranjo 2": {"distancia": 130, "suporta": True},
        "Arranjo 3": {"distancia": 220, "suporta": True},
        "Arranjo 4": {"distancia": 290, "suporta": False},
        "Arranjo 5": {"distancia": 310, "suporta": False},
        "Arranjo 6": {"distancia": 95, "suporta": True},
    },
    "SE 7": {
        "Arranjo 1": {"distancia": 380, "suporta": False},
        "Arranjo 2": {"distancia": 210, "suporta": True},
        "Arranjo 3": {"distancia": 170, "suporta": True},
        "Arranjo 4": {"distancia": 125, "suporta": True},
        "Arranjo 5": {"distancia": 240, "suporta": True},
        "Arranjo 6": {"distancia": 195, "suporta": False},
    },
    "SE 8": {
        "Arranjo 1": {"distancia": 110, "suporta": True},
        "Arranjo 2": {"distancia": 295, "suporta": False},
        "Arranjo 3": {"distancia": 205, "suporta": True},
        "Arranjo 4": {"distancia": 180, "suporta": True},
        "Arranjo 5": {"distancia": 90, "suporta": True},
        "Arranjo 6": {"distancia": 260, "suporta": True},
    },
}

st.title("⚡ Painel de Análise")
st.subheader("Arranjos FV vs Subestações")

st.markdown("---")

# Seletores
subestacao_selecionada = st.selectbox(
    "Selecione a Subestação:", list(dados_projeto.keys())
)
arranjo_selecionado = st.selectbox(
    "Selecione o Arranjo FV:",
    list(dados_projeto[subestacao_selecionada].keys()),
)

# Botão de consulta
if st.button("Consultar Ligação", type="primary", use_container_width=True):
    info = dados_projeto[subestacao_selecionada][arranjo_selecionado]

    st.markdown("### 📊 Resultado da Análise")

    # Exibindo métricas lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Distância Calculada", value=f"{info['distancia']} metros"
        )

    with col2:
        if info["suporta"]:
            st.success("Transformador: Suporta (OK)")
        else:
            st.error("Transformador: Não Suporta (Sobrecarga)")
