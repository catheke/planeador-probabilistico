import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from models.markov_model import MarkovHospitalModel
from models.hospital_sim import HospitalSimulator
from utils.visualizer import Visualizer
from utils.exporter import Exporter

class HomePage:
    def __init__(self, data_manager):
        """Inicializa a página com o gerenciador de dados."""
        self.data_manager = data_manager
        self.visualizer = Visualizer()
        self.exporter = Exporter()
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)

    def save_session(self, config, results, stats, session_name):
        session_data = {
            "config": config,
            "results": results,
            "stats": stats
        }
        session_path = os.path.join(self.sessions_dir, f"{session_name}.json")
        with open(session_path, "w") as f:
            json.dump(session_data, f, indent=2)
        return session_path

    def load_session(self, session_name):
        session_path = os.path.join(self.sessions_dir, f"{session_name}.json")
        if os.path.exists(session_path):
            with open(session_path, "r") as f:
                return json.load(f)
        return None

    def render(self):
        st.markdown("<h2 class='section-title'>🛠️ Planejador de Simulações</h2>", unsafe_allow_html=True)
        st.markdown("Configure e simule o fluxo de pacientes com visualizações interativas e relatórios detalhados.")

        # Gerenciamento de sessões
        st.sidebar.header("💾 Gerenciar Sessões")
        session_name = st.sidebar.text_input("Nome da Sessão", value="simulacao_1")
        if st.sidebar.button("Salvar Sessão"):
            if "results" in st.session_state and "stats" in st.session_state:
                self.save_session(st.session_state["config"], st.session_state["results"], st.session_state["stats"], session_name)
                st.sidebar.success(f"Sessão '{session_name}' salva!")
            else:
                st.sidebar.error("Execute uma simulação primeiro!")

        saved_sessions = [f.replace(".json", "") for f in os.listdir(self.sessions_dir) if f.endswith(".json")]
        selected_session = st.sidebar.selectbox("Carregar Sessão", [""] + saved_sessions)
        if selected_session and st.sidebar.button("Carregar"):
            session_data = self.load_session(selected_session)
            if session_data:
                st.session_state["config"] = session_data["config"]
                st.session_state["results"] = session_data["results"]
                st.session_state["stats"] = session_data["stats"]
                st.sidebar.success(f"Sessão '{selected_session}' carregada!")

        # Configurações
        st.sidebar.header("⚙️ Configurações")
        with st.sidebar.expander("Setores do Hospital", expanded=True):
            setores_input = st.text_area("Setores (um por linha)", value="Triagem\nConsulta\nExames")
            setores = [s.strip() for s in setores_input.split("\n") if s.strip()]
            if len(setores) < 2:
                st.sidebar.error("Insira pelo menos 2 setores.")
                return

        with st.sidebar.expander("Probabilidades de Transição"):
            transition_base = []
            for i, setor_origem in enumerate(setores):
                st.markdown(f"**De {setor_origem} para:**")
                probs = []
                cols = st.columns(len(setores))
                for j, setor_destino in enumerate(setores):
                    prob = cols[j].number_input(
                        f"{setor_destino}",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.3,
                        step=0.01,
                        key=f"prob_{i}_{j}"
                    )
                    probs.append(prob)
                transition_base.append(probs)

        with st.sidebar.expander("Probabilidade de Saída"):
            exit_probs = []
            for i, setor in enumerate(setores):
                prob = st.number_input(
                    f"Saída após {setor}",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.1,
                    step=0.01,
                    key=f"exit_prob_{i}"
                )
                exit_probs.append(prob)

        # Validação em tempo real
        prob_errors = []
        for i, probs in enumerate(transition_base):
            total_prob = sum(probs) + exit_probs[i]
            if abs(total_prob - 1.0) > 0.01:
                prob_errors.append(f"Probabilidades para {setores[i]} devem somar 1 (atual: {total_prob:.2f}).")
        if prob_errors:
            st.sidebar.error("\n".join(prob_errors))
            return

        with st.sidebar.expander("Parâmetros"):
            num_pacientes = st.slider("Pacientes", 1, 200, 20)
            turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite"])
            gravidade = st.selectbox("Gravidade", ["Baixa", "Média", "Alta"])
            medicos_disponiveis = st.slider("Médicos", 1, 30, 5)
            prioridade_ativa = st.checkbox("Prioridade", value=True)

        # Simulação com preview
        if st.button("▶️ Simular Atendimentos", type="primary"):
            config = {
                "sectors": setores,
                "transition_base": transition_base,
                "exit_probs": exit_probs,
                "num_patients": num_pacientes,
                "turno": turno.lower(),
                "gravidade": gravidade.lower(),
                "medicos_disponiveis": medicos_disponiveis,
                "prioridade_ativa": prioridade_ativa
            }

            progress_bar = st.progress(0)
            status_text = st.empty()
            markov_model = MarkovHospitalModel(config)
            try:
                transition_probs = markov_model.compute_transitions()
                config["transition_probs"] = transition_probs.tolist()
            except Exception as e:
                st.error(f"Erro ao calcular probabilidades: {e}")
                return
            
            simulator = HospitalSimulator(config, transition_probs)
            try:
                results, stats = simulator.run_simulation()
                for i in range(100):
                    progress_bar.progress(i + 1)
                    status_text.text(f"Simulando... {i+1}%")
            except Exception as e:
                st.error(f"Erro durante a simulação: {e}")
                return
            status_text.text("Simulação concluída!")
            
            st.session_state["config"] = config
            st.session_state["results"] = results
            st.session_state["stats"] = stats

            # Resultados
            st.subheader("📊 Resultados")
            df_results = pd.DataFrame([
                {
                    "Paciente": r["patient_id"],
                    "Tempo Total (min)": f"{r['total_waiting_time']:.2f}",
                    "Setores Visitados": " -> ".join(r["sectors_visited"]),
                    "Prioridade": r["priority"]
                } for r in results
            ])

            # Filtros
            st.markdown("**Filtros**")
            priority_filter = st.selectbox("Prioridade", ["Todos", "Alta", "Normal"])
            sector_filter = st.selectbox("Setor", ["Todos"] + config["sectors"])
            time_filter = st.slider("Tempo Mínimo (min)", 0, int(max(df_results["Tempo Total (min)"].astype(float))), 0)

            filtered_df = df_results
            if priority_filter != "Todos":
                filtered_df = filtered_df[filtered_df["Prioridade"] == priority_filter]
            if sector_filter != "Todos":
                filtered_df = filtered_df[filtered_df["Setores Visitados"].str.contains(sector_filter)]
            filtered_df = filtered_df[filtered_df["Tempo Total (min)"].astype(float) >= time_filter]
            
            st.dataframe(filtered_df, use_container_width=True)

            # Gargalos
            st.subheader("🚨 Gargalos")
            max_wait_sector = max(stats["avg_time_per_sector"], key=stats["avg_time_per_sector"].get)
            st.warning(f"Setor mais lento: **{max_wait_sector}** ({stats['avg_time_per_sector'][max_wait_sector]:.2f} min)")
            st.write(f"Ocupação dos médicos: **{stats['doctor_occupation']:.2%}**")
            
            # Visualizações
            st.subheader("📈 Visualizações")
            st.info("Filtre o gráfico Sankey ou baixe os gráficos!")
            sankey_priority = st.selectbox("Filtrar Sankey por Prioridade", ["Todos", "Alta", "Normal"])
            filtered_results = results if sankey_priority == "Todos" else [r for r in results if r["priority"] == sankey_priority]
            self.visualizer.plot_waiting_times(results)
            self.visualizer.plot_transition_probabilities(transition_probs, config["sectors"])
            self.visualizer.plot_sankey_flow(filtered_results, config["sectors"])
            self.visualizer.plot_doctor_occupation(stats["doctor_usage"])
            self.visualizer.plot_sector_times(stats, config["sectors"])
            self.visualizer.plot_normalized_probs(config["transition_probs"], config["exit_probs"], config["sectors"])

            # Exportação
            st.subheader("📥 Exportar")
            csv_data = self.exporter.to_csv(results, stats)
            st.download_button("Baixar CSV", csv_data, "resultados.csv", "text/csv")
            pdf_data = self.exporter.to_pdf(results, transition_probs, stats, config)
            if pdf_data:
                st.download_button("Baixar Relatório PDF", pdf_data, "relatorio.pdf", "application/pdf")
            else:
                st.warning("Instale 'reportlab' para exportar PDF.")