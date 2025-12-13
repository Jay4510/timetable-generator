"""
AI-powered analytics and insights for timetable optimization.
Provides intelligent recommendations and predictive analytics.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class TimetableAnalytics:
    """Advanced analytics for timetable performance and optimization"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        
    def analyze_timetable_quality(self, timetable_data):
        """Comprehensive timetable quality analysis"""
        analysis = {
            'overall_score': 0,
            'efficiency_metrics': {},
            'bottlenecks': [],
            'recommendations': [],
            'teacher_workload_analysis': {},
            'room_utilization_analysis': {},
            'student_schedule_analysis': {}
        }
        
        # Convert to DataFrame for analysis
        df = self.prepare_dataframe(timetable_data)
        
        # Calculate efficiency metrics
        analysis['efficiency_metrics'] = self.calculate_efficiency_metrics(df)
        
        # Identify bottlenecks
        analysis['bottlenecks'] = self.identify_bottlenecks(df)
        
        # Generate recommendations
        analysis['recommendations'] = self.generate_recommendations(df, analysis['bottlenecks'])
        
        # Detailed analyses
        analysis['teacher_workload_analysis'] = self.analyze_teacher_workload(df)
        analysis['room_utilization_analysis'] = self.analyze_room_utilization(df)
        analysis['student_schedule_analysis'] = self.analyze_student_schedules(df)
        
        # Calculate overall score
        analysis['overall_score'] = self.calculate_overall_score(analysis)
        
        return analysis
    
    def calculate_efficiency_metrics(self, df):
        """Calculate various efficiency metrics"""
        metrics = {}
        
        # Time utilization
        total_slots = len(df['timeslot'].unique()) * len(df['room'].unique())
        used_slots = len(df)
        metrics['time_utilization'] = used_slots / total_slots if total_slots > 0 else 0
        
        # Teacher utilization
        teacher_sessions = df.groupby('teacher')['session_id'].count()
        metrics['avg_teacher_sessions'] = teacher_sessions.mean()
        metrics['teacher_utilization_std'] = teacher_sessions.std()
        
        # Room utilization
        room_sessions = df.groupby('room')['session_id'].count()
        metrics['avg_room_sessions'] = room_sessions.mean()
        metrics['room_utilization_std'] = room_sessions.std()
        
        # Gap analysis
        metrics['avg_gaps_per_student'] = self.calculate_student_gaps(df)
        metrics['avg_gaps_per_teacher'] = self.calculate_teacher_gaps(df)
        
        # Consecutive session analysis
        metrics['consecutive_sessions_ratio'] = self.calculate_consecutive_ratio(df)
        
        return metrics
    
    def identify_bottlenecks(self, df):
        """Identify scheduling bottlenecks and conflicts"""
        bottlenecks = []
        
        # Overloaded teachers
        teacher_load = df.groupby('teacher').size()
        overloaded_teachers = teacher_load[teacher_load > teacher_load.quantile(0.9)]
        for teacher, load in overloaded_teachers.items():
            bottlenecks.append({
                'type': 'overloaded_teacher',
                'entity': teacher,
                'severity': 'high' if load > teacher_load.quantile(0.95) else 'medium',
                'details': f'Teacher has {load} sessions, above 90th percentile'
            })
        
        # Underutilized rooms
        room_usage = df.groupby('room').size()
        underutilized_rooms = room_usage[room_usage < room_usage.quantile(0.1)]
        for room, usage in underutilized_rooms.items():
            bottlenecks.append({
                'type': 'underutilized_room',
                'entity': room,
                'severity': 'low',
                'details': f'Room used only {usage} times, below 10th percentile'
            })
        
        # Peak time conflicts
        time_conflicts = df.groupby('timeslot').size()
        peak_times = time_conflicts[time_conflicts > time_conflicts.quantile(0.9)]
        for timeslot, conflicts in peak_times.items():
            bottlenecks.append({
                'type': 'peak_time_conflict',
                'entity': timeslot,
                'severity': 'medium',
                'details': f'High demand timeslot with {conflicts} sessions'
            })
        
        return bottlenecks
    
    def generate_recommendations(self, df, bottlenecks):
        """Generate AI-powered recommendations"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'overloaded_teacher':
                recommendations.extend(self.recommend_teacher_load_balancing(df, bottleneck))
            elif bottleneck['type'] == 'underutilized_room':
                recommendations.extend(self.recommend_room_optimization(df, bottleneck))
            elif bottleneck['type'] == 'peak_time_conflict':
                recommendations.extend(self.recommend_time_redistribution(df, bottleneck))
        
        # General optimization recommendations
        recommendations.extend(self.recommend_general_optimizations(df))
        
        return recommendations
    
    def predict_scheduling_conflicts(self, proposed_changes):
        """Predict potential conflicts from proposed changes"""
        if 'conflict_predictor' not in self.models:
            self.train_conflict_predictor()
        
        model = self.models['conflict_predictor']
        
        # Prepare features from proposed changes
        features = self.extract_conflict_features(proposed_changes)
        
        # Predict conflict probability
        conflict_probability = model.predict_proba(features)[:, 1]
        
        predictions = []
        for i, prob in enumerate(conflict_probability):
            if prob > 0.7:  # High conflict probability
                predictions.append({
                    'change': proposed_changes[i],
                    'conflict_probability': prob,
                    'risk_level': 'high' if prob > 0.9 else 'medium',
                    'suggested_alternatives': self.suggest_alternatives(proposed_changes[i])
                })
        
        return predictions
    
    def optimize_teacher_preferences(self, teacher_preferences, current_assignments):
        """Optimize assignments based on teacher preferences using ML"""
        # Create preference matrix
        preference_matrix = self.create_preference_matrix(teacher_preferences)
        
        # Use collaborative filtering approach
        optimized_assignments = self.collaborative_filtering_optimization(
            preference_matrix, 
            current_assignments
        )
        
        return optimized_assignments
    
    def detect_anomalies(self, timetable_data):
        """Detect anomalies in timetable using unsupervised learning"""
        if 'anomaly_detector' not in self.models:
            self.train_anomaly_detector()
        
        model = self.models['anomaly_detector']
        
        # Prepare features
        features = self.extract_anomaly_features(timetable_data)
        
        # Detect anomalies
        anomaly_scores = model.decision_function(features)
        anomalies = model.predict(features)
        
        anomaly_reports = []
        for i, (score, is_anomaly) in enumerate(zip(anomaly_scores, anomalies)):
            if is_anomaly == -1:  # Anomaly detected
                anomaly_reports.append({
                    'session_index': i,
                    'anomaly_score': score,
                    'session_data': timetable_data[i],
                    'possible_issues': self.diagnose_anomaly(timetable_data[i], score)
                })
        
        return anomaly_reports
    
    def generate_optimization_insights(self, historical_data):
        """Generate insights from historical timetable data"""
        insights = {
            'patterns': {},
            'trends': {},
            'success_factors': {},
            'failure_patterns': {}
        }
        
        df = pd.DataFrame(historical_data)
        
        # Identify successful patterns
        insights['patterns'] = self.identify_successful_patterns(df)
        
        # Analyze trends over time
        insights['trends'] = self.analyze_temporal_trends(df)
        
        # Identify success factors
        insights['success_factors'] = self.identify_success_factors(df)
        
        # Common failure patterns
        insights['failure_patterns'] = self.identify_failure_patterns(df)
        
        return insights
    
    def create_interactive_dashboard_data(self, timetable_data):
        """Prepare data for interactive dashboard visualization"""
        dashboard_data = {
            'summary_stats': {},
            'charts': {},
            'heatmaps': {},
            'network_graphs': {},
            'alerts': []
        }
        
        df = self.prepare_dataframe(timetable_data)
        
        # Summary statistics
        dashboard_data['summary_stats'] = {
            'total_sessions': len(df),
            'unique_teachers': df['teacher'].nunique(),
            'unique_rooms': df['room'].nunique(),
            'utilization_rate': len(df) / (df['teacher'].nunique() * 40),  # Assuming 40 slots per week
            'avg_sessions_per_teacher': df.groupby('teacher').size().mean()
        }
        
        # Chart data
        dashboard_data['charts'] = {
            'teacher_workload': df.groupby('teacher').size().to_dict(),
            'room_utilization': df.groupby('room').size().to_dict(),
            'daily_distribution': df.groupby('day').size().to_dict(),
            'hourly_distribution': df.groupby('hour').size().to_dict()
        }
        
        # Heatmap data
        dashboard_data['heatmaps'] = {
            'teacher_time_heatmap': self.create_teacher_time_heatmap(df),
            'room_time_heatmap': self.create_room_time_heatmap(df)
        }
        
        # Network graph data (teacher-subject relationships)
        dashboard_data['network_graphs'] = {
            'teacher_subject_network': self.create_teacher_subject_network(df)
        }
        
        # Generate alerts
        dashboard_data['alerts'] = self.generate_dashboard_alerts(df)
        
        return dashboard_data
    
    def train_models(self, historical_data):
        """Train ML models on historical data"""
        logger.info("Training AI models...")
        
        # Train conflict predictor
        self.train_conflict_predictor(historical_data)
        
        # Train anomaly detector
        self.train_anomaly_detector(historical_data)
        
        # Train satisfaction predictor
        self.train_satisfaction_predictor(historical_data)
        
        logger.info("AI models trained successfully")
    
    def train_conflict_predictor(self, historical_data=None):
        """Train model to predict scheduling conflicts"""
        # This would use historical conflict data to train a classifier
        # For now, creating a placeholder model
        from sklearn.ensemble import RandomForestClassifier
        
        # Generate synthetic training data (in production, use real historical data)
        X, y = self.generate_synthetic_conflict_data()
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        self.models['conflict_predictor'] = model
    
    def train_anomaly_detector(self, historical_data=None):
        """Train anomaly detection model"""
        # Generate synthetic normal timetable patterns
        X = self.generate_synthetic_normal_patterns()
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        self.models['anomaly_detector'] = model
    
    def train_satisfaction_predictor(self, historical_data=None):
        """Train model to predict teacher/student satisfaction"""
        # Generate synthetic satisfaction data
        X, y = self.generate_synthetic_satisfaction_data()
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        self.models['satisfaction_predictor'] = model
    
    # Helper methods for data preparation and feature extraction
    
    def prepare_dataframe(self, timetable_data):
        """Convert timetable data to pandas DataFrame"""
        # This would convert the timetable data structure to a DataFrame
        # Placeholder implementation
        return pd.DataFrame(timetable_data)
    
    def extract_conflict_features(self, proposed_changes):
        """Extract features for conflict prediction"""
        # Extract relevant features from proposed changes
        features = []
        for change in proposed_changes:
            feature_vector = [
                change.get('teacher_load', 0),
                change.get('room_capacity_ratio', 0),
                change.get('time_slot_popularity', 0),
                change.get('subject_difficulty', 0)
            ]
            features.append(feature_vector)
        return np.array(features)
    
    def generate_synthetic_conflict_data(self):
        """Generate synthetic data for training conflict predictor"""
        # In production, this would use real historical conflict data
        n_samples = 1000
        n_features = 10
        
        X = np.random.rand(n_samples, n_features)
        y = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])  # 20% conflicts
        
        return X, y
    
    def generate_synthetic_normal_patterns(self):
        """Generate synthetic normal timetable patterns"""
        n_samples = 1000
        n_features = 15
        
        return np.random.rand(n_samples, n_features)
    
    def generate_synthetic_satisfaction_data(self):
        """Generate synthetic satisfaction data"""
        n_samples = 1000
        n_features = 8
        
        X = np.random.rand(n_samples, n_features)
        y = np.random.uniform(1, 10, n_samples)  # Satisfaction scores 1-10
        
        return X, y

class PredictiveAnalytics:
    """Predictive analytics for proactive timetable management"""
    
    def predict_future_constraints(self, current_data, time_horizon_days=30):
        """Predict future constraints and bottlenecks"""
        predictions = {
            'teacher_availability_changes': [],
            'room_maintenance_schedules': [],
            'enrollment_changes': [],
            'resource_demands': []
        }
        
        # Implement predictive models here
        return predictions
    
    def forecast_optimization_needs(self, historical_performance):
        """Forecast when timetable optimization will be needed"""
        # Analyze patterns in historical performance to predict optimization needs
        forecast = {
            'next_optimization_date': None,
            'expected_performance_decline': 0,
            'recommended_actions': []
        }
        
        return forecast
    
    def simulate_what_if_scenarios(self, base_timetable, scenarios):
        """Simulate various what-if scenarios"""
        results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            # Simulate the scenario
            simulated_result = self.run_scenario_simulation(base_timetable, scenario_params)
            results[scenario_name] = simulated_result
        
        return results

# Export main classes for use in other modules
__all__ = ['TimetableAnalytics', 'PredictiveAnalytics']
