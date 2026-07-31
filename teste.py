from dataclasses import dataclass, field
from typing import Dict, List, Optional
import plotly.graph_objects as go
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Painel FV vs Subestações", page_icon="⚡", layout="wide"
)

# ==========================================
# 1. MODELAGEM DE CLASSES E OBJETOS
# ==========================================


@dataclass
class ArranjoFV:
    nome: str
    potencia_pico_kwp: float  # Potência DC (módulos)
    potencia_ca_kw: float  # Potência AC (inversor)
    num_strings: int = 10  # Fixo por padrão

    @property
    def fdr(self) -> float:
        """Fator de Dimensionamento do Inversor (DC/AC)."""
        return (
            (self.potencia_pico_kwp / self.potencia_ca_kw)
            if self.potencia_ca_kw > 0
            else 0.0
        )


@dataclass
class Subestacao:
    nome: str
    num_transformadores: int
    potencia_total_kva: float  # Potência Nominal da SE (kVA / kW)
    arranjos_vinculados: List[str] = field(default_factory=list)

    def calcular_potencia_alocada(
        self, dicionario_arranjos: Dict[str, ArranjoFV]
    ) -> float:
        """Soma a potência CA (kW) de TODOS os arranjos conectados a esta SE."""
        total = 0.0
        for nome_arr in self.arranjos_vinculados:
            if nome_arr in dicionario_arranjos:
                total += dicionario_arranjos[nome_arr].potencia_ca_kw
        return total

    def verifica_suporte_global(
        self, dicionario_arranjos: Dict[str, ArranjoFV]
    ) -> bool:
        """Regra GLOBAL: Avalia se o somatório de kW dos arranjos vinculados não excede a capacidade da SE."""
        potencia_carregada = self.calcular_potencia_alocada(dicionario_arranjos)
        return potencia_carregada <= self.potencia_total_kva


# ==========================================
# 2. BANCO DE DADOS E ESTADO DA APLICAÇÃO
# ==========================================

# Coordenadas de Geolocalização (Ajuste para a sua localização real se desejar)
COORDENADAS = {
    # Subestações
    "SE 1": {"lat": -23.697401, "lon": -52.618086},
    "SE 2": {"lat": -23.699054, "lon": -52.616319},
    "SE 3": {"lat": -23.697263, "lon": -52.618407},
    "SE 4": {"lat": -23.697584, "lon": -52.618658},
    "SE 5": {"lat": -23.698702, "lon": -52.618521},
    "SE 6": {"lat": -23.699014, "lon": -52.616323},
    "SE 7": {"lat": -23.698566, "lon": -52.615919},
    "SE 8": {"lat": -23.699912, "lon": -52.616115},
    # Arranjos
    "Arranjo 1 (CP1)": {"lat": -23.696875, "lon": -52.618519},
    "Arranjo 2 (CP2)": {"lat": -23.696993, "lon": -52.618243},
    "Arranjo 3 (CP3)": {"lat": -23.696903, "lon": -52.618006},
    "Arranjo 4 (CP4)": {"lat": -23.696713, "lon": -52.616384},
    "Arranjo 5 (CP5)": {"lat": -23.697229, "lon": -52.616394},
    "Arranjo 6 (CP6)": {"lat": -23.697229, "lon": -52.616152},
}

