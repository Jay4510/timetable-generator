#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_generator.settings')
django.setup()

from timetable_app.models import Teacher, Department

def fix_foreign_key_constraints():
    """Fix foreign key constraint issues before migration"""
    
    print("=== FIXING FOREIGN KEY CONSTRAINTS ===")
    
    try:
        # Check if Department model exists and has the required department
        print("1. Checking Department model...")
        
        # Try to get or create the 'Information Technology' department
        dept, created = Department.objects.get_or_create(
            name='Information Technology',
            defaults={
                'description': 'Information Technology Department',
                'code': 'IT'
            }
        )
        
        if created:
            print(f"✓ Created missing department: {dept.name}")
        else:
            print(f"✓ Department already exists: {dept.name}")
            
        # Check for other missing departments
        missing_departments = [
            ('Computer Science', 'CS', 'Computer Science Department'),
            ('Electronics', 'EC', 'Electronics Department'),
            ('Mechanical', 'ME', 'Mechanical Department'),
        ]
        
        for name, code, desc in missing_departments:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'code': code}
            )
            if created:
                print(f"✓ Created department: {name}")
        
        print("\n2. Checking Teacher foreign key references...")
        
        # Check teachers with invalid department references
        teachers = Teacher.objects.all()
        for teacher in teachers:
            if hasattr(teacher, 'department_id') and teacher.department_id:
                try:
                    # Try to access the department to see if it exists
                    dept_name = teacher.department.name if teacher.department else 'None'
                    print(f"✓ Teacher {teacher.name}: Department = {dept_name}")
                except Exception as e:
                    print(f"✗ Teacher {teacher.name}: Invalid department reference - {e}")
                    # Fix by assigning to Information Technology department
                    it_dept = Department.objects.get(name='Information Technology')
                    teacher.department = it_dept
                    teacher.save()
                    print(f"✓ Fixed: Assigned {teacher.name} to {it_dept.name}")
        
        print("\n=== CONSTRAINT FIXES COMPLETE ===")
        print("You can now run: python manage.py migrate")
        
    except Exception as e:
        print(f"Error fixing constraints: {e}")
        print("\nAlternative solution:")
        print("1. Drop the database: rm db.sqlite3")
        print("2. Reset migrations: python manage.py migrate --fake-initial")
        print("3. Run setup script: python manage.py setup_college_data")

if __name__ == "__main__":
    fix_foreign_key_constraints()
