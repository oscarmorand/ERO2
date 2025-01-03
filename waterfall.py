import numpy as np
import pandas as pd
from qs import QS

class Waterfall:

    def __init__(self, lambda_a, lambda_t, lambda_d, nb_servers_test, nb_servers_front=1, q_test_size=None, q_front_size=None, size=100):

        rng = np.random.default_rng(seed=42)

        self.lambda_a = lambda_a
        self.lambda_t = lambda_t
        self.lambda_d = lambda_d

        self.nb_servers_test = nb_servers_test
        self.nb_servers_front = nb_servers_front

        self.a_dist = lambda size : rng.exponential(1./lambda_a, size=size)
        self.t_dist = lambda : rng.exponential(1./lambda_t)
        self.d_dist = lambda : rng.exponential(1./lambda_d)

        self.q_test_size = q_test_size
        self.q_front_size = q_front_size

        self.test_z = size

        self.q_test = QS(self.a_dist, self.t_dist, nb_servers_test, q_test_size, policy = lambda x: 0, test_size=size)
        self.q_front = QS(self.t_dist, self.d_dist, nb_servers_front, q_front_size, policy = lambda x: 0, test_size=size)

    def run(self):
        
        # Pretreat to generate arrivals
        self.q_test.pretreat()

        # Simule la file de tests
        self.q_test.run()

        # Transfert des départs du système de test comme arrivées pour le front
        valid_departures = self.q_test.tops[self.q_test.tops['t_depart_sys'] != -1]
        self.q_front.tops.loc[:, 't_arval_queue'] = valid_departures['t_depart_sys'].values

        # Simule la file de front
        self.q_front.run()

    def posttreat(self):
        """
        Calcule les statistiques pour les deux systèmes de files d'attente.
        """
        # Post-traitement des deux queues
        self.q_test.posttreat()
        self.q_front.posttreat()

        # Statistiques combinées
        combined_stats = {
            'Test Queue': self.q_test.timeline()[1],
            'Front Queue': self.q_front.timeline()[1]
        }

        return combined_stats
    

    def timeline(self, t_delation=2):
        """
        Retourne les processus et les statistiques pour chaque queue.
        """
        process_test, stats_test = self.q_test.timeline(t_delation)
        process_front, stats_front = self.q_front.timeline(t_delation)

        sum_process = pd.concat([process_test, process_front]).groupby(level=0).sum()

        return {
            'Test Process': process_test,
            'Front Process': process_front,
            'Sum Process': sum_process,
            'Test Stats': stats_test,
            'Front Stats': stats_front
        }