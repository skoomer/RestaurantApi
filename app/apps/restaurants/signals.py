from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Review


@receiver(pre_delete, sender=Review)
def send_email_review_deleted_notification(sender, instance, **kwargs):
    """Send notification to user after their review has been deleted"""

    user_email = instance.reviewer.email
    send_mail(
        subject="Your review has been deleted",
        message=f"Your review {instance.message} of {instance.restaurant} has been deleted.",
        from_email=None,
        recipient_list=[user_email],
    )
