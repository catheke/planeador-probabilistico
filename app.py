# app.py: Ponto de entrada da aplicação Streamlit
import streamlit as st
from templates.home import HomePage
from templates.concepts import ConceptsPage
from templates.dashboard import DashboardPage
from templates.optimizer import OptimizerPage
from templates.multi_turns import MultiTurnsPage
from templates.history import HistoryPage
from templates.scenario import ScenarioPage
from templates.pathways import PathwaysPage
from utils.data_manager import DataManager

def main():
    """Função principal da aplicação."""
    st.set_page_config(page_title="Planejador Hospitalar do Lubango", page_icon="🏥", layout="wide")
    
    # Carregar CSS personalizado
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Dark mode toggle
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    dark_mode = st.sidebar.checkbox("Modo Escuro", value=st.session_state["dark_mode"])
    st.session_state["dark_mode"] = dark_mode
    if dark_mode:
        st.markdown("<style>body { background-color: #1e1e1e; color: #e0e0e0; }</style>", unsafe_allow_html=True)
    
    # Welcome banner
    st.markdown("""
        <div class='banner'>
            <h1 class='title'>🏥 Planejador Hospitalar do Lubango</h1>
            <p>Simule, otimize e visualize o atendimento no hospital do Lubango com tecnologia avançada!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Inicializar gerenciador de dados
    data_manager = DataManager()
    
    # Navegação com abas
    tabs = st.tabs([
        "🛠️ Planejador",
        "📊 Dashboard",
        "⚙️ Otimização",
        "🌞 Multi-Turnos",
        "📜 Histórico",
        "🔍 Cenários",
        "🛤️ Caminhos",
        "📚 Conceitos"
    ])
    
    with tabs[0]:
        HomePage(data_manager).render()
    with tabs[1]:
        DashboardPage(data_manager).render()
    with tabs[2]:
        OptimizerPage(data_manager).render()
    with tabs[3]:
        MultiTurnsPage(data_manager).render()
    with tabs[4]:
        HistoryPage(data_manager).render()
    with tabs[5]:
        ScenarioPage(data_manager).render()
    with tabs[6]:
        PathwaysPage(data_manager).render()
    with tabs[7]:
        ConceptsPage().render()

if __name__ == "__main__":
    main()