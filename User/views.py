from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from django.db import connection
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from zoneinfo import ZoneInfo
from Library.models import Student, Faculty, LibraryEntry, ELibrarySession, ElibrarySeat, Department
from Tickets.models import Ticket
from Tickets.utils import send_ticket_created_email
import json
import logging
import re

logger = logging.getLogger(__name__)
BANGLADESH_TZ = ZoneInfo('Asia/Dhaka')
_STUDENT_BLOCK_COLUMNS_READY = None


def student_block_columns_ready():
    """Return True when migration-added student block columns exist in DB."""
    global _STUDENT_BLOCK_COLUMNS_READY
    if _STUDENT_BLOCK_COLUMNS_READY is True:
        return _STUDENT_BLOCK_COLUMNS_READY

    try:
        with connection.cursor() as cursor:
            table_description = connection.introspection.get_table_description(cursor, Student._meta.db_table)
        column_names = {col.name for col in table_description}
        _STUDENT_BLOCK_COLUMNS_READY = {'is_blocked', 'blocked_at', 'block_reason'}.issubset(column_names)
    except Exception:
        _STUDENT_BLOCK_COLUMNS_READY = False

    return _STUDENT_BLOCK_COLUMNS_READY


def _is_before_today_in_bd(dt, bd_today):
    if not dt:
        return False
    return timezone.localtime(dt, BANGLADESH_TZ).date() < bd_today


def enforce_midnight_session_policy():
    """Block students with previous-day active sessions and free reserved seats for the new day."""
    if not student_block_columns_ready():
        return

    now = timezone.now()
    bd_today = timezone.localtime(now, BANGLADESH_TZ).date()

    students_to_block = set()

    active_entries = LibraryEntry.objects.select_related('content_type', 'student').filter(
        status='Entered',
        exit_time__isnull=True,
    )
    for entry in active_entries:
        if not _is_before_today_in_bd(entry.entry_time, bd_today):
            continue

        if entry.student_id:
            students_to_block.add(entry.student_id)
        elif entry.content_type and entry.content_type.model == 'student' and entry.object_id:
            students_to_block.add(entry.object_id)

        entry.exit_time = now
        entry.status = 'Exited'
        entry.save(update_fields=['exit_time', 'status'])

    active_sessions = ELibrarySession.objects.select_related('content_type', 'student', 'seat').filter(
        status='Active',
        end_time__isnull=True,
    )
    for session in active_sessions:
        if not _is_before_today_in_bd(session.start_time, bd_today):
            continue

        if session.student_id:
            students_to_block.add(session.student_id)
        elif session.content_type and session.content_type.model == 'student' and session.object_id:
            students_to_block.add(session.object_id)

        session.end_time = now
        session.status = 'Exited'
        session.save(update_fields=['end_time', 'status'])

        if session.seat_id:
            ElibrarySeat.objects.filter(id=session.seat_id, status='Reserved').update(status='Available')

    if students_to_block:
        Student.objects.filter(id__in=students_to_block).update(
            is_blocked=True,
            blocked_at=now,
            block_reason='Auto-blocked: did not exit before 12:00 AM (Bangladesh time).',
        )

    # Keep seat states consistent: any Reserved seat without an active session
    # is stale and should be released for the new day.
    active_seat_ids = ELibrarySession.objects.filter(
        status='Active',
        end_time__isnull=True,
        seat_id__isnull=False,
    ).values_list('seat_id', flat=True)

    stale_reserved_qs = ElibrarySeat.objects.filter(status='Reserved')
    if active_seat_ids:
        stale_reserved_qs = stale_reserved_qs.exclude(id__in=active_seat_ids)
    stale_reserved_qs.update(status='Available')


def blocked_student_response(user):
    return JsonResponse({
        'status': 'error',
        'message': 'Your account is blocked. Please contact admin to unblock your account.',
        'is_blocked': True,
        'student_name': user.name,
    }, status=403)

def get_user_by_id(user_id):
    """Get user (Student or Faculty) by ID number"""
    # First try to find a student
    student = Student.objects.filter(id_no=user_id).first()
    if student:
        return student, 'student'
    
    # Then try to find a faculty
    faculty = Faculty.objects.filter(id_no=user_id).first()
    if faculty:
        return faculty, 'faculty'
    
    return None, None

def create_library_entry(user, user_type):
    """Create a LibraryEntry for either Student or Faculty"""
    content_type = ContentType.objects.get_for_model(user.__class__)
    return LibraryEntry.objects.create(
        content_type=content_type,
        object_id=user.id,
        status='Entered'
    )

