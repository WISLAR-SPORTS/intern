from django import forms
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "registration_number",
            "course",
            "year_of_study",
            "phone",
            "skills",
            "profile_picture",
        ]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Current Password"
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    "The new passwords do not match."
                )

        return cleaned_data
# students/forms.py

from django import forms


from django import forms


class StudentVerifiedUploadForm(forms.Form):
    file = forms.FileField(
        label="Student List",
        help_text=(
            "Upload an Excel (.xlsx) or PDF file containing "
            "Student Number and Full Name."
        ),
        widget=forms.FileInput(
            attrs={
                "accept": ".xlsx,.pdf",
            }
        ),
    )

    def clean_file(self):
        file = self.cleaned_data["file"]

        allowed_extensions = (".xlsx", ".pdf")
        filename = file.name.lower()

        if not filename.endswith(allowed_extensions):
            raise forms.ValidationError(
                "Invalid file type. Please upload an Excel (.xlsx) "
                "or PDF (.pdf) file."
            )

        return file
