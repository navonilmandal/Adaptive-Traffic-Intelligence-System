    import random
from utils import get_edge_traffic_data

class Particle:
    def __init__(self):
        # Position represents [w1 (density weight), w2 (waiting time weight)]
        self.position = [random.uniform(0, 5), random.uniform(0, 5)]
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.best_position = list(self.position)
        self.best_fitness = float('inf')

class PSO:
    def __init__(self, num_particles=10, iterations=20):
        self.particles = [Particle() for _ in range(num_particles)]
        self.iterations = iterations
        self.global_best_pos = [1.0, 1.0]
        self.global_best_fitness = float('inf')

    def optimize_weights(self, sample_edges):
        """
        Runs PSO to find optimal weights for path evaluation based on current traffic.
        Lower fitness is better.
        """
        for _ in range(self.iterations):
            for p in self.particles:
                # Fitness Function: distance (constant 1) + w1*density + w2*wait_time
                fitness = 0
                for edge in sample_edges:
                    density, wait_time = get_edge_traffic_data(edge)
                    fitness += 1 + (density * p.position[0]) + (wait_time * p.position[1])

                # Update Personal Best
                if fitness < p.best_fitness:
                    p.best_fitness = fitness
                    p.best_position = list(p.position)

                # Update Global Best
                if fitness < self.global_best_fitness:
                    self.global_best_fitness = fitness
                    self.global_best_pos = list(p.position)

            # Update Velocities and Positions
            for p in self.particles:
                for i in range(2):
                    r1, r2 = random.random(), random.random()
                    # Cognitive and Social components
                    cognitive = 1.5 * r1 * (p.best_position[i] - p.position[i])
                    social = 1.5 * r2 * (self.global_best_pos[i] - p.position[i])
                    p.velocity[i] = 0.5 * p.velocity[i] + cognitive + social
                    p.position[i] = max(0, p.position[i] + p.velocity[i]) # Keep weights positive

        return self.global_best_pos