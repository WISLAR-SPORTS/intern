# internships/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Internship
from students.models import Student
from students.models import Notification


@receiver(post_save, sender=Internship)
def internship_created_notification(
    sender,
    instance,
    created,
    **kwargs
):

    if not created:
        return

    students = Student.objects.all()

    notifications = [
        Notification(
            student=student,
            notification_type="internship",
            action="new_internship",
            title="New Internship Available",
            message=(
                f"{instance.title} has been posted by "
                f"{instance.company.company_name}."
            ),
            internship=instance,
        )
        for student in students
    ]

    if notifications:
        Notification.objects.bulk_create(notifications)
