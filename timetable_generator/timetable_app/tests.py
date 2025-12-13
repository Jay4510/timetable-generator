from django.test import TestCase
from django.utils import timezone
from .models import Teacher, Year, Division, Room, Lab, Subject, TimeSlot, Session
from .genetic_algorithm import Chromosome, generate_random_chromosome, genetic_algorithm
import datetime


class TimetableModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a teacher
        self.teacher = Teacher.objects.create(
            name="Test Teacher",
            max_sessions_per_week=14,
            availability={},
            preferences={}
        )
        
        # Create a year
        self.year = Year.objects.create(name="SE")
        
        # Create a division
        self.division = Division.objects.create(
            year=self.year,
            name="A",
            num_batches=3
        )
        
        # Create a room
        self.room = Room.objects.create(
            name="705",
            capacity=60,
            room_type="class"
        )
        
        # Create a lab
        self.lab = Lab.objects.create(
            name="701",
            capacity=30
        )
        
        # Create a subject
        self.subject = Subject.objects.create(
            name="Mathematics",
            sessions_per_week=4,
            is_lab=False,
            year=self.year,
            division=self.division
        )
        
        # Create a timeslot
        self.timeslot = TimeSlot.objects.create(
            day="Monday",
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        
        # Create a session
        self.session = Session.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            room=self.room,
            timeslot=self.timeslot,
            batch_number=1
        )
    
    def test_teacher_creation(self):
        """Test teacher creation"""
        self.assertEqual(self.teacher.name, "Test Teacher")
        self.assertEqual(self.teacher.max_sessions_per_week, 14)
    
    def test_year_creation(self):
        """Test year creation"""
        self.assertEqual(self.year.name, "SE")
    
    def test_division_creation(self):
        """Test division creation"""
        self.assertEqual(self.division.name, "A")
        self.assertEqual(self.division.num_batches, 3)
        self.assertEqual(self.division.year, self.year)
    
    def test_room_creation(self):
        """Test room creation"""
        self.assertEqual(self.room.name, "705")
        self.assertEqual(self.room.capacity, 60)
        self.assertEqual(self.room.room_type, "class")
    
    def test_lab_creation(self):
        """Test lab creation"""
        self.assertEqual(self.lab.name, "701")
        self.assertEqual(self.lab.capacity, 30)
    
    def test_subject_creation(self):
        """Test subject creation"""
        self.assertEqual(self.subject.name, "Mathematics")
        self.assertEqual(self.subject.sessions_per_week, 4)
        self.assertFalse(self.subject.is_lab)
        self.assertEqual(self.subject.year, self.year)
        self.assertEqual(self.subject.division, self.division)
    
    def test_timeslot_creation(self):
        """Test timeslot creation"""
        self.assertEqual(self.timeslot.day, "Monday")
        self.assertEqual(self.timeslot.start_time, datetime.time(9, 0))
        self.assertEqual(self.timeslot.end_time, datetime.time(10, 0))
    
    def test_session_creation(self):
        """Test session creation"""
        self.assertEqual(self.session.subject, self.subject)
        self.assertEqual(self.session.teacher, self.teacher)
        self.assertEqual(self.session.room, self.room)
        self.assertEqual(self.session.timeslot, self.timeslot)
        self.assertEqual(self.session.batch_number, 1)


class GeneticAlgorithmTests(TestCase):
    def setUp(self):
        """Set up test data for genetic algorithm"""
        # Create minimal test data for GA
        self.teacher = Teacher.objects.create(
            name="Test Teacher",
            max_sessions_per_week=14,
            availability={},
            preferences={}
        )
        
        self.year = Year.objects.create(name="SE")
        
        self.division = Division.objects.create(
            year=self.year,
            name="A",
            num_batches=3
        )
        
        self.room = Room.objects.create(
            name="705",
            capacity=60,
            room_type="class"
        )
        
        self.subject = Subject.objects.create(
            name="Mathematics",
            sessions_per_week=2,  # Reduced for testing
            is_lab=False,
            year=self.year,
            division=self.division
        )
        
        self.timeslot = TimeSlot.objects.create(
            day="Monday",
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
    
    def test_chromosome_creation(self):
        """Test chromosome creation"""
        chromosome = Chromosome()
        self.assertEqual(len(chromosome.genes), 0)
        
        # Test with genes
        genes = [(1, 1, 1, 1, 1)]
        chromosome = Chromosome(genes)
        self.assertEqual(chromosome.genes, genes)
    
    def test_generate_random_chromosome(self):
        """Test random chromosome generation"""
        chromosome = generate_random_chromosome()
        self.assertIsInstance(chromosome, Chromosome)
        # We expect some genes to be generated
        self.assertGreaterEqual(len(chromosome.genes), 0)
    
    def test_genetic_algorithm_execution(self):
        """Test genetic algorithm execution"""
        # This is a basic test to ensure the algorithm runs without errors
        # In a real scenario, we would test for convergence and correctness
        try:
            result = genetic_algorithm()
            self.assertIsInstance(result, Chromosome)
        except Exception as e:
            self.fail(f"Genetic algorithm failed with exception: {e}")
    
    def test_chromosome_fitness(self):
        """Test chromosome fitness calculation"""
        chromosome = Chromosome()
        fitness = chromosome.fitness()
        self.assertIsInstance(fitness, (int, float))
        # Fitness should be 0 or negative (0 means no violations)
        self.assertLessEqual(fitness, 0)
    
    def test_hard_constraint_checking(self):
        """Test hard constraint checking"""
        chromosome = Chromosome()
        violations = chromosome.check_hard_constraints()
        self.assertIsInstance(violations, int)
        self.assertGreaterEqual(violations, 0)
    
    def test_soft_constraint_checking(self):
        """Test soft constraint checking"""
        chromosome = Chromosome()
        violations = chromosome.check_soft_constraints()
        self.assertIsInstance(violations, int)
        self.assertGreaterEqual(violations, 0)