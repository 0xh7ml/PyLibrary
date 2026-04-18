from django.db import transaction
from django.db.models import Count, OuterRef, Subquery

from Library.models import ELibrarySession, ElibrarySeat


def canonical_elibrary_seats(base_queryset=None):
    """Return one canonical seat row per PC number, keeping the oldest row."""
    queryset = base_queryset if base_queryset is not None else ElibrarySeat.objects.all()
    canonical_ids = ElibrarySeat.objects.filter(
        pc_no=OuterRef('pc_no')
    ).order_by('id').values('id')[:1]
    return queryset.filter(id=Subquery(canonical_ids))


def cleanup_duplicate_elibrary_seats():
    """Merge duplicate PC rows onto one canonical seat and remove extras."""
    duplicate_pc_nos = (
        ElibrarySeat.objects.values('pc_no')
        .annotate(seat_count=Count('id'))
        .filter(seat_count__gt=1)
        .values_list('pc_no', flat=True)
    )

    for pc_no in duplicate_pc_nos:
        with transaction.atomic():
            seats = list(ElibrarySeat.objects.filter(pc_no=pc_no).order_by('id'))
            if len(seats) < 2:
                continue

            canonical_seat = seats[0]
            duplicate_seats = seats[1:]
            duplicate_ids = [seat.id for seat in duplicate_seats]

            if ELibrarySession.objects.filter(seat_id__in=duplicate_ids, status='Active').exists():
                canonical_status = 'Reserved'
            elif any(seat.status == 'Reserved' for seat in seats):
                canonical_status = 'Reserved'
            elif any(seat.status == 'Maintenance' for seat in seats):
                canonical_status = 'Maintenance'
            else:
                canonical_status = 'Available'

            ELibrarySession.objects.filter(seat_id__in=duplicate_ids).update(seat=canonical_seat)
            ElibrarySeat.objects.filter(id__in=duplicate_ids).delete()

            if canonical_seat.status != canonical_status:
                canonical_seat.status = canonical_status
                canonical_seat.save(update_fields=['status'])
