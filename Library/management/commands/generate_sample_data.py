from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker
from Library.models import Department, ElibrarySeat, Student, LibraryEntry, ELibrarySession

class Command(BaseCommand):
    help = 'Generate sample data for Library models (20 records each, excluding Department)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new sample data',
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            ELibrarySession.objects.all().delete()
            LibraryEntry.objects.all().delete()
            Student.objects.all().delete()
            ElibrarySeat.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Ensure we have some departments (create a few if none exist)
        if not Department.objects.exists():
            departments = [
                'Computer Science',
                'Information Technology', 
                'Software Engineering',
                'Data Science',
                'Cybersecurity'
            ]
            for dept_name in departments:
                Department.objects.get_or_create(name=dept_name)
            self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments.'))

        # Get all departments for foreign key relationships
        departments = list(Department.objects.all())

        # 1. Generate 20 ElibrarySeat records
        self.stdout.write('Generating ElibrarySeat records...')
        seats_created = 0
        for i in range(1, 21):
            pc_no = f"PC-{i:03d}"
            status = random.choice(['Available', 'Reserved', 'Maintenance'])
            
            seat, created = ElibrarySeat.objects.get_or_create(
                pc_no=pc_no,
                defaults={'status': status}
            )
            if created:
                seats_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {seats_created} ElibrarySeat records.'))

        # 2. Generate 20 Student records
        self.stdout.write('Generating Student records...')
        students_created = 0
        student_names = []
        
        for i in range(20):
            name = fake.name()
            student_names.append(name)
            department = random.choice(departments)
            id_no = f"STU{2020 + (i // 4)}{i+1:03d}"  # Mix of years 2020-2024
            
            student, created = Student.objects.get_or_create(
                id_no=id_no,
                defaults={
                    'name': name,
                    'department': department
                }
            )
            if created:
                students_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {students_created} Student records.'))

        # Get all students and seats for foreign key relationships
        students = list(Student.objects.all())
        seats = list(ElibrarySeat.objects.all())

        # 3. Generate 20 LibraryEntry records
        self.stdout.write('Generating LibraryEntry records...')
        entries_created = 0
        library_entries = []
        
        for i in range(20):
            student = random.choice(students)
            
            # Random entry time in the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(8, 20)  # Between 8 AM and 8 PM
            minutes_ago = random.randint(0, 59)
            
            entry_time = timezone.now() - timedelta(
                days=days_ago, 
                hours=random.randint(0, hours_ago),
                minutes=minutes_ago
            )
            
            # 70% chance of having exit time (completed sessions)
            exit_time = None
            status = 'Entered'
            
            if random.random() < 0.7:  # 70% have exited
                # Exit time 1-8 hours after entry
                exit_hours = random.randint(1, 8)
                exit_minutes = random.randint(0, 59)
                exit_time = entry_time + timedelta(hours=exit_hours, minutes=exit_minutes)
                status = 'Exited'
            
            entry = LibraryEntry.objects.create(
                student=student,
                entry_time=entry_time,
                exit_time=exit_time,
                status=status
            )
            library_entries.append(entry)
            entries_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {entries_created} LibraryEntry records.'))

        # 4. Generate 20 ELibrarySession records
        self.stdout.write('Generating ELibrarySession records...')
        sessions_created = 0
        
        for i in range(20):
            student = random.choice(students)
            seat = random.choice(seats)
            library_entry = random.choice(library_entries) if random.random() < 0.8 else None
            
            # Random start time in the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(8, 20)
            minutes_ago = random.randint(0, 59)
            
            start_time = timezone.now() - timedelta(
                days=days_ago,
                hours=random.randint(0, hours_ago), 
                minutes=minutes_ago
            )
            
            # 80% chance of having end time (completed sessions)
            end_time = None
            status = 'Active'
            
            if random.random() < 0.8:  # 80% are completed
                session_duration = random.randint(30, 480)  # 30 minutes to 8 hours
                end_time = start_time + timedelta(minutes=session_duration)
                status = random.choice(['Completed', 'Cancelled']) if random.random() < 0.1 else 'Completed'
            
            session = ELibrarySession.objects.create(
                student=student,
                seat=seat,
                library_entry=library_entry,
                start_time=start_time,
                end_time=end_time,
                status=status
            )
            sessions_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {sessions_created} ELibrarySession records.'))

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Sample data generation completed!\n'
                f'📊 Summary:\n'
                f'   • ElibrarySeat: {ElibrarySeat.objects.count()} records\n'
                f'   • Student: {Student.objects.count()} records\n'
                f'   • LibraryEntry: {LibraryEntry.objects.count()} records\n'
                f'   • ELibrarySession: {ELibrarySession.objects.count()} records\n'
                f'   • Department: {Department.objects.count()} records (existing)\n\n'
                f'🚀 You can now test your reports and filters!'
            )
        )