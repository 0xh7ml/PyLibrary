"""
Utility functions for User app business logic
"""
from django.utils import timezone
from Library.models import Student, LibraryEntry, ELibrarySession, ElibrarySeat
import logging

logger = logging.getLogger(__name__)

class LibraryService:
    """Service class for library operations"""
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID number"""
        try:
            return Student.objects.get(id_no=student_id)
        except Student.DoesNotExist:
            return None
    
    @staticmethod
    def get_active_library_entry(student):
        """Get active library entry for student"""
        return LibraryEntry.objects.filter(
            student=student,
            status='Entered'
        ).first()
    
    @staticmethod
    def get_active_elibrary_session(student):
        """Get active e-library session for student"""
        return ELibrarySession.objects.filter(
            student=student,
            status='Active'
        ).first()
    
    @staticmethod
    def process_library_entry(student):
        """Process library entry for student"""
        active_entry = LibraryService.get_active_library_entry(student)
        
        if active_entry:
            # Student is exiting
            return LibraryService._process_exit(student, active_entry)
        else:
            # Student is entering
            return LibraryService._process_entry(student)
    
    @staticmethod
    def _process_entry(student):
        """Process library entry"""
        new_entry = LibraryEntry.objects.create(
            student=student,
            status='Entered'
        )
        
        logger.info(f"Student {student.name} ({student.id_no}) entered library at {timezone.now()}")
        
        return {
            'success': True,
            'action': 'entry',
            'message': f'Welcome {student.name}! You have successfully entered the library.',
            'student': {
                'name': student.name,
                'id_no': student.id_no,
                'department': student.department.name
            },
            'entry_time': new_entry.entry_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def _process_exit(student, active_entry):
        """Process library exit"""
        active_entry.mark_exit()
        
        # End any active e-library sessions
        active_sessions = ELibrarySession.objects.filter(
            student=student,
            status='Active'
        )
        
        ended_sessions = []
        for session in active_sessions:
            ended_sessions.append(session.seat.pc_no)
            session.end_session()
        
        logger.info(f"Student {student.name} ({student.id_no}) exited library at {timezone.now()}")
        
        response_data = {
            'success': True,
            'action': 'exit',
            'message': f'Goodbye {student.name}! You have successfully exited the library.',
            'student': {
                'name': student.name,
                'id_no': student.id_no,
                'department': student.department.name
            },
            'entry_time': active_entry.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': active_entry.exit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(active_entry.duration).split('.')[0] if active_entry.duration else None
        }
        
        if ended_sessions:
            response_data['ended_elibrary_sessions'] = ended_sessions
            response_data['message'] += f' Your e-library sessions at seats {", ".join(ended_sessions)} have also been ended.'
        
        return response_data
    
    @staticmethod
    def process_elibrary_service(student):
        """Process e-library service request"""
        # Check if student has entered main library first
        active_library_entry = LibraryService.get_active_library_entry(student)
        
        if not active_library_entry:
            return {
                'success': False,
                'message': f'{student.name}, you must first enter the main library before accessing e-library services.'
            }
        
        # Check for active e-library session
        active_session = LibraryService.get_active_elibrary_session(student)
        
        if active_session:
            # End the session
            return LibraryService._end_elibrary_session(student, active_session)
        else:
            # Start new session
            return LibraryService._start_elibrary_session(student, active_library_entry)
    
    @staticmethod
    def _start_elibrary_session(student, library_entry):
        """Start new e-library session"""
        # Find available seat
        available_seat = ElibrarySeat.objects.filter(status='Available').first()
        
        if not available_seat:
            return {
                'success': False,
                'message': 'Sorry, all e-library seats are currently occupied. Please try again later.'
            }
        
        # Reserve seat and create session
        available_seat.status = 'Reserved'
        available_seat.save()
        
        new_session = ELibrarySession.objects.create(
            student=student,
            seat=available_seat,
            library_entry=library_entry,
            status='Active'
        )
        
        logger.info(f"Student {student.name} ({student.id_no}) started e-library session at seat {available_seat.pc_no}")
        
        return {
            'success': True,
            'action': 'start_session',
            'message': f'Welcome {student.name}! You have been assigned to seat {available_seat.pc_no}.',
            'student': {
                'name': student.name,
                'id_no': student.id_no,
                'department': student.department.name
            },
            'seat': available_seat.pc_no,
            'start_time': new_session.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def _end_elibrary_session(student, active_session):
        """End active e-library session"""
        seat_no = active_session.seat.pc_no
        active_session.end_session()
        
        logger.info(f"Student {student.name} ({student.id_no}) ended e-library session at seat {seat_no}")
        
        return {
            'success': True,
            'action': 'end_session',
            'message': f'{student.name}, you have successfully ended your e-library session.',
            'student': {
                'name': student.name,
                'id_no': student.id_no,
                'department': student.department.name
            },
            'seat': seat_no,
            'start_time': active_session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': active_session.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(active_session.duration).split('.')[0] if active_session.duration else None
        }

class LibraryStats:
    """Service class for library statistics"""
    
    @staticmethod
    def get_current_stats():
        """Get current library statistics"""
        return {
            'students_in_library': LibraryEntry.objects.filter(status='Entered').count(),
            'active_elibrary_sessions': ELibrarySession.objects.filter(status='Active').count(),
            'available_elibrary_seats': ElibrarySeat.objects.filter(status='Available').count(),
            'total_elibrary_seats': ElibrarySeat.objects.count(),
            'occupied_elibrary_seats': ElibrarySeat.objects.filter(status='Reserved').count(),
            'maintenance_elibrary_seats': ElibrarySeat.objects.filter(status='Maintenance').count()
        }
    
    @staticmethod
    def get_student_status(student):
        """Get current status of a student"""
        active_entry = LibraryService.get_active_library_entry(student)
        active_session = LibraryService.get_active_elibrary_session(student)
        
        status = {
            'in_library': bool(active_entry),
            'has_elibrary_session': bool(active_session),
            'entry_time': active_entry.entry_time.strftime('%Y-%m-%d %H:%M:%S') if active_entry else None,
            'elibrary_seat': active_session.seat.pc_no if active_session else None,
            'elibrary_start_time': active_session.start_time.strftime('%Y-%m-%d %H:%M:%S') if active_session else None
        }
        
        return status