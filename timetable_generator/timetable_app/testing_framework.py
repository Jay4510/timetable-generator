"""
Comprehensive testing and quality assurance framework for timetable generation.
Includes unit tests, integration tests, performance tests, and validation suites.
"""

import unittest
import pytest
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from unittest.mock import Mock, patch, MagicMock
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import memory_profiler
import cProfile
import pstats
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class TimetableTestCase(TestCase):
    """Base test case with common setup for timetable tests"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
        self.performance_metrics = {}
        self.start_time = time.time()
    
    def tearDown(self):
        """Clean up after tests"""
        self.end_time = time.time()
        self.performance_metrics['execution_time'] = self.end_time - self.start_time
        logger.info(f"Test execution time: {self.performance_metrics['execution_time']:.3f}s")
    
    def create_test_data(self):
        """Create comprehensive test data"""
        from .models import Teacher, Subject, Room, TimeSlot, Year, Division
        
        # Create years and divisions
        self.se_year = Year.objects.create(name="SE")
        self.te_year = Year.objects.create(name="TE")
        
        self.se_a = Division.objects.create(year=self.se_year, name="A", num_batches=3)
        self.se_b = Division.objects.create(year=self.se_year, name="B", num_batches=3)
        
        # Create teachers with different specializations
        self.teachers = []
        teacher_data = [
            ("Dr. Smith", "Computer Science", 5),
            ("Prof. Johnson", "Mathematics", 8),
            ("Dr. Brown", "Physics", 3),
            ("Ms. Davis", "Chemistry", 6),
            ("Mr. Wilson", "Electronics", 4)
        ]
        
        for name, specialization, experience in teacher_data:
            teacher = Teacher.objects.create(
                name=name,
                max_sessions_per_week=14,
                specialization=specialization,
                experience_years=experience
            )
            self.teachers.append(teacher)
        
        # Create subjects
        self.subjects = []
        subject_data = [
            ("Data Structures", 4, False, self.se_year, self.se_a),
            ("Database Management", 3, False, self.se_year, self.se_a),
            ("Programming Lab", 2, True, self.se_year, self.se_a),
            ("Mathematics", 4, False, self.se_year, self.se_a),
            ("Physics", 3, False, self.se_year, self.se_a)
        ]
        
        for name, sessions, is_lab, year, division in subject_data:
            subject = Subject.objects.create(
                name=name,
                sessions_per_week=sessions,
                is_lab=is_lab,
                year=year,
                division=division
            )
            self.subjects.append(subject)
        
        # Create rooms
        self.rooms = []
        room_data = [
            ("Room 101", 60, "class"),
            ("Room 102", 60, "class"),
            ("Lab 201", 30, "lab"),
            ("Lab 202", 30, "lab"),
            ("Auditorium", 200, "class")
        ]
        
        for name, capacity, room_type in room_data:
            room = Room.objects.create(
                name=name,
                capacity=capacity,
                room_type=room_type
            )
            self.rooms.append(room)
        
        # Create time slots
        self.timeslots = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        times = [
            ("09:00", "10:00"),
            ("10:00", "11:00"),
            ("11:15", "12:15"),
            ("12:15", "13:15"),
            ("14:00", "15:00"),
            ("15:00", "16:00"),
            ("16:00", "17:00")
        ]
        
        for day in days:
            for start_time, end_time in times:
                timeslot = TimeSlot.objects.create(
                    day=day,
                    start_time=start_time,
                    end_time=end_time
                )
                self.timeslots.append(timeslot)

class GeneticAlgorithmTests(TimetableTestCase):
    """Test suite for genetic algorithm functionality"""
    
    def test_chromosome_creation(self):
        """Test chromosome creation and validation"""
        from .genetic_algorithm import generate_random_chromosome, Chromosome
        
        chromosome = generate_random_chromosome()
        
        self.assertIsInstance(chromosome, Chromosome)
        self.assertGreater(len(chromosome.genes), 0)
        
        # Validate gene structure
        for gene in chromosome.genes:
            self.assertEqual(len(gene), 5)  # (subject_id, teacher_id, room_id, timeslot_id, batch_num)
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            self.assertIsInstance(subject_id, int)
            self.assertIsInstance(teacher_id, int)
            self.assertIsInstance(batch_num, int)
    
    def test_fitness_calculation(self):
        """Test fitness function accuracy"""
        from .genetic_algorithm import Chromosome
        
        # Create a chromosome with known violations
        test_genes = [
            (self.subjects[0].id, self.teachers[0].id, self.rooms[0].id, self.timeslots[0].id, 1),
            (self.subjects[1].id, self.teachers[0].id, self.rooms[1].id, self.timeslots[0].id, 1),  # Same teacher, same time
        ]
        
        chromosome = Chromosome(test_genes)
        fitness = chromosome.fitness()
        
        # Should have negative fitness due to teacher conflict
        self.assertLess(fitness, 0)
    
    def test_crossover_operation(self):
        """Test crossover operations"""
        from .genetic_algorithm import single_point_crossover, generate_random_chromosome
        
        parent1 = generate_random_chromosome()
        parent2 = generate_random_chromosome()
        
        child1, child2 = single_point_crossover(parent1, parent2)
        
        self.assertIsNotNone(child1)
        self.assertIsNotNone(child2)
        self.assertNotEqual(child1.genes, parent1.genes)
        self.assertNotEqual(child2.genes, parent2.genes)
    
    def test_mutation_operation(self):
        """Test mutation operations"""
        from .genetic_algorithm import mutate, generate_random_chromosome
        
        original = generate_random_chromosome()
        mutated = generate_random_chromosome()
        mutated.genes = original.genes.copy()
        
        mutate(mutated, mutation_rate=1.0)  # Force mutation
        
        # Should have some differences after mutation
        differences = sum(1 for i, gene in enumerate(mutated.genes) 
                         if i < len(original.genes) and gene != original.genes[i])
        self.assertGreater(differences, 0)
    
    @pytest.mark.performance
    def test_algorithm_performance(self):
        """Test genetic algorithm performance"""
        from .genetic_algorithm import GeneticAlgorithm
        
        start_time = time.time()
        
        ga = GeneticAlgorithm(population_size=20, generations=50)
        result = ga.run()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertLess(execution_time, 60)  # Should complete within 60 seconds
        self.assertIsNotNone(result)
        logger.info(f"GA execution time: {execution_time:.2f}s")

class ConstraintValidationTests(TimetableTestCase):
    """Test suite for constraint validation"""
    
    def test_hard_constraint_validation(self):
        """Test all hard constraints"""
        from .genetic_algorithm import Chromosome
        
        # Test teacher double-booking
        conflicting_genes = [
            (self.subjects[0].id, self.teachers[0].id, self.rooms[0].id, self.timeslots[0].id, 1),
            (self.subjects[1].id, self.teachers[0].id, self.rooms[1].id, self.timeslots[0].id, 2),
        ]
        
        chromosome = Chromosome(conflicting_genes)
        violations = chromosome.check_hard_constraints()
        
        self.assertGreater(violations, 0, "Should detect teacher double-booking")
    
    def test_room_constraint_validation(self):
        """Test room-related constraints"""
        from .genetic_algorithm import Chromosome
        
        # Test lab subject in regular room (should violate)
        lab_subject = next(s for s in self.subjects if s.is_lab)
        regular_room = next(r for r in self.rooms if r.room_type == 'class')
        
        violating_genes = [
            (lab_subject.id, self.teachers[0].id, regular_room.id, self.timeslots[0].id, 1)
        ]
        
        chromosome = Chromosome(violating_genes)
        violations = chromosome.check_hard_constraints()
        
        self.assertGreater(violations, 0, "Should detect lab subject in regular room")
    
    def test_teacher_preference_constraints(self):
        """Test teacher preference system"""
        from .teacher_subject_assignment import TeacherSubjectPreference
        
        # Create a preference
        preference = TeacherSubjectPreference.objects.create(
            teacher=self.teachers[0],
            subject=self.subjects[0],
            preference='refused',
            competency='unqualified'
        )
        
        from .genetic_algorithm import Chromosome
        
        # Create chromosome that violates preference
        violating_genes = [
            (self.subjects[0].id, self.teachers[0].id, self.rooms[0].id, self.timeslots[0].id, 1)
        ]
        
        chromosome = Chromosome(violating_genes)
        violations = chromosome.check_hard_constraints()
        
        self.assertGreater(violations, 0, "Should detect teacher preference violation")

class PerformanceTests(TimetableTestCase):
    """Performance and scalability tests"""
    
    def setUp(self):
        super().setUp()
        self.create_large_dataset()
    
    def create_large_dataset(self):
        """Create large dataset for performance testing"""
        from .models import Teacher, Subject, Room, TimeSlot
        
        # Create 100 teachers
        for i in range(100):
            Teacher.objects.create(
                name=f"Teacher_{i}",
                max_sessions_per_week=random.randint(10, 20)
            )
        
        # Create 200 subjects
        for i in range(200):
            Subject.objects.create(
                name=f"Subject_{i}",
                sessions_per_week=random.randint(2, 6),
                is_lab=random.choice([True, False]),
                year=random.choice([self.se_year, self.te_year]),
                division=random.choice([self.se_a, self.se_b])
            )
        
        # Create 50 rooms
        for i in range(50):
            Room.objects.create(
                name=f"Room_{i}",
                capacity=random.randint(30, 100),
                room_type=random.choice(['class', 'lab'])
            )
    
    @pytest.mark.slow
    def test_large_scale_optimization(self):
        """Test optimization with large dataset"""
        from .genetic_algorithm import GeneticAlgorithm
        
        start_time = time.time()
        memory_before = memory_profiler.memory_usage()[0]
        
        ga = GeneticAlgorithm(population_size=50, generations=100)
        result = ga.run()
        
        end_time = time.time()
        memory_after = memory_profiler.memory_usage()[0]
        
        execution_time = end_time - start_time
        memory_used = memory_after - memory_before
        
        self.assertLess(execution_time, 300)  # Should complete within 5 minutes
        self.assertLess(memory_used, 500)    # Should use less than 500MB
        
        logger.info(f"Large scale test - Time: {execution_time:.2f}s, Memory: {memory_used:.2f}MB")
    
    def test_concurrent_optimization(self):
        """Test concurrent optimization requests"""
        from .genetic_algorithm import GeneticAlgorithm
        
        def run_optimization():
            ga = GeneticAlgorithm(population_size=20, generations=30)
            return ga.run()
        
        start_time = time.time()
        
        # Run 5 concurrent optimizations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_optimization) for _ in range(5)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        
        self.assertEqual(len(results), 5)
        self.assertTrue(all(result is not None for result in results))
        
        logger.info(f"Concurrent optimization time: {end_time - start_time:.2f}s")

class IntegrationTests(TransactionTestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_timetable_generation(self):
        """Test complete timetable generation workflow"""
        from .tasks import generate_timetable_task
        from .models import Session
        
        # Clear existing sessions
        Session.objects.all().delete()
        
        # Run timetable generation
        result = generate_timetable_task()
        
        self.assertEqual(result['status'], 'success')
        
        # Verify sessions were created
        sessions = Session.objects.all()
        self.assertGreater(len(sessions), 0)
        
        # Verify no hard constraint violations
        violations = self.validate_generated_timetable(sessions)
        self.assertEqual(violations['hard_violations'], 0)
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test timetable generation endpoint
        response = client.post('/api/generate-timetable/')
        self.assertIn(response.status_code, [200, 202])
        
        # Test timetable retrieval endpoint
        response = client.get('/api/timetable/')
        self.assertEqual(response.status_code, 200)
        
        # Test teacher endpoints
        response = client.get('/api/teachers/')
        self.assertEqual(response.status_code, 200)
    
    def validate_generated_timetable(self, sessions):
        """Validate generated timetable for constraint violations"""
        violations = {
            'hard_violations': 0,
            'soft_violations': 0,
            'details': []
        }
        
        # Check for teacher conflicts
        teacher_schedule = {}
        for session in sessions:
            key = (session.teacher_id, session.timeslot_id)
            if key in teacher_schedule:
                violations['hard_violations'] += 1
                violations['details'].append(f"Teacher {session.teacher_id} double-booked at {session.timeslot_id}")
            teacher_schedule[key] = session
        
        # Check for room conflicts
        room_schedule = {}
        for session in sessions:
            if session.room_id:
                key = (session.room_id, session.timeslot_id)
                if key in room_schedule:
                    violations['hard_violations'] += 1
                    violations['details'].append(f"Room {session.room_id} double-booked at {session.timeslot_id}")
                room_schedule[key] = session
        
        return violations

class StressTests(TimetableTestCase):
    """Stress tests for system limits"""
    
    def test_memory_usage_under_load(self):
        """Test memory usage under heavy load"""
        from .genetic_algorithm import GeneticAlgorithm
        
        initial_memory = memory_profiler.memory_usage()[0]
        
        # Run multiple optimizations
        for i in range(10):
            ga = GeneticAlgorithm(population_size=100, generations=50)
            result = ga.run()
            
            current_memory = memory_profiler.memory_usage()[0]
            memory_increase = current_memory - initial_memory
            
            # Memory shouldn't grow indefinitely
            self.assertLess(memory_increase, 1000, f"Memory leak detected at iteration {i}")
    
    def test_database_performance_under_load(self):
        """Test database performance with many concurrent operations"""
        from django.db import transaction
        from .models import Session
        
        start_time = time.time()
        
        # Simulate heavy database load
        with transaction.atomic():
            for i in range(1000):
                Session.objects.create(
                    subject=self.subjects[i % len(self.subjects)],
                    teacher=self.teachers[i % len(self.teachers)],
                    room=self.rooms[i % len(self.rooms)],
                    timeslot=self.timeslots[i % len(self.timeslots)],
                    batch_number=random.randint(1, 3)
                )
        
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 30)

class SecurityTests(TimetableTestCase):
    """Security and validation tests"""
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        from django.test import Client
        
        client = Client()
        
        # Test malicious input
        malicious_data = {
            'name': '<script>alert("xss")</script>',
            'sessions_per_week': 'invalid',
            'teacher_id': -1
        }
        
        response = client.post('/api/subjects/', malicious_data)
        self.assertNotEqual(response.status_code, 200)  # Should reject invalid input
    
    def test_permission_enforcement(self):
        """Test permission and access control"""
        from django.contrib.auth.models import User
        from django.test import Client
        
        # Create test user without permissions
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        
        client = Client()
        client.force_login(user)
        
        # Try to access admin-only endpoint
        response = client.delete('/api/sessions/1/')
        self.assertIn(response.status_code, [401, 403])  # Should be unauthorized

class TestRunner:
    """Custom test runner with comprehensive reporting"""
    
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'performance_metrics': {},
            'coverage_report': {}
        }
    
    def run_all_tests(self):
        """Run all test suites"""
        test_suites = [
            GeneticAlgorithmTests,
            ConstraintValidationTests,
            PerformanceTests,
            IntegrationTests,
            StressTests,
            SecurityTests
        ]
        
        for suite_class in test_suites:
            self.run_test_suite(suite_class)
        
        return self.generate_report()
    
    def run_test_suite(self, suite_class):
        """Run a specific test suite"""
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.results['total_tests'] += result.testsRun
        self.results['passed'] += result.testsRun - len(result.failures) - len(result.errors)
        self.results['failed'] += len(result.failures)
        self.results['errors'] += len(result.errors)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        report = {
            'summary': self.results,
            'timestamp': datetime.now().isoformat(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        if self.results['failed'] > 0:
            recommendations.append("Address failing tests before deployment")
        
        if self.results['errors'] > 0:
            recommendations.append("Fix test errors - they indicate code issues")
        
        # Add performance recommendations based on metrics
        recommendations.append("Consider implementing caching for better performance")
        recommendations.append("Monitor memory usage in production")
        
        return recommendations

# Utility functions for testing
def create_test_timetable_data():
    """Create standardized test data"""
    pass

def benchmark_algorithm(algorithm_func, iterations=10):
    """Benchmark algorithm performance"""
    times = []
    for _ in range(iterations):
        start = time.time()
        algorithm_func()
        end = time.time()
        times.append(end - start)
    
    return {
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': np.std(times)
    }

def profile_memory_usage(func):
    """Profile memory usage of a function"""
    def wrapper(*args, **kwargs):
        mem_before = memory_profiler.memory_usage()[0]
        result = func(*args, **kwargs)
        mem_after = memory_profiler.memory_usage()[0]
        
        logger.info(f"Memory usage: {mem_after - mem_before:.2f} MB")
        return result
    
    return wrapper

# Export test classes
__all__ = [
    'TimetableTestCase', 'GeneticAlgorithmTests', 'ConstraintValidationTests',
    'PerformanceTests', 'IntegrationTests', 'StressTests', 'SecurityTests',
    'TestRunner'
]