# Distâncias Lineares (Matriz Arranjo x SE)
DADOS_DISTANCIAS = {
    "SE 1": {
        "Arranjo 1 (CP1)": 130,
        "Arranjo 2 (CP2)": 87,
        "Arranjo 3 (CP3)": 108,
        "Arranjo 4 (CP4)": 101,
        "Arranjo 5 (CP5)": 27,
        "Arranjo 6 (CP6)": 62,
    },
    "SE 2": {
        "Arranjo 1 (CP1)": 352,
        "Arranjo 2 (CP2)": 310,
        "Arranjo 3 (CP3)": 305,
        "Arranjo 4 (CP4)": 140,
        "Arranjo 5 (CP5)": 137,
        "Arranjo 6 (CP6)": 110,
    },
    "SE 3": {
        "Arranjo 1 (CP1)": 55,
        "Arranjo 2 (CP2)": 91,
        "Arranjo 3 (CP3)": 135,
        "Arranjo 4 (CP4)": 240,
        "Arranjo 5 (CP5)": 210,
        "Arranjo 6 (CP6)": 116,
    },
    "SE 4": {
        "Arranjo 1 (CP1)": 136,
        "Arranjo 2 (CP2)": 196,
        "Arranjo 3 (CP3)": 227,
        "Arranjo 4 (CP4)": 262,
        "Arranjo 5 (CP5)": 227,
        "Arranjo 6 (CP6)": 207,
    },
    "SE 5": {
        "Arranjo 1 (CP1)": 264,
        "Arranjo 2 (CP2)": 265,
        "Arranjo 3 (CP3)": 314,
        "Arranjo 4 (CP4)": 307,
        "Arranjo 5 (CP5)": 260,
        "Arranjo 6 (CP6)": 300,
    },
    "SE 6": {
        "Arranjo 1 (CP1)": 275,
        "Arranjo 2 (CP2)": 276,
        "Arranjo 3 (CP3)": 258,
        "Arranjo 4 (CP4)": 330,
        "Arranjo 5 (CP5)": 390,
        "Arranjo 6 (CP6)": 335,
    },
    "SE 7": {
        "Arranjo 1 (CP1)": 262,
        "Arranjo 2 (CP2)": 210,
        "Arranjo 3 (CP3)": 160,
        "Arranjo 4 (CP4)": 387,
        "Arranjo 5 (CP5)": 396,
        "Arranjo 6 (CP6)": 395,
    },
    "SE 8": {
        "Arranjo 1 (CP1)": 487,
        "Arranjo 2 (CP2)": 445,
        "Arranjo 3 (CP3)": 455,
        "Arranjo 4 (CP4)": 457,
        "Arranjo 5 (CP5)": 379,
        "Arranjo 6 (CP6)": 260,
    },
}

# Inicialização dos Arranjos/CPs
if "arranjos" not in st.session_state:
    st.session_state.arranjos = {
        "Arranjo 1 (CP1)": ArranjoFV(
            nome="Arranjo 1 (CP1)", potencia_pico_kwp=97.5, potencia_ca_kw=75.0
        ),
        "Arranjo 2 (CP2)": ArranjoFV(
            nome="Arranjo 2 (CP2)", potencia_pico_kwp=97.5, potencia_ca_kw=75.0
        ),
        "Arranjo 3 (CP3)": ArranjoFV(
            nome="Arranjo 3 (CP3)", potencia_pico_kwp=97.5, potencia_ca_kw=75.0
        ),
        "Arranjo 4 (CP4)": ArranjoFV(
            nome="Arranjo 4 (CP4)", potencia_pico_kwp=520.0, potencia_ca_kw=400.0
        ),
        "Arranjo 5 (CP5)": ArranjoFV(
            nome="Arranjo 5 (CP5)", potencia_pico_kwp=260.0, potencia_ca_kw=200.0
        ),
        "Arranjo 6 (CP6)": ArranjoFV(
            nome="Arranjo 6 (CP6)", potencia_pico_kwp=260.0, potencia_ca_kw=200.0
        ),
    }

if "subestacoes" not in st.session_state:
    st.session_state.subestacoes = {
        "SE 1": Subestacao(
            nome="SE 1", num_transformadores=3, potencia_total_kva=6000.0
        ),
        "SE 2": Subestacao(
            nome="SE 2", num_transformadores=2, potencia_total_kva=2000.0
        ),
        "SE 3": Subestacao(
            nome="SE 3", num_transformadores=2, potencia_total_kva=4000.0
        ),
        "SE 4": Subestacao(
            nome="SE 4", num_transformadores=1, potencia_total_kva=1500.0
        ),
        "SE 5": Subestacao(
            nome="SE 5", num_transformadores=1, potencia_total_kva=112.5
        ),
        "SE 6": Subestacao(
            nome="SE 6", num_transformadores=1, potencia_total_kva=1500.0
        ),
        "SE 7": Subestacao(
            nome="SE 7", num_transformadores=1, potencia_total_kva=75.0
        ),
        "SE 8": Subestacao(
            nome="SE 8", num_transformadores=1, potencia_total_kva=75.0
        ),
    }

