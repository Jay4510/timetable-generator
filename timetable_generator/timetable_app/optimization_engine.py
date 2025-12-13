"""
Multi-algorithm optimization engine for timetable generation.
Combines different algorithms for better results and handles edge cases.
"""

import random
import copy
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OptimizationAlgorithm(ABC):
    """Base class for optimization algorithms"""
    
    @abstractmethod
    def optimize(self, initial_solution, constraints, max_iterations=1000):
        pass
    
    @abstractmethod
    def get_algorithm_name(self):
        pass

class HybridGeneticAlgorithm(OptimizationAlgorithm):
    """Enhanced genetic algorithm with multiple operators"""
    
    def __init__(self, population_size=100, elite_ratio=0.1, mutation_rate=0.15):
        self.population_size = population_size
        self.elite_ratio = elite_ratio
        self.mutation_rate = mutation_rate
        self.crossover_operators = ['single_point', 'two_point', 'uniform', 'subject_based']
        self.mutation_operators = ['random', 'smart', 'local_search', 'constraint_guided']
    
    def optimize(self, initial_solution, constraints, max_iterations=500):
        """Run hybrid genetic algorithm with adaptive operators"""
        population = self.initialize_diverse_population(initial_solution)
        best_fitness_history = []
        stagnation_counter = 0
        
        for generation in range(max_iterations):
            # Evaluate fitness
            fitness_scores = [self.evaluate_fitness(individual, constraints) for individual in population]
            
            # Track best fitness
            best_fitness = max(fitness_scores)
            best_fitness_history.append(best_fitness)
            
            # Check for stagnation and adapt
            if generation > 10 and best_fitness <= max(best_fitness_history[-10:-1]):
                stagnation_counter += 1
                if stagnation_counter > 5:
                    self.adapt_parameters()
                    stagnation_counter = 0
            
            # Selection
            elite_count = int(self.population_size * self.elite_ratio)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            elite = [population[i] for i in elite_indices]
            
            # Generate new population
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                # Adaptive operator selection
                crossover_op = self.select_crossover_operator(generation, stagnation_counter)
                mutation_op = self.select_mutation_operator(generation, stagnation_counter)
                
                # Parent selection
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                
                # Crossover
                child1, child2 = self.crossover(parent1, parent2, crossover_op)
                
                # Mutation
                child1 = self.mutate(child1, mutation_op, constraints)
                child2 = self.mutate(child2, mutation_op, constraints)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            
            # Early termination if perfect solution found
            if best_fitness >= 0:  # Assuming 0 or positive means no violations
                logger.info(f"Perfect solution found at generation {generation}")
                break
        
        # Return best solution
        final_fitness = [self.evaluate_fitness(ind, constraints) for ind in population]
        best_index = np.argmax(final_fitness)
        return population[best_index]
    
    def get_algorithm_name(self):
        return "Hybrid Genetic Algorithm"

class SimulatedAnnealingOptimizer(OptimizationAlgorithm):
    """Simulated Annealing for fine-tuning solutions"""
    
    def __init__(self, initial_temp=1000, cooling_rate=0.95, min_temp=1):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
    
    def optimize(self, initial_solution, constraints, max_iterations=10000):
        """Run simulated annealing optimization"""
        current_solution = copy.deepcopy(initial_solution)
        current_fitness = self.evaluate_fitness(current_solution, constraints)
        
        best_solution = copy.deepcopy(current_solution)
        best_fitness = current_fitness
        
        temperature = self.initial_temp
        
        for iteration in range(max_iterations):
            if temperature < self.min_temp:
                break
            
            # Generate neighbor solution
            neighbor = self.generate_neighbor(current_solution, constraints)
            neighbor_fitness = self.evaluate_fitness(neighbor, constraints)
            
            # Accept or reject neighbor
            if self.should_accept(current_fitness, neighbor_fitness, temperature):
                current_solution = neighbor
                current_fitness = neighbor_fitness
                
                # Update best solution
                if neighbor_fitness > best_fitness:
                    best_solution = copy.deepcopy(neighbor)
                    best_fitness = neighbor_fitness
            
            # Cool down
            temperature *= self.cooling_rate
        
        return best_solution
    
    def get_algorithm_name(self):
        return "Simulated Annealing"

