from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Student
from .serializers import StudentSerializer



class MyProfileView(RetrieveAPIView):

    serializer_class = StudentSerializer

    permission_classes = [
        IsAuthenticated
    ]


    def get_object(self):

        return Student.objects.get(
            user=self.request.user
        )
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from .forms import (
    StudentProfileForm,
    UserProfileForm,
    PasswordChangeForm,
)

User = get_user_model()

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def student_profile(request):

    if request.user.role != "student":
        return redirect("home")

    student = request.user.student

    context = {
        "student": student,
        "user": request.user,
    }

    return render(
        request,
        "students/profile.html",
        context
    )


@login_required
def edit_profile(request):

    # Make sure the logged-in user is a student
    if request.user.role != "student":
        return redirect("home")

    student = request.user.student
    user = request.user

    if request.method == "POST":

        student_form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=student
        )

        user_form = UserProfileForm(
            request.POST,
            instance=user
        )

        password_form = PasswordChangeForm(request.POST)

        # Check which form was submitted
        form_type = request.POST.get("form_type")

        if form_type == "profile":

            if student_form.is_valid() and user_form.is_valid():

                student_form.save()
                user_form.save()

                messages.success(
                    request,
                    "Your profile has been updated successfully."
                )

                return redirect("students:edit_profile")

        elif form_type == "password":

            if password_form.is_valid():

                current_password = password_form.cleaned_data[
                    "current_password"
                ]

                new_password = password_form.cleaned_data[
                    "new_password"
                ]

                # Check current password
                if not user.check_password(current_password):

                    password_form.add_error(
                        "current_password",
                        "Your current password is incorrect."
                    )

                else:

                    user.set_password(new_password)
                    user.save()

                    messages.success(
                        request,
                        "Your password has been changed successfully."
                    )

                    # Important: keep the user logged in
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, user)

                    return redirect("students:edit_profile")

    else:

        student_form = StudentProfileForm(
            instance=student
        )

        user_form = UserProfileForm(
            instance=user
        )

        password_form = PasswordChangeForm()

    context = {
        "student_form": student_form,
        "user_form": user_form,
        "password_form": password_form,
    }

    return render(
        request,
        "students/edit_profile.html",
        context
    )
# views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from .models import (
    Student,
    StudentVerified,
    Application,
)



from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from .models import Student, StudentVerified, Application


def university_user_required(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.is_staff
        and (
            user.is_superuser
            or user.role == "university"
        )
    )


@staff_member_required
@user_passes_test(university_user_required)
def university_dashboard(request):

    user = request.user

    if user.is_superuser:
        university = None
    else:
        university = user.university

    if university:

        verified_students = StudentVerified.objects.filter(
            university=university
        )

        students = Student.objects.filter(
            university=university
        )

        applications = Application.objects.filter(
            student__university=university
        )

    else:

        verified_students = StudentVerified.objects.all()

        students = Student.objects.all()

        applications = Application.objects.all()

    total_verified_students = verified_students.count()
    total_students = students.count()
    total_applications = applications.count()

    pending_applications = applications.filter(
        status="pending"
    ).count()

    shortlisted_applications = applications.filter(
        status="shortlisted"
    ).count()

    accepted_applications = applications.filter(
        status="accepted"
    ).count()

    rejected_applications = applications.filter(
        status="rejected"
    ).count()

    recent_applications = (
        applications
        .select_related(
            "student",
            "internship",
            "internship__company",
        )
        .order_by("-applied_date")[:10]
    )

    context = {
        "title": "University Dashboard",
        "university": university,

        "total_verified_students": total_verified_students,
        "total_students": total_students,

        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "shortlisted_applications": shortlisted_applications,
        "accepted_applications": accepted_applications,
        "rejected_applications": rejected_applications,

        "recent_applications": recent_applications,
    }

    return render(
        request,
        "dashboard/university_dashboard.html",
        context,
    )
