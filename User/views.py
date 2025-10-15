from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from Library.models import Student, LibraryEntry, ELibrarySession, ElibrarySeat
import json
import logging

logger = logging.getLogger(__name__)

def entry_monitor(request):
    """Render the entry monitoring page"""
    return render(request, 'users/entry_monitor.html')

def service_monitor(request):
    """Render the service monitoring page"""
    return render(request, 'users/service_monitor.html')

@csrf_exempt
def main_library_handler(request):
    """Handle library entry/exit for Entry Monitor"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        service_type = data.get('service_type')

        if not student_id:
            return JsonResponse({'message': 'Student ID is required'}, status=400)

        # This handler is specifically for library entry/exit (Entry Monitor)
        if service_type != 'library':
            return JsonResponse({'message': 'Invalid service type for entry monitor'}, status=400)

        try:
            # Check if the student exists
            student = Student.objects.filter(id_no=student_id).first()
            if not student:
                logger.error(f"Student not found: {student_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student not found. Please check the ID and try again.'
                }, status=404)
        
        except Exception as e:
            logger.error(f"Error finding student {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error finding student'
            }, status=500)
        
        try:
            with transaction.atomic():
                # Get today's date
                today = timezone.now().date()
                
                # Check if student has an active library entry today (entered but not exited)
                today_entry = LibraryEntry.objects.filter(
                    student=student,
                    entry_time__date=today,
                    status='Entered',
                    exit_time__isnull=True
                ).first()
                
                if today_entry:
                    # Student is already inside - mark as exit
                    today_entry.mark_exit()
                    action = 'Exited'
                    message = f'Student {student.name} has exited the library'
                    logger.info(f"Student {student_id} ({student.name}) exited library")
                else:
                    # Student is entering - create new entry record
                    LibraryEntry.objects.create(student=student, status='Entered')
                    action = 'Entered'
                    message = f'Student {student.name} has entered the library'
                    logger.info(f"Student {student_id} ({student.name}) entered library")
                
                return JsonResponse({
                    'status': 'success', 
                    'action': action,
                    'message': message,
                    'student_name': student.name,
                    'student_id': student.id,
                    'department': student.department.name if student.department else 'N/A'
                })
                
        except Exception as e:
            logger.error(f"Error processing library entry/exit for student {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
def service_monitor_handler(request):
    """Handle e-library service for Service Monitor"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        service_type = data.get('service_type')

        if not student_id:
            return JsonResponse({'message': 'Student ID is required'}, status=400)

        # This handler is specifically for e-library service (Service Monitor)
        if service_type != 'elibrary':
            return JsonResponse({'message': 'Invalid service type for service monitor'}, status=400)

        try:
            # Check if the student exists
            student = Student.objects.filter(id_no=student_id).first()
            if not student:
                logger.error(f"Student not found: {student_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student not found. Please check the ID and try again.'
                }, status=404)
        
        except Exception as e:
            logger.error(f"Error finding student {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error finding student'
            }, status=500)
        
        try:
            with transaction.atomic():
                # Get today's date
                today = timezone.now().date()
                
                # First check if student has entered the main library today
                today_library_entry = LibraryEntry.objects.filter(
                    student=student,
                    entry_time__date=today,
                    status='Entered'
                ).first()
                
                if not today_library_entry:
                    # Student has not entered main library today
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Enter Main Library First',
                        'student_name': student.name,
                        'requires_library_entry': True
                    }, status=400)
                
                # Check if student has an active e-library session today
                today_session = ELibrarySession.objects.filter(
                    student=student,
                    start_time__date=today,
                    status='Active',
                    end_time__isnull=True
                ).first()
                
                if today_session:
                    # Student is ending e-library service
                    today_session.end_session()
                    
                    # Free up the seat
                    if today_session.seat:
                        today_session.seat.status = 'Available'
                        today_session.seat.save()
                        seat_info = f" (Seat {today_session.seat.pc_no})"
                    else:
                        seat_info = ""
                    
                    action = 'Service Ended'
                    message = f'Student {student.name} has ended e-library service{seat_info}'
                    
                    logger.info(f"Student {student_id} ({student.name}) ended e-library service")
                    
                    return JsonResponse({
                        'status': 'success', 
                        'action': action,
                        'message': message,
                        'student_name': student.name,
                        'seat_number': today_session.seat.pc_no if today_session.seat else None
                    })
                else:
                    # Student is starting e-library service - check for available seats
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
                        'message': f'Please select a seat for {student.name}',
                        'student_name': student.name,
                        'student_id': student.id,
                        'department': student.department.name if student.department else 'N/A',
                        'requires_seat_selection': True
                    })
                
        except Exception as e:
            logger.error(f"Error processing e-library service for student {student_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
def seat_selection_handler(request):
    """Handle seat selection for e-library service"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        seat_id = data.get('seat_id')

        if not student_id or not seat_id:
            return JsonResponse({'message': 'Student ID and Seat ID required'}, status=400)

        try:
            with transaction.atomic():
                # Get the student
                student = Student.objects.filter(id=student_id).first()
                if not student:
                    return JsonResponse({'message': 'Student not found'}, status=404)

                # Get the seat
                seat = ElibrarySeat.objects.filter(id=seat_id, status='Available').first()
                if not seat:
                    return JsonResponse({'message': 'Seat not available'}, status=400)

                # Create the ELibrarySession record
                session = ELibrarySession.objects.create(
                    student=student,
                    seat=seat,
                    status='Active'
                )

                # Mark the seat as Reserved
                seat.status = 'Reserved'
                seat.save()

                logger.info(f"Student {student.name} assigned to seat {seat.pc_no}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Seat {seat.pc_no} assigned to {student.name}',
                    'seat_number': seat.pc_no,
                    'student_name': student.name
                })

        except Exception as e:
            logger.error(f"Error assigning seat for student {student_id}: {str(e)}")
            return JsonResponse({'message': 'Internal server error'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

def pc_layout(request):
    """Render the PC layout for seat selection"""
    all_seats = ElibrarySeat.objects.all().order_by('pc_no')
    available_seats = all_seats.filter(status='Available')
    context = {
        'all_seats': all_seats,
        'available_seats': available_seats,
        'total_available': available_seats.count(),
        'total_seats': all_seats.count()
    }
    return render(request, 'components/seat_selection.html', context)