if "vinculos" not in st.session_state:
    st.session_state.vinculos = {
        "Arranjo 1 (CP1)": "SE 1",
        "Arranjo 2 (CP2)": "SE 1",
        "Arranjo 3 (CP3)": "SE 2",
        "Arranjo 4 (CP4)": "SE 4",
        "Arranjo 5 (CP5)": "SE 5",
        "Arranjo 6 (CP6)": "SE 6",
    }


def sincronizar_vinculos():
    for se in st.session_state.subestacoes.values():
        se.arranjos_vinculados.clear()
    for arranjo, se_nome in st.session_state.vinculos.items():
        if se_nome and se_nome in st.session_state.subestacoes:
            st.session_state.subestacoes[se_nome].arranjos_vinculados.append(
                arranjo
            )


sincronizar_vinculos()

# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================

st.title("⚡ Gestão de Arranjos FV vs Subestações")
st.caption(
    "Dimensionamento técnico, atribuição de distâncias e análise de carregamento global."
)

tab1, tab2 = st.tabs(
    ["🔗 Vinculação & Diagnóstico", "📊 Dashboard & Mapa de Conexões"]
)

# -------------------------------------------------------------
# TAB 1: VINCULAÇÃO E DIAGNÓSTICO DE ARRANJOS
# -------------------------------------------------------------
with tab1:
    st.subheader("Configuração por Arranjo Fotovoltaico")

    col_arr, col_se = st.columns(2)

    with col_arr:
        arranjo_sel = st.selectbox(
            "Selecione o Arranjo FV:", list(st.session_state.arranjos.keys())
        )
        obj_arranjo = st.session_state.arranjos[arranjo_sel]

        m1, m2, m3 = st.columns(3)
        m1.metric("Potência DC (Módulos)", f"{obj_arranjo.potencia_pico_kwp} kWp")
        m2.metric("Potência AC (Inversor)", f"{obj_arranjo.potencia_ca_kw} kW")
        m3.metric("Nº de Strings", f"{obj_arranjo.num_strings} (Fixo)")

    with col_se:
        se_atual = st.session_state.vinculos.get(arranjo_sel, "Nenhuma")
        opcoes_se = ["Nenhuma"] + list(st.session_state.subestacoes.keys())

        se_selecionada = st.selectbox(
            "Vincular à Subestação:",
            opcoes_se,
            index=opcoes_se.index(se_atual) if se_atual in opcoes_se else 0,
        )

        if se_selecionada != se_atual:
            st.session_state.vinculos[arranjo_sel] = (
                se_selecionada if se_selecionada != "Nenhuma" else None
            )
            sincronizar_vinculos()
            st.rerun()

    st.divider()

    st.markdown("### 🔍 Análise Automática da Ligação")

    if se_selecionada == "Nenhuma" or not se_selecionada:
        st.info("⚠️ Este arranjo não está vinculado a nenhuma subestação.")
    else:
        obj_se = st.session_state.subestacoes[se_selecionada]

        distancia = DADOS_DISTANCIAS.get(se_selecionada, {}).get(
            arranjo_sel, "N/A"
        )
        carga_total_se = obj_se.calcular_potencia_alocada(
            st.session_state.arranjos
        )
        capacidade_se = obj_se.potencia_total_kva
        suporta_global = obj_se.verifica_suporte_global(
            st.session_state.arranjos
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                label="Distância Linear",
                value=f"{distancia} metros"
                if isinstance(distancia, (int, float))
                else distancia,
            )

        with c2:
            st.metric(
                label="Carregamento Total da SE",
                value=f"{carga_total_se:,.1f} kW",
                delta=f"Capacidade: {capacidade_se:,.1f} kVA",
                delta_color="off",
            )

        with c3:
            if suporta_global:
                st.success("✅ **Transformadores: Suportam**")
                st.caption(
                    f"A SE {se_selecionada} está com {(carga_total_se/capacidade_se)*100:.1f}% da capacidade alocada."
                )
            else:
                st.error("❌ **Transformadores: Sobrecarregados!**")
                st.caption(
                    f"Excesso de {carga_total_se - capacidade_se:,.1f} kW em relação ao limite nominal da SE."
                )