def create_elibrary_session(user, user_type, seat, library_entry=None):
    """Create an ELibrarySession for either Student or Faculty"""
    content_type = ContentType.objects.get_for_model(user.__class__)
    return ELibrarySession.objects.create(
        content_type=content_type,
        object_id=user.id,
        seat=seat,
        library_entry=library_entry,
        status='Active'
    )

def entry_monitor(request):
    """Render the entry monitoring page"""
    departments = Department.objects.order_by('name')
    return render(
        request,
        'users/entry_monitor.html',
        {
            'departments': departments,
            'footer_notice': 'You must log out before you exit the library. Otherwise, you may be blocked from entering again.',
        },
    )

def service_monitor(request):
    """Render the service monitoring page"""
    return render(
        request,
        'users/service_monitor.html',
        {
            'footer_notice': 'You must log out before you exit using the e-library PC. Otherwise, you may be blocked from using the library service again.',
        },
    )


def departments_list_handler(request):
    """Return departments list for registration popup."""
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    departments = Department.objects.order_by('name').values('id', 'name')
    print(f'Departments fetched: {list(departments)}')  # Debugging statement
    return JsonResponse({
        'status': 'success',
        'departments': list(departments)
    })

@csrf_exempt
def main_library_handler(request):
    """Handle library entry/exit for Entry Monitor"""
    if request.method == 'POST':
        enforce_midnight_session_policy()
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        service_type = data.get('service_type')

        if not student_id:
            return JsonResponse({'message': 'Student/Faculty ID is required'}, status=400)

        # This handler is specifically for library entry/exit (Entry Monitor)
        if service_type != 'library':
            return JsonResponse({'message': 'Invalid service type for entry monitor'}, status=400)

        try:
            # Check if the user exists (Student or Faculty)
            user, user_type = get_user_by_id(student_id)
            if not user:
                logger.error(f"User not found: {student_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student/Faculty not found. Please check the ID and try again.'
                }, status=404)

            if user_type == 'student' and student_block_columns_ready() and user.is_blocked:
                return blocked_student_response(user)
        
        except Exception as e:
            logger.error(f"Error finding user {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error finding user'
            }, status=500)
        
        try:
            with transaction.atomic():
                # Get today's date
                today = timezone.now().date()
                
                # Check if user has an active library entry today (entered but not exited)
                # First check with new generic FK
                content_type = ContentType.objects.get_for_model(user.__class__)
                today_entry = LibraryEntry.objects.filter(
                    content_type=content_type,
                    object_id=user.id,
                    entry_time__date=today,
                    status='Entered',
                    exit_time__isnull=True
                ).first()
                
                # If not found and user is a student, check legacy field for backward compatibility
                if not today_entry and user_type == 'student':
                    today_entry = LibraryEntry.objects.filter(
                        student=user,
                        entry_time__date=today,
                        status='Entered',
                        exit_time__isnull=True
                    ).first()
                
                if today_entry:
                    # User must end active e-library session before exiting main library
                    today_session = ELibrarySession.objects.filter(
                        content_type=content_type,
                        object_id=user.id,
                        start_time__date=today,
                        status='Active',
                        end_time__isnull=True
                    ).first()

                    # Backward compatibility for legacy student FK records
                    if not today_session and user_type == 'student':
                        today_session = ELibrarySession.objects.filter(
                            student=user,
                            start_time__date=today,
                            status='Active',
                            end_time__isnull=True
                        ).first()

                    if today_session:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please exit from Service Monitor first before exiting the main library.',
                            'requires_service_exit': True
                        }, status=400)

                    # User is already inside - mark as exit
                    today_entry.mark_exit()
                    action = 'Exited'
                    message = f'{user_type.title()} {user.name} has exited the library'
                    logger.info(f"{user_type.title()} {student_id} ({user.name}) exited library")
                else:
                    # User is entering - create new entry record
                    create_library_entry(user, user_type)
                    action = 'Entered'
                    message = f'{user_type.title()} {user.name} has entered the library'
                    logger.info(f"{user_type.title()} {student_id} ({user.name}) entered library")
                
                return JsonResponse({
                    'status': 'success', 
                    'action': action,
                    'message': message,
                    'student_name': user.name,  # Keep 'student_name' for backward compatibility
                    'user_name': user.name,
                    'user_type': user_type,
                    'student_id': user.id,
                    'user_id': user.id,
                    'department': user.department.name if user.department else 'N/A'
                })
                
        except Exception as e:
            logger.error(f"Error processing library entry/exit for user {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def entry_registration_handler(request):
    """Register a new student from entry monitor popup when ID is not found."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)

    student_id = str(data.get('student_id', '')).strip()
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    department_id = data.get('department_id')

    if not re.fullmatch(r'\d{8}', student_id):
        return JsonResponse({'status': 'error', 'message': 'Invalid ID. Please provide an 8-digit ID.'}, status=400)

    if not name:
        return JsonResponse({'status': 'error', 'message': 'Name is required.'}, status=400)

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Please provide a valid email address.'}, status=400)

    if not department_id:
        return JsonResponse({'status': 'error', 'message': 'Department is required.'}, status=400)

    if Student.objects.filter(id_no=student_id).exists() or Faculty.objects.filter(id_no=student_id).exists():
        return JsonResponse({'status': 'error', 'message': 'This ID already exists.'}, status=400)

    if Student.objects.filter(email=email).exists() or Faculty.objects.filter(email=email).exists():
        return JsonResponse({'status': 'error', 'message': 'This email already exists.'}, status=400)

    department = Department.objects.filter(id=department_id).first()
    if not department:
        return JsonResponse({'status': 'error', 'message': 'Selected department is invalid.'}, status=400)

    student = Student.objects.create(
        name=name,
        email=email,
        department=department,
        id_no=student_id,
    )

    return JsonResponse({
        'status': 'success',
        'message': f'{student.name} has been registered successfully.',
        'student_id': student.id_no,
    })

@csrf_exempt
def service_monitor_handler(request):
    """Handle e-library service for Service Monitor"""
    if request.method == 'POST':
        enforce_midnight_session_policy()
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        service_type = data.get('service_type')

        if not student_id:
            return JsonResponse({'message': 'Student/Faculty ID is required'}, status=400)

        # This handler is specifically for e-library service (Service Monitor)
        if service_type != 'elibrary':
            return JsonResponse({'message': 'Invalid service type for service monitor'}, status=400)

        try:
            # Check if the user exists (Student or Faculty)
            user, user_type = get_user_by_id(student_id)
            if not user:
                logger.error(f"User not found: {student_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student/Faculty not found. Please check the ID and try again.'
                }, status=404)

            if user_type == 'student' and student_block_columns_ready() and user.is_blocked:
                return blocked_student_response(user)
        
        except Exception as e:
            logger.error(f"Error finding user {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error finding user'
            }, status=500)
        
        try:
            with transaction.atomic():
                # Get today's date
                today = timezone.now().date()
                
                # First check if user has entered the main library today
                content_type = ContentType.objects.get_for_model(user.__class__)
                today_library_entry = LibraryEntry.objects.filter(
                    content_type=content_type,
                    object_id=user.id,
                    entry_time__date=today,
                    status='Entered'
                ).first()
                
                # If not found with generic FK and user is student, check legacy field
                if not today_library_entry and user_type == 'student':
                    today_library_entry = LibraryEntry.objects.filter(
                        student=user,
                        entry_time__date=today,
                        status='Entered'
                    ).first()
                
                if not today_library_entry:
                    # User has not entered main library today
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Enter Main Library First',
                        'student_name': user.name,  # Keep for backward compatibility
                        'user_name': user.name,
                        'user_type': user_type,
                        'requires_library_entry': True
                    }, status=400)
                
                # Check if user has an active e-library session today
                today_session = ELibrarySession.objects.filter(
                    content_type=content_type,
                    object_id=user.id,
                    start_time__date=today,
                    status='Active',
                    end_time__isnull=True
                ).first()
                
                # If not found with generic FK and user is student, check legacy field
                if not today_session and user_type == 'student':
                    today_session = ELibrarySession.objects.filter(
                        student=user,
                        start_time__date=today,
                        status='Active',
                        end_time__isnull=True
                    ).first()
                
                if today_session:
                    # User is ending e-library service
                    today_session.end_session()
                    
                    # Free up the seat
                    if today_session.seat:
                        today_session.seat.status = 'Available'
                        today_session.seat.save()
                        seat_info = f" (Seat {today_session.seat.pc_no})"
                    else:
                        seat_info = ""
                    
                    action = 'Service Ended'
                    message = f'{user_type.title()} {user.name} has ended e-library service{seat_info}'
                    
                    logger.info(f"{user_type.title()} {student_id} ({user.name}) ended e-library service")
                    
                    return JsonResponse({
                        'status': 'success', 
                        'action': action,
                        'message': message,
                        'student_name': user.name,  # Keep for backward compatibility
                        'user_name': user.name,
                        'user_type': user_type,
                        'seat_number': today_session.seat.pc_no if today_session.seat else None
                    })
                else:
                    # User is starting e-library service - check for available seats
                    available_seats = ElibrarySeat.objects.filter(status='Available')
                    if not available_seats.exists():
                        return JsonResponse({
                            'status': 'error',
                            'message': 'No available e-library seats. Please try again later.'
                        }, status=400)
                    
                    # Return success with seat selection required
                    return JsonResponse({
                        'status': 'success', 
                        'action': 'Service Starting',
                        'message': f'Please select a seat for {user.name}',
                        'student_name': user.name,  # Keep for backward compatibility
                        'user_name': user.name,
                        'user_type': user_type,
                        'student_id': user.id,
                        'user_id': user.id,
                        'department': user.department.name if user.department else 'N/A',
                        'requires_seat_selection': True
                    })
                
        except Exception as e:
            logger.error(f"Error processing e-library service for user {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
def seat_selection_handler(request):
    """Handle seat selection for e-library service"""
    if request.method == 'POST':
        enforce_midnight_session_policy()
        data = json.loads(request.body)
        
        student_id = data.get('student_id')  # This is actually the user database ID, not ID number
        seat_id = data.get('seat_id')

        if not student_id or not seat_id:
            return JsonResponse({'message': 'User ID and Seat ID required'}, status=400)

        try:
            with transaction.atomic():
                # Get the user - first try Student, then Faculty
                user = Student.objects.filter(id=student_id).first()
                user_type = 'student'
                
                if not user:
                    user = Faculty.objects.filter(id=student_id).first()
                    user_type = 'faculty'
                
                if not user:
                    return JsonResponse({'message': 'User not found'}, status=404)

                if user_type == 'student' and student_block_columns_ready() and user.is_blocked:
                    return blocked_student_response(user)

                # Get the seat
                seat = ElibrarySeat.objects.filter(id=seat_id, status='Available').first()
                if not seat:
                    return JsonResponse({'message': 'Seat not available'}, status=400)

                # Create the ELibrarySession record with generic FK
                session = create_elibrary_session(user, user_type, seat)

                # Mark the seat as Reserved
                seat.status = 'Reserved'
                seat.save()

                logger.info(f"{user_type.title()} {user.name} assigned to seat {seat.pc_no}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Seat {seat.pc_no} assigned to {user.name}',
                    'seat_number': seat.pc_no,
                    'student_name': user.name,  # Keep for backward compatibility
                    'user_name': user.name,
                    'user_type': user_type
                })

        except Exception as e:
            logger.error(f"Error assigning seat for user {student_id}: {str(e)}")
            return JsonResponse({'message': 'Internal server error'}, status=500)

@csrf_exempt
def submit_ticket_handler(request):
    """Handle ticket submission from service monitor"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        user_id_no = data.get('student_id')  # This comes from localStorage as ID number
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        issue_type = data.get('issue_type', 'other_issue')

        if not user_id_no:
            return JsonResponse({
                'status': 'error',
                'message': 'User ID is required'
            }, status=400)
        
        if not title or not description:
            return JsonResponse({
                'status': 'error',
                'message': 'Title and description are required'
            }, status=400)

        try:
            # Find the user (Student or Faculty) by ID number
            user, user_type = get_user_by_id(user_id_no)
            if not user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found'
                }, status=404)
            
            # Create the ticket with generic foreign key
            content_type = ContentType.objects.get_for_model(user.__class__)
            ticket = Ticket.objects.create(
                title=title,
                description=description,
                issue_type=issue_type,
                content_type=content_type,
                object_id=user.id,
                status='open'
            )
            
            logger.info(f"Ticket #{ticket.id} created by {user_type} {user.name} ({user.id_no})")

            # Send email notification to admin
            send_ticket_created_email(ticket)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Ticket submitted successfully! Ticket ID: #{ticket.id}',
                'ticket_id': ticket.id,
                'user_name': user.name,
                'user_type': user_type
            })

        except Exception as e:
            logger.error(f"Error creating ticket for user {user_id_no}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to submit ticket. Please try again.'
            }, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

def pc_layout(request):
    """Render the PC layout for seat selection"""
    all_seats = ElibrarySeat.objects.all().order_by('layout_slot', 'pc_no')
    available_seats = all_seats.filter(status='Available')
    context = {
        'all_seats': all_seats,
        'available_seats': available_seats,
        'total_available': available_seats.count(),
        'total_seats': all_seats.count()
    }
    return render(request, 'components/seat_selection.html', context)