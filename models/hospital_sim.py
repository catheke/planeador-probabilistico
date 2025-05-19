import simpy
import numpy as np
import logging

# Configurar logging para depuração
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class HospitalSimulator:
    def __init__(self, config, transition_probs):
        """Inicializa a simulação com configurações e probabilidades."""
        self.config = config
        # Usar transition_probs normalizadas do config, se disponíveis
        self.transition_probs = np.array(config.get("transition_probs", transition_probs), dtype=float)
        self.env = simpy.Environment()
        self.results = []
        self.medicos = simpy.PriorityResource(self.env, capacity=config["medicos_disponiveis"])
        self.sector_queues = {sector: simpy.PriorityResource(self.env, capacity=1) for sector in config["sectors"]}
        self.stats = {
            "avg_time_per_sector": {sector: 0.0 for sector in config["sectors"]},
            "sector_visits": {sector: 0 for sector in config["sectors"]},
            "doctor_usage": [],
            "doctor_occupation": 0.0
        }

    def patient_process(self, patient_id, start_sector):
        """Processo de atendimento para um paciente."""
        current_sector = start_sector
        total_waiting_time = 0
        sectors_visited = []
        gravidade_factor = {"baixa": 1.2, "média": 1.0, "alta": 0.8}.get(self.config["gravidade"], 1.0)
        priority = -1 if self.config["prioridade_ativa"] and self.config["gravidade"] == "alta" else 0
        max_steps = 100
        
        step = 0
        while step < max_steps:
            sectors_visited.append(self.config["sectors"][current_sector])
            self.stats["sector_visits"][self.config["sectors"][current_sector]] += 1
            
            try:
                if self.config["sectors"][current_sector] == "Consulta":
                    with self.medicos.request(priority=priority) as req:
                        yield req
                        self.stats["doctor_usage"].append((self.env.now, 1))
                        waiting_time = np.random.exponential(15.0 * gravidade_factor)
                        yield self.env.timeout(waiting_time)
                        self.stats["doctor_usage"].append((self.env.now, -1))
                else:
                    with self.sector_queues[self.config["sectors"][current_sector]].request(priority=priority) as req:
                        yield req
                        waiting_time = np.random.exponential(10.0 * gravidade_factor)
                        yield self.env.timeout(waiting_time)
            except Exception as e:
                logger.error(f"Erro no atendimento do paciente {patient_id} no setor {self.config['sectors'][current_sector]}: {e}")
                break
            
            total_waiting_time += waiting_time
            self.stats["avg_time_per_sector"][self.config["sectors"][current_sector]] += waiting_time
            
            exit_prob = self.config["exit_probs"][current_sector]
            logger.debug(f"Paciente {patient_id}, Setor {self.config['sectors'][current_sector]}, Exit Prob: {exit_prob}")
            if np.random.random() < exit_prob:
                sectors_visited.append("Saída")
                break
            
            trans_probs = self.transition_probs[current_sector]
            prob_sum = sum(trans_probs)
            if not (0.999 <= prob_sum <= 1.001):
                logger.warning(f"Probabilidades inválidas para setor {current_sector}: {trans_probs}, soma: {prob_sum}. Usando uniforme.")
                trans_probs = np.ones(len(self.config["sectors"])) / len(self.config["sectors"])
            
            try:
                logger.debug(f"Probabilidades para setor {current_sector}: {trans_probs}")
                current_sector = np.random.choice(
                    len(self.config["sectors"]),
                    p=trans_probs / sum(trans_probs)
                )
            except ValueError as e:
                logger.error(f"Erro ao escolher próximo setor para paciente {patient_id}: {e}")
                break
            
            step += 1
        
        if step >= max_steps:
            logger.warning(f"Paciente {patient_id} atingiu o limite de passos ({max_steps})")
        
        self.results.append({
            "patient_id": patient_id,
            "total_waiting_time": total_waiting_time,
            "sectors_visited": sectors_visited,
            "priority": "Alta" if priority == -1 else "Normal"
        })

    def run_simulation(self):
        """Executa a simulação completa."""
        for i in range(self.config["num_patients"]):
            self.env.process(self.patient_process(i, start_sector=0))
        
        try:
            self.env.run()
        except Exception as e:
            logger.error(f"Erro durante a simulação: {e}")
            raise
        
        for sector in self.stats["avg_time_per_sector"]:
            visits = self.stats["sector_visits"][sector]
            self.stats["avg_time_per_sector"][sector] = (
                self.stats["avg_time_per_sector"][sector] / visits if visits > 0 else 0.0
            )
        
        total_time = self.env.now
        if total_time > 0:
            occupied_time = sum(
                (end - start) for start, end in zip(
                    [t for t, _ in self.stats["doctor_usage"][::2]],
                    [t for t, _ in self.stats["doctor_usage"][1::2]]
                )
            )
            self.stats["doctor_occupation"] = occupied_time / total_time
        
        return self.results, self.stats