# -------------------------------------------------------------
# TAB 2: DASHBOARD E MAPA DE CONEXÕES
# -------------------------------------------------------------
with tab2:
    st.subheader("📊 Status de Carregamento Global por Subestação")

    rows = []
    for nome_se, se in st.session_state.subestacoes.items():
        carga = se.calcular_potencia_alocada(st.session_state.arranjos)
        cap = se.potencia_total_kva
        suporta = se.verifica_suporte_global(st.session_state.arranjos)
        arranjos_str = (
            ", ".join(se.arranjos_vinculados)
            if se.arranjos_vinculados
            else "Nenhum"
        )

        rows.append(
            {
                "Subestação": nome_se,
                "Nº de Transformadores": se.num_transformadores,
                "Capacidade Nominal (kVA)": cap,
                "Carga Alocada Total (kW)": carga,
                "Ocupação (%)": round((carga / cap) * 100, 1)
                if cap > 0
                else 0.0,
                "Arranjos Vinculados": arranjos_str,
                "Status Global": "🟢 OK (Suporta)"
                if suporta
                else "🔴 SOBRECARGA",
            }
        )

    st.dataframe(rows, use_container_width=True)

    st.divider()

    st.subheader("🗺️ Mapa do Arranjo Físico e Ligações (SE vs Arranjo)")

    # Criação do Mapa Plotly
    fig = go.Figure()

    # 1. Desenhar as Linhas de Conexão entre Arranjos e SEs
    for arranjo_nome, se_nome in st.session_state.vinculos.items():
        if (
            se_nome
            and arranjo_nome in COORDENADAS
            and se_nome in COORDENADAS
        ):
            pt_arr = COORDENADAS[arranjo_nome]
            pt_se = COORDENADAS[se_nome]

            fig.add_trace(
                go.Scattermapbox(
                    mode="lines",
                    lon=[pt_arr["lon"], pt_se["lon"]],
                    lat=[pt_arr["lat"], pt_se["lat"]],
                    line=dict(width=2, color="#1f77b4"),
                    hoverinfo="text",
                    text=f"Ligação: {arranjo_nome} ➔ {se_nome}",
                    showlegend=False,
                )
            )

    # 2. Adicionar Marcadores das Subestações (Vermelho)
    se_lats = [COORDENADAS[se]["lat"] for se in st.session_state.subestacoes if se in COORDENADAS]
    se_lons = [COORDENADAS[se]["lon"] for se in st.session_state.subestacoes if se in COORDENADAS]
    se_names = [se for se in st.session_state.subestacoes if se in COORDENADAS]

    fig.add_trace(
        go.Scattermapbox(
            mode="markers+text",
            lon=se_lons,
            lat=se_lats,
            marker=dict(size=14, color="red"),
            text=se_names,
            textposition="top center",
            name="Subestações (SE)",
        )
    )

    # 3. Adicionar Marcadores dos Arranjos (Verde)
    arr_lats = [COORDENADAS[arr]["lat"] for arr in st.session_state.arranjos if arr in COORDENADAS]
    arr_lons = [COORDENADAS[arr]["lon"] for arr in st.session_state.arranjos if arr in COORDENADAS]
    arr_names = [arr for arr in st.session_state.arranjos if arr in COORDENADAS]

    fig.add_trace(
        go.Scattermapbox(
            mode="markers+text",
            lon=arr_lons,
            lat=arr_lats,
            marker=dict(size=12, color="green"),
            text=arr_names,
            textposition="bottom center",
            name="Arranjos (CPs)",
        )
    )

    # Configuração do Layout do Mapa
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=-23.697238, lon=-52.616777),  # Centro inicial da visualização
            zoom=12.5,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=550,
    )

    st.plotly_chart(fig, use_container_width=True)
