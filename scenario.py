# scenario.py: Análise de cenários
import streamlit as st
import pandas as pd
import numpy as np
from models.hospital_sim import HospitalSimulator
import json
from models.markov_model import MarkovHospitalModel

class ScenarioPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def render(self):
        st.markdown("<h2 class='section-title'>🔍 Análise de Cenários</h2>", unsafe_allow_html=True)
        st.markdown("Simule cenários 'e se' para testar mudanças no hospital.")

        if "config" not in st.session_state:
            st.warning("Configure uma simulação na aba Planejador primeiro!")
            return

        config = st.session_state["config"].copy()
        st.subheader("Configurar Cenários")
        
        patient_factor = st.slider("Fator de Pacientes", 0.5, 2.0, 1.0)
        medicos_factor = st.slider("Fator de Médicos", 0.5, 2.0, 1.0)
        
        scenarios = [
            {"name": "Base", "patients": config["num_patients"], "medicos": config["medicos_disponiveis"]},
            {"name": "Mais Pacientes", "patients": int(config["num_patients"] * patient_factor), "medicos": config["medicos_disponiveis"]},
            {"name": "Menos Médicos", "patients": config["num_patients"], "medicos": int(config["medicos_disponiveis"] * medicos_factor)}
        ]
        
        if st.button("Simular Cenários", type="primary"):
            results = []
            with st.spinner("Simulando cenários..."):
                for scenario in scenarios:
                    config["num_patients"] = scenario["patients"]
                    config["medicos_disponiveis"] = max(1, scenario["medicos"])
                    markov_model = MarkovHospitalModel(config)
                    transition_probs = markov_model.compute_transitions()
                    simulator = HospitalSimulator(config, transition_probs)
                    sim_results, sim_stats = simulator.run_simulation()
                    avg_time = np.mean([r["total_waiting_time"] for r in sim_results])
                    results.append({
                        "Cenário": scenario["name"],
                        "Pacientes": scenario["patients"],
                        "Médicos": scenario["medicos"],
                        "Tempo Médio (min)": avg_time,
                        "Ocupação (%)": sim_stats["doctor_occupation"] * 100
                    })
                
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)