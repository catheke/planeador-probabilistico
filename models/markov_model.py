import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MarkovHospitalModel:
    def __init__(self, config):
        """Inicializa o modelo com configurações."""
        self.config = config
        self.sectors = config["sectors"]
        self.turno = config["turno"]
        self.gravidade = config["gravidade"]
        self.transition_base = config["transition_base"]
        self.exit_probs = config["exit_probs"]
        
        # Validar probabilidades iniciais
        for i, probs in enumerate(self.transition_base):
            total = sum(probs) + self.exit_probs[i]
            if abs(total - 1.0) > 0.1:
                logger.warning(f"Probabilidades iniciais para {self.sectors[i]} somam {total:.2f}. Serão normalizadas.")

    def compute_transitions(self):
        """Calcula probabilidades de transição com ajustes."""
        num_sectors = len(self.sectors)
        transition_probs = np.array(self.transition_base, dtype=float)
        exit_probs = np.array(self.exit_probs, dtype=float)
        
        # Ajustar probabilidades com base no turno e gravidade
        turno_factor = {"manhã": 1.0, "tarde": 1.1, "noite": 1.3}.get(self.turno, 1.0)
        gravidade_factor = {"baixa": 0.9, "média": 1.0, "alta": 1.2}.get(self.gravidade, 1.0)
        factor = turno_factor * gravidade_factor
        
        # Aplicar fator e adicionar pequena aleatoriedade
        transition_probs *= factor
        transition_probs += np.random.uniform(0, 0.05, transition_probs.shape)
        exit_probs *= factor
        exit_probs += np.random.uniform(0, 0.05, exit_probs.shape)
        
        # Garantir valores não-negativos
        transition_probs = np.clip(transition_probs, 0, None)
        exit_probs = np.clip(exit_probs, 0, None)
        
        # Normalizar para soma exata de 1
        for i in range(num_sectors):
            total = sum(transition_probs[i]) + exit_probs[i]
            if total > 0:
                scale = 1.0 / total
                transition_probs[i] *= scale
                exit_probs[i] *= scale
            else:
                logger.warning(f"Total de probabilidades zero para setor {self.sectors[i]}. Usando distribuição uniforme.")
                transition_probs[i] = np.ones(num_sectors) / (num_sectors + 1)
                exit_probs[i] = 1.0 / (num_sectors + 1)
        
        # Verificar normalização
        for i in range(num_sectors):
            total = sum(transition_probs[i]) + exit_probs[i]
            if not (0.99999 <= total <= 1.00001):
                logger.error(f"Normalização falhou para setor {self.sectors[i]}: soma = {total}")
            else:
                logger.debug(f"Setor {self.sectors[i]} normalizado: soma = {total}")
        
        # Atualizar config com probabilidades normalizadas
        self.config["transition_probs"] = transition_probs.tolist()
        self.config["exit_probs"] = exit_probs.tolist()
        
        return transition_probs