from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_ticket_created_email(ticket):
    """
    Send email notification to admin when a new ticket/issue is created.
    Includes the student ID, issue details, and request body.
    """
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if not admin_email:
            logger.warning('ADMIN_EMAIL not configured, skipping ticket creation email.')
            return

        subject = f'New Issue #{ticket.id} - {ticket.title}'

        creator_name = ticket.creator_name
        creator_id = ticket.creator_id_no
        creator_type = ticket.creator_type

        body = (
            f"A new issue has been reported.\n\n"
            f"Ticket ID: #{ticket.id}\n"
            f"Title: {ticket.title}\n"
            f"Issue Type: {ticket.get_issue_type_display()}\n"
            f"Status: {ticket.get_status_display()}\n\n"
            f"Reported By:\n"
            f"  Name: {creator_name}\n"
            f"  ID: {creator_id}\n"
            f"  Type: {creator_type}\n\n"
            f"Description:\n{ticket.description}\n\n"
            f"Created At: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        logger.info(f'Ticket creation email sent to {admin_email} for ticket #{ticket.id}')
    except Exception as e:
        logger.error(f'Failed to send ticket creation email for ticket #{ticket.id}: {str(e)}')


def send_ticket_status_update_email(ticket):
    """
    Send email notification to the student/faculty when ticket status is updated.
    Subject: Issue #ID - Title
    Body: The updated status
    """
    try:
        # Get the user's email from the generic FK or legacy field
        user_email = None
        if ticket.created_by and hasattr(ticket.created_by, 'email'):
            user_email = ticket.created_by.email
        elif ticket.issued_by and hasattr(ticket.issued_by, 'email'):
            user_email = ticket.issued_by.email

        if not user_email:
            logger.warning(
                f'No email found for ticket #{ticket.id} creator, skipping status update email.'
            )
            return

        subject = f'Issue #{ticket.id} - {ticket.title}'

        body = (
            f"Your issue status has been updated.\n\n"
            f"Ticket ID: #{ticket.id}\n"
            f"Title: {ticket.title}\n"
            f"New Status: {ticket.get_status_display()}\n\n"
            f"If you have any questions, please contact the library admin.\n"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f'Status update email sent to {user_email} for ticket #{ticket.id}')
    except Exception as e:
        logger.error(f'Failed to send status update email for ticket #{ticket.id}: {str(e)}')