class TabuSearchOptimizer(OptimizationAlgorithm):
    """Tabu Search for avoiding local optima"""
    
    def __init__(self, tabu_tenure=50, max_tabu_size=100):
        self.tabu_tenure = tabu_tenure
        self.max_tabu_size = max_tabu_size
        self.tabu_list = []
    
    def optimize(self, initial_solution, constraints, max_iterations=1000):
        """Run tabu search optimization"""
        current_solution = copy.deepcopy(initial_solution)
        best_solution = copy.deepcopy(current_solution)
        best_fitness = self.evaluate_fitness(best_solution, constraints)
        
        for iteration in range(max_iterations):
            # Generate neighborhood
            neighbors = self.generate_neighborhood(current_solution, constraints)
            
            # Find best non-tabu neighbor
            best_neighbor = None
            best_neighbor_fitness = float('-inf')
            
            for neighbor in neighbors:
                if not self.is_tabu(neighbor):
                    fitness = self.evaluate_fitness(neighbor, constraints)
                    if fitness > best_neighbor_fitness:
                        best_neighbor = neighbor
                        best_neighbor_fitness = fitness
            
            if best_neighbor is not None:
                current_solution = best_neighbor
                
                # Add to tabu list
                self.add_to_tabu(best_neighbor)
                
                # Update best solution
                if best_neighbor_fitness > best_fitness:
                    best_solution = copy.deepcopy(best_neighbor)
                    best_fitness = best_neighbor_fitness
        
        return best_solution
    
    def get_algorithm_name(self):
        return "Tabu Search"

class MultiObjectiveOptimizer:
    """Handles multiple conflicting objectives using NSGA-II approach"""
    
    def __init__(self):
        self.objectives = [
            'minimize_hard_violations',
            'minimize_soft_violations', 
            'maximize_teacher_satisfaction',
            'minimize_student_travel_time',
            'balance_workload',
            'optimize_room_utilization'
        ]
    
    def optimize(self, initial_population, constraints, max_generations=200):
        """Multi-objective optimization using NSGA-II"""
        population = initial_population
        
        for generation in range(max_generations):
            # Evaluate all objectives
            objective_scores = self.evaluate_all_objectives(population, constraints)
            
            # Non-dominated sorting
            fronts = self.non_dominated_sort(objective_scores)
            
            # Crowding distance calculation
            for front in fronts:
                self.calculate_crowding_distance(front, objective_scores)
            
            # Selection for next generation
            population = self.select_next_generation(population, fronts)
            
            # Generate offspring
            offspring = self.generate_offspring(population)
            population.extend(offspring)
        
        # Return Pareto front
        final_scores = self.evaluate_all_objectives(population, constraints)
        pareto_front = self.get_pareto_front(population, final_scores)
        
        return pareto_front

