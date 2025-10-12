"""
Django management command to load student data from data.json file
Usage: python manage.py load_student_data
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from Library.models import Department, Student, ElibrarySeat

class Command(BaseCommand):
    help = 'Load student data from data.json file and create sample e-library seats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data.json',
            help='Path to the JSON file containing student data (default: data.json)'
        )
        parser.add_argument(
            '--create-seats',
            action='store_true',
            help='Also create sample e-library seats'
        )
        parser.add_argument(
            '--seats-count',
            type=int,
            default=20,
            help='Number of e-library seats to create (default: 20)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        create_seats = options['create_seats']
        seats_count = options['seats_count']

        # Check if file exists
        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist.')

        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            students_data = data.get('students_data', [])
            if not students_data:
                raise CommandError('No student data found in the file.')

            self.stdout.write(
                self.style.SUCCESS(f'Found {len(students_data)} students in the data file.')
            )

            # Process data with database transaction
            with transaction.atomic():
                created_students = 0
                updated_students = 0
                created_departments = 0

                for student_data in students_data:
                    # Extract data
                    student_id = student_data.get('student_id', '').strip()
                    name = student_data.get('name', '').strip()
                    department_name = student_data.get('department', '').strip()

                    if not all([student_id, name, department_name]):
                        self.stdout.write(
                            self.style.WARNING(f'Skipping incomplete data: {student_data}')
                        )
                        continue

                    # Create or get department
                    department, dept_created = Department.objects.get_or_create(
                        name=department_name
                    )
                    if dept_created:
                        created_departments += 1
                        self.stdout.write(f'Created department: {department_name}')

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
                        self.stdout.write(f'Created student: {name} ({student_id})')
                    else:
                        # Update existing student if data has changed
                        if student.name != name or student.department != department:
                            student.name = name
                            student.department = department
                            student.save()
                            updated_students += 1
                            self.stdout.write(f'Updated student: {name} ({student_id})')

                # Create e-library seats if requested
                created_seats = 0
                if create_seats:
                    for i in range(1, seats_count + 1):
                        seat_no = f"PC-{i:02d}"
                        seat, seat_created = ElibrarySeat.objects.get_or_create(
                            pc_no=seat_no,
                            defaults={'status': 'Available'}
                        )
                        if seat_created:
                            created_seats += 1

                # Summary
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('DATA LOADING SUMMARY'))
                self.stdout.write('='*50)
                self.stdout.write(f'Created departments: {created_departments}')
                self.stdout.write(f'Created students: {created_students}')
                self.stdout.write(f'Updated students: {updated_students}')
                
                if create_seats:
                    self.stdout.write(f'Created e-library seats: {created_seats}')
                    existing_seats = ElibrarySeat.objects.count()
                    self.stdout.write(f'Total e-library seats: {existing_seats}')

                self.stdout.write('='*50)
                self.stdout.write(
                    self.style.SUCCESS('✅ Student data loaded successfully!')
                )

        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')
        except Exception as e:
            raise CommandError(f'Error loading data: {e}')

    def format_department_name(self, dept_name):
        """Format department name for consistency"""
        # Remove extra spaces and normalize
        formatted = ' '.join(dept_name.split())
        return formatted