import streamlit as st
import pandas as pd
import numpy as np
from utils.visualizer import Visualizer
import plotly.graph_objects as go
import plotly.express as px

class DashboardPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.visualizer = Visualizer()

    def render(self):
        st.markdown("<h2 class='section-title'>📊 Dashboard de Métricas</h2>", unsafe_allow_html=True)
        st.markdown("Resumo visual das simulações com indicadores-chave de desempenho (KPIs).")

        if "results" not in st.session_state or "stats" not in st.session_state:
            st.warning("Execute ou carregue uma simulação na aba Planejador primeiro!")
            return

        results = st.session_state["results"]
        stats = st.session_state["stats"]
        config = st.session_state["config"]

        # KPIs
        st.subheader("🔑 Indicadores-Chave")
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_time = np.mean([r["total_waiting_time"] for r in results])
            st.metric("Tempo Médio Total", f"{avg_time:.2f} min")
        with col2:
            max_wait_sector = max(stats["avg_time_per_sector"], key=stats["avg_time_per_sector"].get)
            st.metric("Setor Mais Congestionado", f"{max_wait_sector} ({stats['avg_time_per_sector'][max_wait_sector]:.2f} min)")
        with col3:
            st.metric("Ocupação dos Médicos", f"{stats['doctor_occupation']:.2%}")

        # Fluxo de pacientes
        st.subheader("🌐 Fluxo de Pacientes")

        # Criar matriz de fluxos
        sectors = config["sectors"]  # Ex.: ["Triagem", "Consulta", "Exames"]
        flows = np.zeros((len(sectors), len(sectors)))
        valid_transitions = 0

        for r in results:
            path = r.get("sectors_visited", [])
            if len(path) < 2:
                continue
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]
                if source in sectors and target in sectors:
                    source_idx = sectors.index(source)
                    target_idx = sectors.index(target)
                    flows[source_idx, target_idx] += 1
                    valid_transitions += 1

        # Exibir matriz de fluxos como tabela
        flows_df = pd.DataFrame(flows, index=sectors, columns=sectors)
        with st.expander("Ver Matriz de Fluxos"):
            st.write("Número de transições entre setores:")
            st.dataframe(flows_df, use_container_width=True)
            st.write(f"Total de transições válidas: {valid_transitions}")

        # Verificar se há dados para a visualização
        if flows.max() == 0:
            st.warning("Nenhum fluxo de pacientes registrado. Verifique os dados da simulação.")
            return

        # Gráfico de Sankey
        st.subheader("Diagrama de Fluxo")
        node_labels = sectors
        source_indices = []
        target_indices = []
        values = []
        for i in range(len(sectors)):
            for j in range(len(sectors)):
                if flows[i, j] > 0:
                    source_indices.append(i)
                    target_indices.append(j)
                    values.append(flows[i, j])

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=["#1f77b4", "#ff7f0e", "#2ca02c"]  # Cores para Triagem, Consulta, Exames
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color="rgba(100, 149, 237, 0.5)"  # Links azuis semi-transparentes
            )
        )])
        fig_sankey.update_layout(
            title_text="Fluxo de Pacientes entre Setores",
            font_size=12,
            height=400,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_sankey, use_container_width=True)

        # Gráfico de barras: Tempo médio por setor
        st.subheader("Tempo Médio por Setor")
        sector_times = stats["avg_time_per_sector"]
        bar_data = pd.DataFrame({
            "Setor": list(sector_times.keys()),
            "Tempo Médio (min)": list(sector_times.values())
        })
        fig_bar = px.bar(
            bar_data,
            x="Setor",
            y="Tempo Médio (min)",
            color="Setor",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            title="Tempo Médio de Atendimento por Setor"
        )
        fig_bar.update_layout(
            height=350,
            showlegend=False,
            xaxis_tickangle=45,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_bar, use_container_width=True)