import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import json

class Visualizer:
    def plot_waiting_times(self, results):
        times = [r["total_waiting_time"] for r in results]
        fig, ax = plt.subplots()
        sns.histplot(times, bins=20, kde=True, ax=ax)
        ax.set_title("Distribuição dos Tempos de Espera")
        ax.set_xlabel("Tempo Total (min)")
        ax.set_ylabel("Frequência")
        st.pyplot(fig)

    def plot_transition_probabilities(self, transition_probs, sectors):
        fig, ax = plt.subplots()
        sns.heatmap(transition_probs, annot=True, fmt=".2f", cmap="Blues", xticklabels=sectors, yticklabels=sectors, ax=ax)
        ax.set_title("Probabilidades de Transição")
        st.pyplot(fig)

    def plot_sankey_flow(self, results, sectors):
        labels = sectors + ["Saída"]
        source = []
        target = []
        value = []
        flow_counts = {}
        for r in results:
            path = r["sectors_visited"]
            for i in range(len(path) - 1):
                src = path[i]
                tgt = path[i + 1]
                key = (src, tgt)
                flow_counts[key] = flow_counts.get(key, 0) + 1
        for (src, tgt), count in flow_counts.items():
            src_idx = labels.index(src)
            tgt_idx = labels.index(tgt)
            source.append(src_idx)
            target.append(tgt_idx)
            value.append(count)
        fig = go.Figure(data=[go.Sankey(
            node=dict(label=labels),
            link=dict(source=source, target=target, value=value)
        )])
        fig.update_layout(title_text="Fluxo de Pacientes (Sankey)")
        st.plotly_chart(fig)

    def plot_doctor_occupation(self, doctor_usage):
        times = [t for t, _ in doctor_usage]
        usage = [u for _, u in doctor_usage]
        fig, ax = plt.subplots()
        ax.step(times, np.cumsum(usage), where="post")
        ax.set_title("Ocupação dos Médicos")
        ax.set_xlabel("Tempo (min)")
        ax.set_ylabel("Médicos Ocupados")
        st.pyplot(fig)

    def plot_sector_times(self, stats, sectors):
        sector_times = stats["avg_time_per_sector"]
        fig, ax = plt.subplots()
        sns.barplot(x=list(sector_times.values()), y=list(sector_times.keys()), ax=ax, palette="Blues")
        ax.set_title("Tempo Médio por Setor")
        ax.set_xlabel("Tempo (min)")
        ax.set_ylabel("Setor")
        st.pyplot(fig)

    def plot_normalized_probs(self, transition_probs, exit_probs, sectors):
        fig, ax = plt.subplots(figsize=(8, 6))
        data = np.array(transition_probs)
        exit_data = np.array(exit_probs).reshape(-1, 1)
        combined = np.hstack((data, exit_data))
        labels = sectors + ["Saída"]
        sns.heatmap(combined, annot=True, fmt=".3f", cmap="Blues", xticklabels=labels, yticklabels=sectors, ax=ax)
        ax.set_title("Probabilidades Normalizadas (Transição + Saída)")
        st.pyplot(fig)