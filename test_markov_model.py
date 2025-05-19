import unittest
import numpy as np
from models.markov_model import MarkovHospitalModel

class TestMarkovModel(unittest.TestCase):
    def setUp(self):
        self.config = {
            "sectors": ["Triagem", "Consulta", "Exames"],
            "turno": "manhã",
            "gravidade": "média",
            "transition_base": [
                [0.6, 0.3, 0.0],
                [0.2, 0.5, 0.2],
                [0.1, 0.3, 0.5]
            ],
            "exit_probs": [0.1, 0.1, 0.1]
        }
        self.model = MarkovHospitalModel(self.config)

    def test_compute_transitions(self):
        transition_probs = self.model.compute_transitions()
        self.assertEqual(transition_probs.shape, (3, 3))
        for i in range(len(self.config["sectors"])):
            total = sum(transition_probs[i]) + self.config["exit_probs"][i]
            self.assertAlmostEqual(total, 1.0, places=5)

    def test_transition_probs_sum_to_one(self):
        transition_probs = self.model.compute_transitions()
        for i in range(len(self.config["sectors"])):
            total = sum(transition_probs[i]) + self.config["exit_probs"][i]
            self.assertTrue(0.99999 <= total <= 1.00001, f"Soma das probabilidades para setor {i} é {total}")

    def test_adjustments_by_turno(self):
        self.config["turno"] = "noite"
        model = MarkovHospitalModel(self.config)
        transition_probs = model.compute_transitions()
        for prob in transition_probs.flatten():
            self.assertGreaterEqual(prob, 0)

    def test_adjustments_by_gravidade(self):
        self.config["gravidade"] = "alta"
        model = MarkovHospitalModel(self.config)
        transition_probs = model.compute_transitions()
        for prob in transition_probs.flatten():
            self.assertGreaterEqual(prob, 0)

if __name__ == '__main__':
    unittest.main()