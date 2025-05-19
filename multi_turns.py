# multi_turns.py: Simulação multi-turnos
import streamlit as st
import pandas as pd
from models.hospital_sim import HospitalSimulator
from models.markov_model import MarkovHospitalModel
from utils.visualizer import Visualizer
import json
import numpy as np

class MultiTurnsPage:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.visualizer = Visualizer()

    def render(self):
        st.markdown("<h2 class='section-title'>🌞 Simulação Multi-Turnos</h2>", unsafe_allow_html=True)
        st.markdown("Compare o desempenho do hospital em diferentes turnos (manhã, tarde, noite).")

        if "config" not in st.session_state:
            st.warning("Configure uma simulação na aba Planejador primeiro!")
            return

        config = st.session_state["config"].copy()
        turnos = ["manhã", "tarde", "noite"]
        results_by_turno = {}

        if st.button("Simular Turnos", type="primary"):
            with st.spinner("Simulando turnos..."):
                for turno in turnos:
                    config["turno"] = turno
                    markov_model = MarkovHospitalModel(config)
                    transition_probs = markov_model.compute_transitions()
                    simulator = HospitalSimulator(config, transition_probs)
                    results, stats = simulator.run_simulation()
                    results_by_turno[turno] = {"results": results, "stats": stats}

                # Comparação
                st.subheader("Comparação por Turno")
                df = pd.DataFrame([
                    {
                        "Turno": turno,
                        "Tempo Médio (min)": np.mean([r["total_waiting_time"] for r in data["results"]]),
                        "Ocupação Médicos (%)": data["stats"]["doctor_occupation"] * 100
                    }
                    for turno, data in results_by_turno.items()
                ])
                st.dataframe(df, use_container_width=True)

                # Gráfico comparativo
                chart_data = {
                    "labels": turnos,
                    "datasets": [
                        {
                            "label": "Tempo Médio (min)",
                            "data": [np.mean([r["total_waiting_time"] for r in data["results"]]) for data in results_by_turno.values()],
                            "backgroundColor": "rgba(75, 192, 192, 0.5)"
                        },
                        {
                            "label": "Ocupação Médicos (%)",
                            "data": [data["stats"]["doctor_occupation"] * 100 for data in results_by_turno.values()],
                            "backgroundColor": "rgba(255, 99, 132, 0.5)"
                        }
                    ]
                }

                st.components.v1.html(f"""
                    <canvas id="turnosChart"></canvas>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2"></script>
                    <script>
                        const ctx = document.getElementById('turnosChart').getContext('2d');
                        new Chart(ctx, {{
                            type: 'bar',
                            data: {json.dumps(chart_data)},
                            options: {{
                                scales: {{ y: {{ beginAtZero: true }} }},
                                plugins: {{ legend: {{ display: true }} }}
                            }}
                        }});
                    </script>
                """, height=400)