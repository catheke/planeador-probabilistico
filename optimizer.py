# optimizer.py: Otimização de recursos
import streamlit as st
from models.hospital_sim import HospitalSimulator
from models.markov_model import MarkovHospitalModel
import json
import pandas as pd

class OptimizerPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def render(self):
        st.markdown("<h2 class='section-title'>⚙️ Otimização de Recursos</h2>", unsafe_allow_html=True)
        st.markdown("Teste diferentes alocações de médicos e setores para reduzir gargalos.")

        if "config" not in st.session_state:
            st.warning("Configure uma simulação na aba Planejador primeiro!")
            return

        config = st.session_state["config"].copy()
        st.subheader("Cenários de Otimização")
        
        medicos_range = st.slider("Faixa de Médicos", 1, 20, (config["medicos_disponiveis"], config["medicos_disponiveis"]+5))
        results = []
        
        if st.button("Testar Cenários", type="primary"):
            with st.spinner("Otimizando..."):
                for medicos in range(medicos_range[0], medicos_range[1]+1):
                    config["medicos_disponiveis"] = medicos
                    markov_model = MarkovHospitalModel(config)
                    transition_probs = markov_model.compute_transitions()
                    simulator = HospitalSimulator(config, transition_probs)
                    sim_results, sim_stats = simulator.run_simulation()
                    avg_time = sum(r["total_waiting_time"] for r in sim_results) / len(sim_results)
                    results.append({
                        "Médicos": medicos,
                        "Tempo Médio (min)": avg_time,
                        "Ocupação (%)": sim_stats["doctor_occupation"] * 100
                    })
                
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                best_scenario = df.loc[df["Tempo Médio (min)"].idxmin()]
                st.success(f"Melhor cenário: {best_scenario['Médicos']} médicos, Tempo Médio: {best_scenario['Tempo Médio (min)']:.2f} min, Ocupação: {best_scenario['Ocupação (%)']:.2f}%")