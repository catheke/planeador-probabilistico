import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

class PathwaysPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def render(self):
        st.markdown("<h2 class='section-title'>🛤️ Caminhos de Pacientes</h2>", unsafe_allow_html=True)
        st.markdown("Visualize os caminhos individuais dos pacientes pelos setores.")

        if "results" not in st.session_state:
            st.warning("Execute uma simulação na aba Planejador primeiro!")
            return

        results = st.session_state["results"]
        patient_id = st.selectbox("Selecione o Paciente", [r["patient_id"] for r in results], key="patient_select")
        patient_data = next(r for r in results if r["patient_id"] == patient_id)
        
        # Exibir informações do paciente
        st.subheader(f"Caminho do Paciente {patient_id}")
        st.write(f"**Tempo Total**: {patient_data['total_waiting_time']:.2f} min")
        st.write(f"**Prioridade**: {patient_data['priority']}")
        st.write(f"**Caminho**: {' -> '.join(patient_data['sectors_visited'])}")
        
        # Gráfico de Sankey
        st.markdown("**Fluxo do Paciente**")
        
        # Preparar dados para o Sankey
        sectors = patient_data["sectors_visited"]
        if not sectors:
            st.warning("Nenhum setor visitado registrado para este paciente.")
            return

        # Estimar duração por setor (dividir tempo total igualmente)
        total_time = patient_data["total_waiting_time"]
        time_per_sector = total_time / len(sectors) if len(sectors) > 0 else 0
        
        # Criar lista de nós únicos e índices
        unique_sectors = list(dict.fromkeys(sectors))  # Preserva ordem, remove duplicatas
        node_indices = {sector: idx for idx, sector in enumerate(unique_sectors)}
        
        # Preparar dados para o Sankey
        source = []
        target = []
        values = []
        link_labels = []
        for i in range(len(sectors) - 1):
            source_sector = sectors[i]
            target_sector = sectors[i + 1]
            source.append(node_indices[source_sector])
            target.append(node_indices[target_sector])
            values.append(time_per_sector)
            link_labels.append(f"{source_sector} -> {target_sector}: {time_per_sector:.2f} min")

        # Definir cores vibrantes para nós
        node_colors = {
            "Triagem": "#00BFFF",  # Azul neon
            "Consulta": "#FF4500",  # Laranja forte
            "Exames": "#32CD32",   # Verde lima
            "Saída": "#DC143C"     # Vermelho escuro
        }
        
        # Criar gráfico de Sankey
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=30,
                line=dict(color="black", width=2),
                label=unique_sectors,
                color=[node_colors.get(s, "#FFFFFF") for s in unique_sectors],
                hovertemplate="Setor: %{label}<extra></extra>"
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                color="rgba(255, 255, 255, 0.4)",  # Links brancos semi-transparentes
                label=link_labels,
                hovertemplate="%{label}<extra></extra>"
            )
        )])

        # Personalizar o layout
        fig.update_layout(
            title=f"Fluxo do Paciente {patient_id}",
            font=dict(size=14, color="white", family="Arial"),
            height=400,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor="#1C2526",  # Cinza muito escuro
            paper_bgcolor="#1C2526",
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )

        # Forçar tema escuro no Streamlit
        st.markdown(
            """
            <style>
            .stPlotlyChart { background-color: #1C2526 !important; }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(fig, use_container_width=True)