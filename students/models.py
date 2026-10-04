from django.db import models
from django.conf import settings
import secrets
from cloudinary.models import CloudinaryField



class University(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="university",
    )
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    website = models.URLField(
        blank=True,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    logo = models.ImageField(
        upload_to="universities/",
        blank=True,
        null=True,
    )
    verified = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name



class StudentVerified(models.Model):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="verified_students"
    )

    full_name = models.CharField(
        max_length=200
    )

    registration_number = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["university", "registration_number"],
                name="unique_student_registration_per_university"
            )
        ]

    def __str__(self):
        return f"{self.full_name} - {self.registration_number}"


class Student(models.Model):

    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="student",
)
    university = models.ForeignKey(
        University,
        on_delete=models.PROTECT,
        related_name="students"
    )

    registration_number = models.CharField(
        max_length=50,
        unique=True
    )


    course = models.CharField(
        max_length=100,
        null=True,
            blank=True,
    )


    year_of_study = models.IntegerField(
    null=True,
    blank=True,
)



    phone = models.CharField(
        max_length=20,
        null=True,
            blank=True,
    )


    skills = models.TextField(
        
        null=True,
            blank=True,
    )


    profile_picture = CloudinaryField(
        "photo",
        folder="students/photos/",
        blank=True,
        null=True
    )


    def __str__(self):

        return self.user.get_full_name()
    
from django.db import models
from students.models import Student
from internships.models import Application, Internship


class Notification(models.Model):

    TYPE_CHOICES = (
        ("application", "Application"),
        ("internship", "Internship"),
        ("system", "System"),
    )

    ACTION_CHOICES = (
        ("application_submitted", "Application Submitted"),
        ("application_shortlisted", "Application Shortlisted"),
        ("application_accepted", "Application Accepted"),
        ("application_rejected", "Application Rejected"),
        ("new_internship", "New Internship"),
        ("system", "System"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    action = models.CharField(
        max_length=40,
        choices=ACTION_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    is_read = models.BooleanField(
        default=False
    )

    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.title}"
