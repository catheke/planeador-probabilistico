import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

class Exporter:
    def to_csv(self, results, stats):
        df = pd.DataFrame([
            {
                "Paciente": r["patient_id"],
                "Tempo Total (min)": r["total_waiting_time"],
                "Setores Visitados": " -> ".join(r["sectors_visited"]),
                "Prioridade": r["priority"]
            } for r in results
        ])
        return df.to_csv(index=False)

    def to_pdf(self, results, transition_probs, stats, config):
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph("Relatório de Simulação - Hospital do Lubango", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Resumo
            elements.append(Paragraph("Resumo da Simulação", styles['Heading2']))
            data = [
                ["Parâmetro", "Valor"],
                ["Pacientes", config["num_patients"]],
                ["Médicos", config["medicos_disponiveis"]],
                ["Turno", config["turno"].capitalize()],
                ["Gravidade", config["gravidade"].capitalize()],
                ["Ocupação Médicos", f"{stats['doctor_occupation']:.2%}"]
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Tempos por Setor
            elements.append(Paragraph("Tempos Médios por Setor", styles['Heading2']))
            data = [["Setor", "Tempo Médio (min)"]] + [
                [sector, f"{time:.2f}"] for sector, time in stats["avg_time_per_sector"].items()
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Gráfico de Probabilidades Normalizadas
            fig, ax = plt.subplots(figsize=(6, 4))
            data = np.array(config["transition_probs"])
            exit_data = np.array(config["exit_probs"]).reshape(-1, 1)
            combined = np.hstack((data, exit_data))
            labels = config["sectors"] + ["Saída"]
            sns.heatmap(combined, annot=True, fmt=".3f", cmap="Blues", xticklabels=labels, yticklabels=config["sectors"], ax=ax)
            ax.set_title("Probabilidades Normalizadas")
            fig.tight_layout()
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png", dpi=150)
            plt.close(fig)
            elements.append(Image(img_buffer, width=400, height=300))
            elements.append(Spacer(1, 12))
            
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            return None