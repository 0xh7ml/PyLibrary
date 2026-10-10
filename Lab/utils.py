from django.db import transaction
from django.db.models import Count, OuterRef, Subquery
from django.utils import timezone
from zoneinfo import ZoneInfo
from Library.models import Student, Faculty
from .models import LabSeat, LabSession

BANGLADESH_TZ = ZoneInfo('Asia/Dhaka')


def canonical_lab_seats(base_queryset=None):
    """Return one canonical seat row per PC number, keeping the oldest row and excluding empty spaces."""
    queryset = base_queryset if base_queryset is not None else LabSeat.objects.filter(is_space=False)
    canonical_ids = LabSeat.objects.filter(
        is_space=False,
        pc_no=OuterRef('pc_no')
    ).order_by('id').values('id')[:1]
    return queryset.filter(id=Subquery(canonical_ids))


def cleanup_duplicate_lab_seats():
    """Merge duplicate PC rows onto one canonical seat and remove extras."""
    duplicate_pc_nos = (
        LabSeat.objects.values('pc_no')
        .annotate(seat_count=Count('id'))
        .filter(seat_count__gt=1)
        .values_list('pc_no', flat=True)
    )

    for pc_no in duplicate_pc_nos:
        with transaction.atomic():
            seats = list(LabSeat.objects.filter(pc_no=pc_no).order_by('id'))
            if len(seats) < 2:
                continue

            canonical_seat = seats[0]
            duplicate_seats = seats[1:]
            duplicate_ids = [seat.id for seat in duplicate_seats]

            if LabSession.objects.filter(seat_id__in=duplicate_ids, status='Active').exists():
                canonical_status = 'Reserved'
            elif any(seat.status == 'Reserved' for seat in seats):
                canonical_status = 'Reserved'
            elif any(seat.status == 'Maintenance' for seat in seats):
                canonical_status = 'Maintenance'
            else:
                canonical_status = 'Available'

            LabSession.objects.filter(seat_id__in=duplicate_ids).update(seat=canonical_seat)
            LabSeat.objects.filter(id__in=duplicate_ids).delete()

            if canonical_seat.status != canonical_status:
                canonical_seat.status = canonical_status
                canonical_seat.save(update_fields=['status'])


def _is_before_today_in_bd(dt, bd_today):
    if not dt:
        return False
    return timezone.localtime(dt, BANGLADESH_TZ).date() < bd_today


def enforce_midnight_lab_session_policy():
    """Block students with previous-day active lab sessions and free reserved seats for the new day."""
    now = timezone.now()
    bd_today = timezone.localtime(now, BANGLADESH_TZ).date()

    students_to_block = set()

    active_sessions = LabSession.objects.select_related('content_type', 'student', 'seat').filter(
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
            LabSeat.objects.filter(id=session.seat_id, status='Reserved').update(status='Available')

    if students_to_block:
        Student.objects.filter(id__in=students_to_block).update(
            is_blocked=True,
            blocked_at=now,
            block_reason='Auto-blocked: did not exit Computer Lab before 12:00 AM (Bangladesh time).',
        )

    # Release any stale reserved seats without an active session
    active_seat_ids = LabSession.objects.filter(
        status='Active',
        end_time__isnull=True,
        seat_id__isnull=False,
    ).values_list('seat_id', flat=True)

    stale_reserved_qs = LabSeat.objects.filter(status='Reserved')
    if active_seat_ids:
        stale_reserved_qs = stale_reserved_qs.exclude(id__in=active_seat_ids)
    stale_reserved_qs.update(status='Available')


def get_user_by_id(user_id):
    """Find student or faculty by ID number"""
    student = Student.objects.filter(id_no=user_id).first()
    if student:
        return student, 'student'

    faculty = Faculty.objects.filter(id_no=user_id).first()
    if faculty:
        return faculty, 'faculty'

    return None, None
