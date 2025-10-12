from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from Library.models import Student, LibraryEntry, ELibrarySession, ElibrarySeat
from .utils import LibraryService, LibraryStats
import json
import logging

logger = logging.getLogger(__name__)

def entry_monitor(request):
    """Handle main library entry/exit operations"""
    if request.method == 'POST':
        # Check if it's an AJAX request
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If not AJAX, redirect to prevent JSON display in browser
            return redirect('entry_monitor')
            
        try:
            student_id = request.POST.get('student_id', '').strip()
            
            if not student_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Student ID is required'
                })
            
            # Get student
            student = LibraryService.get_student_by_id(student_id)
            if not student:
                return JsonResponse({
                    'success': False,
                    'message': f'Student with ID {student_id} not found in the system'
                })
            
            # Process entry/exit with transaction
            with transaction.atomic():
                result = LibraryService.process_library_entry(student)
                return JsonResponse(result)
                    
        except Exception as e:
            logger.error(f"Error processing entry/exit for {student_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while processing your request. Please try again.'
            })
    
    # GET request - render the template with stats
    stats = LibraryStats.get_current_stats()
    context = {
        'APP_NAME': 'IUBAT Library System',
        'stats': stats
    }
    return render(request, 'users/entry_monitor.html', context)

def service_monitor(request):
    """Handle e-library seat assignment and services"""
    if request.method == 'POST':
        # Check if it's an AJAX request
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If not AJAX, redirect to prevent JSON display in browser
            return redirect('service_monitor')
            
        try:
            student_id = request.POST.get('student_id', '').strip()
            
            if not student_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Student ID is required'
                })
            
            # Get student
            student = LibraryService.get_student_by_id(student_id)
            if not student:
                return JsonResponse({
                    'success': False,
                    'message': f'Student with ID {student_id} not found in the system'
                })
            
            # Process e-library service with transaction
            with transaction.atomic():
                result = LibraryService.process_elibrary_service(student)
                return JsonResponse(result)
                    
        except Exception as e:
            logger.error(f"Error processing e-library service for {student_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while processing your request. Please try again.'
            })
    
    # GET request - render the template with stats
    stats = LibraryStats.get_current_stats()
    context = {
        'APP_NAME': 'IUBAT Library System',
        'stats': stats
    }
    return render(request, 'users/service_monitor.html', context)

def student_status(request):
    """Get current status of a student - useful for debugging/admin"""
    if request.method == 'GET':
        student_id = request.GET.get('student_id', '').strip()
        
        if not student_id:
            return JsonResponse({
                'success': False,
                'message': 'Student ID is required'
            })
        
        try:
            student = LibraryService.get_student_by_id(student_id)
            if not student:
                return JsonResponse({
                    'success': False,
                    'message': f'Student with ID {student_id} not found in the system'
                })
            
            status = LibraryStats.get_student_status(student)
            
            return JsonResponse({
                'success': True,
                'student': {
                    'name': student.name,
                    'id_no': student.id_no,
                    'department': student.department.name
                },
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Error getting status for {student_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while fetching student status.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

def library_stats(request):
    """Get current library statistics"""
    try:
        stats = LibraryStats.get_current_stats()
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting library stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while fetching library statistics.'
        })
