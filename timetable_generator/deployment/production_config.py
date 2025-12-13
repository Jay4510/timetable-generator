"""
Production deployment configuration and monitoring system.
Handles scalability, monitoring, logging, and production optimizations.
"""

import os
import logging
from datetime import datetime, timedelta
import redis
import celery
from celery import Celery
from kombu import Queue
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import psutil
import json

# Production Django Settings
class ProductionConfig:
    """Production configuration settings"""
    
    # Security settings
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
    DEBUG = False
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
    
    # Database configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'MAX_CONNS': 20,
                'conn_max_age': 600,
            }
        },
        'read_replica': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_READ_USER'),
            'PASSWORD': os.environ.get('DB_READ_PASSWORD'),
            'HOST': os.environ.get('DB_READ_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
    
    # Cache configuration
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 50},
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            }
        },
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/2'),
            'TIMEOUT': 86400,  # 24 hours
        }
    }
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Task routing
    CELERY_TASK_ROUTES = {
        'timetable_app.tasks.generate_timetable_task': {'queue': 'optimization'},
        'timetable_app.tasks.send_notifications': {'queue': 'notifications'},
        'timetable_app.tasks.backup_data': {'queue': 'maintenance'},
    }
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'json': {
                'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/var/log/timetable/app.log',
                'maxBytes': 1024*1024*100,  # 100MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/var/log/timetable/error.log',
                'maxBytes': 1024*1024*50,  # 50MB
                'backupCount': 5,
                'formatter': 'json',
            },
            'sentry': {
                'level': 'ERROR',
                'class': 'sentry_sdk.integrations.logging.SentryHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'error_file'],
                'level': 'INFO',
                'propagate': True,
            },
            'timetable_app': {
                'handlers': ['file', 'error_file', 'sentry'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

class MonitoringSystem:
    """Comprehensive monitoring and alerting system"""
    
    def __init__(self):
        self.setup_metrics()
        self.setup_alerts()
    
    def setup_metrics(self):
        """Initialize Prometheus metrics"""
        self.metrics = {
            'timetable_generations': Counter(
                'timetable_generations_total',
                'Total number of timetable generations',
                ['status', 'algorithm']
            ),
            'generation_duration': Histogram(
                'timetable_generation_duration_seconds',
                'Time spent generating timetables',
                buckets=[1, 5, 10, 30, 60, 120, 300, 600]
            ),
            'active_users': Gauge(
                'active_users_count',
                'Number of active users'
            ),
            'constraint_violations': Counter(
                'constraint_violations_total',
                'Total constraint violations',
                ['type', 'severity']
            ),
            'api_requests': Counter(
                'api_requests_total',
                'Total API requests',
                ['endpoint', 'method', 'status']
            ),
            'database_connections': Gauge(
                'database_connections_active',
                'Active database connections'
            ),
            'memory_usage': Gauge(
                'memory_usage_bytes',
                'Memory usage in bytes'
            ),
            'cpu_usage': Gauge(
                'cpu_usage_percent',
                'CPU usage percentage'
            ),
        }
    
    def setup_alerts(self):
        """Setup alerting rules"""
        self.alert_rules = {
            'high_generation_time': {
                'metric': 'generation_duration',
                'threshold': 300,  # 5 minutes
                'severity': 'warning'
            },
            'high_error_rate': {
                'metric': 'timetable_generations',
                'condition': 'error_rate > 0.1',
                'severity': 'critical'
            },
            'high_memory_usage': {
                'metric': 'memory_usage',
                'threshold': 0.9,  # 90% of available memory
                'severity': 'warning'
            },
            'database_connection_exhaustion': {
                'metric': 'database_connections',
                'threshold': 18,  # Close to max connections
                'severity': 'critical'
            }
        }
    
    def record_timetable_generation(self, status, algorithm, duration):
        """Record timetable generation metrics"""
        self.metrics['timetable_generations'].labels(
            status=status, 
            algorithm=algorithm
        ).inc()
        
        self.metrics['generation_duration'].observe(duration)
    
    def record_api_request(self, endpoint, method, status_code):
        """Record API request metrics"""
        self.metrics['api_requests'].labels(
            endpoint=endpoint,
            method=method,
            status=status_code
        ).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics['memory_usage'].set(memory.used)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics['cpu_usage'].set(cpu_percent)
        
        # Database connections (would need to query actual DB)
        # self.metrics['database_connections'].set(get_db_connection_count())
    
    def check_alerts(self):
        """Check alert conditions and trigger notifications"""
        alerts_triggered = []
        
        for alert_name, rule in self.alert_rules.items():
            if self.evaluate_alert_condition(rule):
                alerts_triggered.append({
                    'name': alert_name,
                    'severity': rule['severity'],
                    'timestamp': datetime.now(),
                    'details': rule
                })
        
        if alerts_triggered:
            self.send_alerts(alerts_triggered)
        
        return alerts_triggered
    
    def evaluate_alert_condition(self, rule):
        """Evaluate if an alert condition is met"""
        # Simplified alert evaluation
        # In production, this would query actual metrics
        return False
    
    def send_alerts(self, alerts):
        """Send alert notifications"""
        for alert in alerts:
            if alert['severity'] == 'critical':
                self.send_critical_alert(alert)
            else:
                self.send_warning_alert(alert)
    
    def send_critical_alert(self, alert):
        """Send critical alert via multiple channels"""
        # Email, SMS, Slack, PagerDuty, etc.
        logging.critical(f"CRITICAL ALERT: {alert['name']} - {alert['details']}")
    
    def send_warning_alert(self, alert):
        """Send warning alert"""
        logging.warning(f"WARNING: {alert['name']} - {alert['details']}")

class PerformanceOptimizer:
    """Automatic performance optimization system"""
    
    def __init__(self):
        self.optimization_history = []
        self.current_config = self.load_current_config()
    
    def analyze_performance(self):
        """Analyze current system performance"""
        metrics = {
            'avg_generation_time': self.get_avg_generation_time(),
            'memory_usage': self.get_memory_usage(),
            'cpu_usage': self.get_cpu_usage(),
            'database_performance': self.analyze_database_performance(),
            'cache_hit_rate': self.get_cache_hit_rate()
        }
        
        return metrics
    
    def suggest_optimizations(self, performance_metrics):
        """Suggest performance optimizations based on metrics"""
        suggestions = []
        
        if performance_metrics['avg_generation_time'] > 120:
            suggestions.append({
                'type': 'algorithm_tuning',
                'description': 'Reduce genetic algorithm population size or generations',
                'impact': 'high',
                'config_changes': {
                    'population_size': max(20, self.current_config.get('population_size', 50) - 10),
                    'generations': max(50, self.current_config.get('generations', 100) - 20)
                }
            })
        
        if performance_metrics['memory_usage'] > 0.8:
            suggestions.append({
                'type': 'memory_optimization',
                'description': 'Enable memory optimization features',
                'impact': 'medium',
                'config_changes': {
                    'enable_memory_optimization': True,
                    'batch_size': min(100, self.current_config.get('batch_size', 1000) // 2)
                }
            })
        
        if performance_metrics['cache_hit_rate'] < 0.7:
            suggestions.append({
                'type': 'cache_optimization',
                'description': 'Increase cache timeout and add more caching layers',
                'impact': 'medium',
                'config_changes': {
                    'cache_timeout': self.current_config.get('cache_timeout', 300) * 2,
                    'enable_query_caching': True
                }
            })
        
        return suggestions
    
    def apply_optimization(self, optimization):
        """Apply an optimization suggestion"""
        try:
            # Backup current config
            self.backup_config()
            
            # Apply changes
            for key, value in optimization['config_changes'].items():
                self.current_config[key] = value
            
            # Save new config
            self.save_config(self.current_config)
            
            # Record optimization
            self.optimization_history.append({
                'timestamp': datetime.now(),
                'optimization': optimization,
                'status': 'applied'
            })
            
            return {'success': True, 'message': 'Optimization applied successfully'}
            
        except Exception as e:
            logging.error(f"Failed to apply optimization: {e}")
            self.restore_config()
            return {'success': False, 'message': str(e)}
    
    def auto_optimize(self):
        """Automatically optimize system based on performance metrics"""
        metrics = self.analyze_performance()
        suggestions = self.suggest_optimizations(metrics)
        
        applied_optimizations = []
        
        for suggestion in suggestions:
            if suggestion['impact'] in ['high', 'medium']:
                result = self.apply_optimization(suggestion)
                if result['success']:
                    applied_optimizations.append(suggestion)
        
        return applied_optimizations
    
    def load_current_config(self):
        """Load current configuration"""
        # Load from file or database
        return {
            'population_size': 50,
            'generations': 100,
            'cache_timeout': 300,
            'batch_size': 1000
        }
    
    def save_config(self, config):
        """Save configuration"""
        # Save to file or database
        pass
    
    def backup_config(self):
        """Backup current configuration"""
        # Create backup
        pass
    
    def restore_config(self):
        """Restore previous configuration"""
        # Restore from backup
        pass

class HealthCheckSystem:
    """System health monitoring and diagnostics"""
    
    def __init__(self):
        self.health_checks = {
            'database': self.check_database_health,
            'redis': self.check_redis_health,
            'celery': self.check_celery_health,
            'disk_space': self.check_disk_space,
            'memory': self.check_memory_health,
            'external_apis': self.check_external_apis
        }
    
    def run_health_checks(self):
        """Run all health checks"""
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in self.health_checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                if result['status'] != 'healthy':
                    overall_status = 'unhealthy'
                    
            except Exception as e:
                results[check_name] = {
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                overall_status = 'unhealthy'
        
        return {
            'overall_status': overall_status,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_database_health(self):
        """Check database connectivity and performance"""
        from django.db import connection
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'response_time': 0.1  # Would measure actual response time
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
    
    def check_redis_health(self):
        """Check Redis connectivity"""
        try:
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
            r.ping()
            
            return {
                'status': 'healthy',
                'message': 'Redis connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Redis connection failed: {str(e)}'
            }
    
    def check_celery_health(self):
        """Check Celery worker status"""
        try:
            from celery import current_app
            
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                return {
                    'status': 'healthy',
                    'message': f'Celery workers active: {len(stats)}',
                    'workers': list(stats.keys())
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'No Celery workers found'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Celery check failed: {str(e)}'
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent > 20:
                status = 'healthy'
            elif free_percent > 10:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'message': f'Disk space: {free_percent:.1f}% free',
                'free_space_gb': disk_usage.free / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Disk space check failed: {str(e)}'
            }
    
    def check_memory_health(self):
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            
            if used_percent < 80:
                status = 'healthy'
            elif used_percent < 90:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'message': f'Memory usage: {used_percent:.1f}%',
                'available_gb': memory.available / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Memory check failed: {str(e)}'
            }
    
    def check_external_apis(self):
        """Check external API dependencies"""
        # Check any external services the system depends on
        return {
            'status': 'healthy',
            'message': 'No external APIs configured'
        }

class DeploymentManager:
    """Manages deployment processes and rollbacks"""
    
    def __init__(self):
        self.deployment_history = []
        self.rollback_points = []
    
    def deploy_new_version(self, version_info):
        """Deploy a new version of the application"""
        deployment = {
            'version': version_info['version'],
            'timestamp': datetime.now(),
            'status': 'in_progress',
            'rollback_point': self.create_rollback_point()
        }
        
        try:
            # Pre-deployment checks
            self.run_pre_deployment_checks()
            
            # Deploy application
            self.execute_deployment(version_info)
            
            # Post-deployment verification
            self.verify_deployment()
            
            deployment['status'] = 'success'
            deployment['end_time'] = datetime.now()
            
        except Exception as e:
            deployment['status'] = 'failed'
            deployment['error'] = str(e)
            deployment['end_time'] = datetime.now()
            
            # Auto-rollback on failure
            self.rollback_to_previous_version(deployment['rollback_point'])
        
        self.deployment_history.append(deployment)
        return deployment
    
    def run_pre_deployment_checks(self):
        """Run checks before deployment"""
        health_checker = HealthCheckSystem()
        health_status = health_checker.run_health_checks()
        
        if health_status['overall_status'] != 'healthy':
            raise Exception("System not healthy for deployment")
    
    def execute_deployment(self, version_info):
        """Execute the actual deployment"""
        # Implementation would handle:
        # - Code deployment
        # - Database migrations
        # - Static file updates
        # - Service restarts
        pass
    
    def verify_deployment(self):
        """Verify deployment was successful"""
        # Run smoke tests
        # Check critical functionality
        # Verify metrics are normal
        pass
    
    def create_rollback_point(self):
        """Create a rollback point"""
        rollback_point = {
            'timestamp': datetime.now(),
            'version': 'current',
            'database_backup': 'backup_location',
            'code_snapshot': 'snapshot_location'
        }
        
        self.rollback_points.append(rollback_point)
        return rollback_point
    
    def rollback_to_previous_version(self, rollback_point):
        """Rollback to a previous version"""
        try:
            # Restore code
            # Restore database
            # Restart services
            logging.info(f"Rolled back to version from {rollback_point['timestamp']}")
        except Exception as e:
            logging.critical(f"Rollback failed: {e}")

# Initialize monitoring system
monitoring = MonitoringSystem()
health_checker = HealthCheckSystem()
performance_optimizer = PerformanceOptimizer()
deployment_manager = DeploymentManager()

# Export for use in Django settings
__all__ = [
    'ProductionConfig', 'MonitoringSystem', 'HealthCheckSystem',
    'PerformanceOptimizer', 'DeploymentManager'
]
