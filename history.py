import streamlit as st
import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class HistoryPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.sessions_dir = "sessions"

    def render(self):
        st.markdown("<h2 class='section-title'>📜 Histórico de Sessões</h2>", unsafe_allow_html=True)
        st.markdown("Compare e analise sessões salvas anteriormente.")

        # Listar sessões salvas
        saved_sessions = [f.replace(".json", "") for f in os.listdir(self.sessions_dir) if f.endswith(".json")]
        if not saved_sessions:
            st.warning("Nenhuma sessão salva encontrada.")
            return

        # Seleção de sessões
        st.subheader("Selecionar Sessões")
        selected_sessions = st.multiselect("Escolha até 3 sessões", saved_sessions, max_selections=3)
        
        if selected_sessions and st.button("Comparar Sessões", type="primary"):
            comparison = []
            heatmap_data = []  # Para o mapa de calor 3D
            sectors = set()    # Conjunto de todos os setores

            # Carregar dados das sessões selecionadas
            for session in selected_sessions:
                session_data = self.load_session(session)
                if session_data:
                    results = session_data["results"]
                    stats = session_data["stats"]
                    
                    # Adicionar dados à tabela de comparação
                    comparison.append({
                        "Sessão": session,
                        "Pacientes": len(results),
                        "Tempo Médio (min)": np.mean([r["total_waiting_time"] for r in results]),
                        "Ocupação Médicos (%)": stats["doctor_occupation"] * 100,
                        "Setor Mais Congestionado": max(stats["avg_time_per_sector"], key=stats["avg_time_per_sector"].get)
                    })

                    # Preparar dados para o mapa de calor
                    sector_times = stats["avg_time_per_sector"]  # Dicionário {setor: tempo}
                    sectors.update(sector_times.keys())  # Adicionar setores ao conjunto
                    heatmap_data.append({
                        "session": session,
                        "times": sector_times
                    })

            # Exibir tabela de comparação
            df = pd.DataFrame(comparison)
            st.dataframe(df, use_container_width=True)

            # Criar mapa de calor 3D
            if heatmap_data:
                st.subheader("Mapa de Calor 3D: Tempos Médios por Setor")
                
                # Organizar dados para o mapa de calor
                sectors = sorted(sectors)  # Lista ordenada de setores
                z_data = []  # Matriz para valores z (tempos)
                for data in heatmap_data:
                    session_times = [data["times"].get(sector, 0) for sector in sectors]  # Preencher com 0 se setor ausente
                    z_data.append(session_times)
                
                # Verificar se há dados suficientes
                if not z_data or not sectors:
                    st.warning("Dados insuficientes para gerar o mapa de calor 3D.")
                    return

                # Criar o mapa de calor 3D com Plotly
                fig = go.Figure(data=[
                    go.Surface(
                        x=sectors,  # Eixo x: Setores
                        y=selected_sessions,  # Eixo y: Sessões
                        z=z_data,  # Eixo z: Tempos médios
                        colorscale="Viridis",  # Escala de cores
                        showscale=True  # Mostrar barra de cores
                    )
                ])

                # Configurar layout
                fig.update_layout(
                    title="Tempos Médios por Setor nas Sessões Selecionadas",
                    scene=dict(
                        xaxis_title="Setores",
                        yaxis_title="Sessões",
                        zaxis_title="Tempo Médio (min)",
                        xaxis=dict(tickangle=45),
                    ),
                    height=600
                )

                # Renderizar o mapa de calor no Streamlit
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nenhum dado disponível para o mapa de calor 3D.")

    def load_session(self, session_name):
        session_path = os.path.join(self.sessions_dir, f"{session_name}.json")
        if os.path.exists(session_path):
            with open(session_path, "r") as f:
                return json.load(f)
        return None