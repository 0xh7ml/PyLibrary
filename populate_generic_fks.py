#!/usr/bin/env python3
"""
Script to populate generic foreign key fields after migration
Run this after running migrations: python3 populate_generic_fks.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from Library.models import Student, Faculty, LibraryEntry, ELibrarySession
    from Tickets.models import Ticket
    from django.contrib.contenttypes.models import ContentType
    from django.db import transaction
    
    def populate_library_entries():
        """Populate LibraryEntry generic foreign keys from student field"""
        print("Populating LibraryEntry generic foreign keys...")
        student_content_type = ContentType.objects.get_for_model(Student)
        
        entries = LibraryEntry.objects.filter(
            student__isnull=False,
            content_type__isnull=True
        )
        
        updated = 0
        with transaction.atomic():
            for entry in entries:
                entry.content_type = student_content_type
                entry.object_id = entry.student.id
                entry.save()
                updated += 1
        
        print(f"✅ Updated {updated} LibraryEntry records")
    
    def populate_elibrary_sessions():
        """Populate ELibrarySession generic foreign keys from student field"""
        print("Populating ELibrarySession generic foreign keys...")
        student_content_type = ContentType.objects.get_for_model(Student)
        
        sessions = ELibrarySession.objects.filter(
            student__isnull=False,
            content_type__isnull=True
        )
        
        updated = 0
        with transaction.atomic():
            for session in sessions:
                session.content_type = student_content_type
                session.object_id = session.student.id
                session.save()
                updated += 1
        
        print(f"✅ Updated {updated} ELibrarySession records")
    
    def populate_tickets():
        """Populate Ticket generic foreign keys from issued_by field"""
        print("Populating Ticket generic foreign keys...")
        student_content_type = ContentType.objects.get_for_model(Student)
        
        tickets = Ticket.objects.filter(
            issued_by__isnull=False,
            content_type__isnull=True
        )
        
        updated = 0
        with transaction.atomic():
            for ticket in tickets:
                ticket.content_type = student_content_type
                ticket.object_id = ticket.issued_by.id
                ticket.save()
                updated += 1
        
        print(f"✅ Updated {updated} Ticket records")
    
    def main():
        print("🔧 Populating generic foreign key fields...")
        print("=" * 50)
        
        try:
            populate_library_entries()
            populate_elibrary_sessions()
            populate_tickets()
            
            print("=" * 50)
            print("✅ All generic foreign key fields populated successfully!")
            
            # Show summary
            total_entries = LibraryEntry.objects.count()
            total_sessions = ELibrarySession.objects.count()
            total_tickets = Ticket.objects.count()
            
            print(f"\n📊 Summary:")
            print(f"   LibraryEntry records: {total_entries}")
            print(f"   ELibrarySession records: {total_sessions}")
            print(f"   Ticket records: {total_tickets}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("Make sure Django is installed and the virtual environment is activated")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()