class AdaptiveHybridOptimizer:
    """Combines multiple algorithms adaptively based on problem characteristics"""
    
    def __init__(self):
        self.algorithms = {
            'genetic': HybridGeneticAlgorithm(),
            'annealing': SimulatedAnnealingOptimizer(),
            'tabu': TabuSearchOptimizer(),
        }
        self.performance_history = {}
    
    def optimize(self, initial_solution, constraints, time_limit=300):
        """Adaptive optimization using multiple algorithms"""
        start_time = datetime.now()
        best_solution = initial_solution
        best_fitness = self.evaluate_fitness(initial_solution, constraints)
        
        # Analyze problem characteristics
        problem_profile = self.analyze_problem(constraints)
        
        # Select initial algorithm based on problem profile
        algorithm_sequence = self.select_algorithm_sequence(problem_profile)
        
        for algorithm_name in algorithm_sequence:
            if (datetime.now() - start_time).seconds > time_limit:
                break
            
            algorithm = self.algorithms[algorithm_name]
            logger.info(f"Running {algorithm.get_algorithm_name()}")
            
            # Run algorithm with remaining time
            remaining_time = time_limit - (datetime.now() - start_time).seconds
            max_iterations = max(50, remaining_time // 2)  # Adaptive iteration count
            
            try:
                solution = algorithm.optimize(best_solution, constraints, max_iterations)
                fitness = self.evaluate_fitness(solution, constraints)
                
                if fitness > best_fitness:
                    best_solution = solution
                    best_fitness = fitness
                    logger.info(f"Improved fitness: {fitness}")
                
                # Update performance history
                self.update_performance_history(algorithm_name, fitness, problem_profile)
                
            except Exception as e:
                logger.error(f"Algorithm {algorithm_name} failed: {e}")
                continue
        
        return best_solution
    
    def analyze_problem(self, constraints):
        """Analyze problem characteristics to guide algorithm selection"""
        profile = {
            'constraint_density': len(constraints) / 100,  # Normalized
            'hard_constraint_ratio': 0.7,  # Would calculate from actual constraints
            'solution_space_size': 'large',  # Would estimate based on variables
            'constraint_conflicts': 'medium',  # Would analyze constraint interactions
        }
        return profile
    
    def select_algorithm_sequence(self, problem_profile):
        """Select optimal algorithm sequence based on problem characteristics"""
        if problem_profile['constraint_density'] > 0.8:
            return ['genetic', 'tabu', 'annealing']  # High constraint density
        elif problem_profile['hard_constraint_ratio'] > 0.8:
            return ['genetic', 'annealing']  # Many hard constraints
        else:
            return ['genetic', 'annealing', 'tabu']  # Balanced approach

class RealTimeOptimizer:
    """Handles real-time updates and incremental optimization"""
    
    def __init__(self):
        self.current_solution = None
        self.change_log = []
    
    def handle_constraint_change(self, change_type, affected_entities):
        """Handle real-time constraint changes"""
        if change_type == 'teacher_unavailable':
            return self.reschedule_teacher_sessions(affected_entities['teacher_id'])
        elif change_type == 'room_maintenance':
            return self.relocate_room_sessions(affected_entities['room_id'])
        elif change_type == 'subject_added':
            return self.add_subject_sessions(affected_entities['subject_id'])
        
    def incremental_optimization(self, changes):
        """Optimize only affected parts of the timetable"""
        affected_sessions = self.identify_affected_sessions(changes)
        
        # Create mini-problem for affected sessions
        mini_problem = self.extract_subproblem(affected_sessions)
        
        # Optimize subproblem
        optimizer = HybridGeneticAlgorithm(population_size=50)
        optimized_subproblem = optimizer.optimize(mini_problem, self.get_local_constraints())
        
        # Integrate back into main solution
        self.integrate_subsolution(optimized_subproblem, affected_sessions)
        
        return self.current_solution

# Utility functions for the optimization engine

def evaluate_solution_quality(solution, constraints):
    """Comprehensive solution quality evaluation"""
    metrics = {
        'hard_violations': 0,
        'soft_violations': 0,
        'teacher_satisfaction': 0,
        'student_satisfaction': 0,
        'room_utilization': 0,
        'time_efficiency': 0
    }
    
    # Implementation would calculate all metrics
    return metrics

def generate_optimization_report(solution, optimization_history):
    """Generate detailed optimization report"""
    report = {
        'final_fitness': 0,
        'iterations_run': len(optimization_history),
        'algorithms_used': [],
        'constraint_violations': {},
        'improvement_timeline': optimization_history,
        'recommendations': []
    }
    
    return report
