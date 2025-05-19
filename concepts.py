# concepts.py: Página de conceitos para leigos
import streamlit as st
import json

class ConceptsPage:
    def render(self):
        """Renderiza a página de conceitos."""
        st.title("📚 Entenda os Conceitos")
        st.markdown("""
            Este sistema ajuda a planejar o atendimento no hospital do Lubango de forma inteligente. Aqui, explicamos os conceitos de forma simples para todos entenderem!
        """)

        with st.expander("O que é uma Cadeia de Markov?"):
            st.write("""
                Imagine pacientes passando por setores do hospital, como Triagem, Consulta e Exames. Uma **Cadeia de Markov** é um mapa que mostra a chance de um paciente ir de um setor para outro (ou sair do hospital). Por exemplo, após a Triagem, pode haver 60% de chance de ir para a Consulta. Isso ajuda a planejar o fluxo!
            """)
        
        with st.expander("O que é Incerteza Temporal?"):
            st.write("""
                No hospital, o tempo de espera varia. Uma Consulta pode levar 5 ou 20 minutos! **Incerteza temporal** significa usar matemática para prever esses tempos variáveis, tornando o planejamento mais realista.
            """)
        
        with st.expander("Como usamos o SimPy?"):
            st.write("""
                **SimPy** simula pacientes movendo-se pelos setores do hospital. Ele decide para onde cada paciente vai (baseado nas chances que você definiu) e quanto tempo espera, como se fosse um hospital real!
            """)
        
        with st.expander("O que é Prioridade por Paciente?"):
            st.write("""
                Pacientes com casos graves (ex.: gravidade alta) podem ser atendidos mais rápido em todos os setores, não só na Consulta. Isso simula a realidade, onde médicos priorizam emergências, reduzindo o tempo de espera para quem mais precisa.
            """)
        
        with st.expander("O que é o Setor de Saída?"):
            st.write("""
                Após cada setor, há uma chance de o paciente sair do hospital (ex.: após Exames, pode não precisar de mais atendimentos). Você define essas chances, ajudando a simular quando os pacientes terminam o atendimento.
            """)
        
        with st.expander("Como identificar gargalos?"):
            st.write("""
                O sistema mostra quais setores têm os maiores tempos de espera (ex.: Triagem lotada) e a taxa de ocupação dos médicos. Isso ajuda a decidir onde adicionar recursos, como mais médicos ou melhor organização.
            """)
        
        with st.expander("O que é o Histórico de Sessões?"):
            st.write("""
                Você pode salvar suas simulações (configurações, resultados e estatísticas) em arquivos locais e carregá-los depois. Isso é útil para comparar diferentes cenários, como turnos ou número de médicos, sem precisar reconfigurar tudo!
            """)
        
        with st.expander("O que são Recomendações?"):
            st.write("""
                O sistema analisa os resultados e sugere melhorias, como adicionar médicos se a ocupação estiver alta ou reforçar um setor com muito tempo de espera. Isso ajuda a otimizar o atendimento no hospital do Lubango!
            """)
        
        with st.expander("Como funciona a simulação?"):
            st.write("""
                O sistema simula pacientes passando pelos setores, considerando médicos disponíveis, gravidade, prioridades e chances de saída. Ele rastreia tempos de espera, visitas aos setores e ocupação, mostrando onde melhorar o atendimento no Lubango!
            """)
        
        with st.expander("Como configurar a simulação?"):
            st.write("""
                Na página 'Planejador', você define:
                - **Setores** (ex.: Triagem, Consulta).
                - **Chances de transição** entre setores.
                - **Chances de saída** após cada setor.
                - **Número de pacientes**, turno, gravidade e médicos.
                - **Prioridade** para casos graves.
                - **Sessões** para salvar/carregar simulações.
                Cada campo tem explicações. Experimente valores para ver como otimizar o hospital!
            """)