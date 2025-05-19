# test_hospital_sim.py: Testes unitários para a simulação
import unittest
from models.hospital_sim import HospitalSimulator

class TestHospitalSimulator(unittest.TestCase):
    def setUp(self):
        self.config = {
            "sectors": ["Triagem", "Consulta", "Exames"],
            "num_patients": 5,
            "gravidade": "média",
            "medicos_disponiveis": 2,
            "transition_base": [[0.6, 0.2, 0.1], [0.2, 0.5, 0.2], [0.1, 0.3, 0.5]],
            "exit_probs": [0.1, 0.1, 0.1],
            "prioridade_ativa": True
        }
        self.transition_probs = [[0.6, 0.2, 0.1], [0.2, 0.5, 0.2], [0.1, 0.3, 0.5]]
        self.simulator = HospitalSimulator(self.config, self.transition_probs)

    def test_simulation_results(self):
        results, stats = self.simulator.run_simulation()
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertGreater(result["total_waiting_time"], 0)
            self.assertTrue(len(result["sectors_visited"]) > 0)
        
    def test_stats(self):
        results, stats = self.simulator.run_simulation()
        self.assertTrue(all(v >= 0 for v in stats["avg_time_per_sector"].values()))
        self.assertTrue(all(v >= 0 for v in stats["sector_visits"].values()))
        self.assertTrue(0 <= stats["doctor_occupation"] <= 1)

if __name__ == '__main__':
    unittest.main()