#!/usr/bin/env python3
"""
Simple script to load student data into Django models
Run this with: python3 load_data_script.py
"""

import os
import sys
import json
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from Library.models import Department, Student, ElibrarySeat
    from django.db import transaction
    
    def load_student_data():
        """Load student data from data.json"""
        
        # Load JSON data
        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        students_data = data.get('students_data', [])
        print(f"Found {len(students_data)} students in data.json")
        
        # Load data with transaction
        with transaction.atomic():
            created_students = 0
            updated_students = 0
            created_departments = 0
            
            for student_data in students_data:
                student_id = student_data.get('student_id', '').strip()
                name = student_data.get('name', '').strip()
                department_name = student_data.get('department', '').strip()
                
                if not all([student_id, name, department_name]):
                    print(f"Skipping incomplete data: {student_data}")
                    continue
                
                # Create or get department
                department, dept_created = Department.objects.get_or_create(
                    name=department_name
                )
                if dept_created:
                    created_departments += 1
                    print(f"✅ Created department: {department_name}")
                
                # Create or update student
                student, student_created = Student.objects.get_or_create(
                    id_no=student_id,
                    defaults={
                        'name': name,
                        'department': department
                    }
                )
                
                if student_created:
                    created_students += 1
                    print(f"✅ Created student: {name} ({student_id})")
                else:
                    # Update existing student if data changed
                    if student.name != name or student.department != department:
                        student.name = name
                        student.department = department
                        student.save()
                        updated_students += 1
                        print(f"🔄 Updated student: {name} ({student_id})")
            
            # Create e-library seats
            created_seats = 0
            for i in range(1, 21):  # Create 20 seats
                seat_no = f"PC-{i:02d}"
                seat, seat_created = ElibrarySeat.objects.get_or_create(
                    pc_no=seat_no,
                    defaults={'status': 'Available'}
                )
                if seat_created:
                    created_seats += 1
            
            # Summary
            print("\n" + "="*50)
            print("📊 DATA LOADING SUMMARY")
            print("="*50)
            print(f"Created departments: {created_departments}")
            print(f"Created students: {created_students}")
            print(f"Updated students: {updated_students}")
            print(f"Created e-library seats: {created_seats}")
            print(f"Total e-library seats: {ElibrarySeat.objects.count()}")
            print("="*50)
            print("✅ Student data loaded successfully!")
            
    if __name__ == "__main__":
        load_student_data()
        
except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("Make sure Django is installed and the virtual environment is activated")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    import traceback
    traceback.print_exc()