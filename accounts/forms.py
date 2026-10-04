from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from students.models import Student, University
from companies.models import Company

User = get_user_model()


from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "autocomplete": "email",
            }
        ),
    )
class PasswordLoginForm(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )
class OTPVerificationForm(forms.Form):

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter 6-digit code",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "maxlength": "6",
            }
        ),
    )


class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
    )
    username = forms.CharField(
        max_length=150,
        required=True,
    )
    email = forms.EmailField(
        required=True,
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )
    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        required=True,
    )
    registration_number = forms.CharField(
        max_length=50,
        required=True,
        label="Registration Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your registration number",
            }
        ),
    )
    university = forms.ModelChoiceField(
    queryset=University.objects.all(),
    required=True,
    empty_label="Select your university",
)

   
    

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_registration_number(self):
        registration_number = self.cleaned_data["registration_number"]
        university = self.cleaned_data.get("university")

        if university and Student.objects.filter(
            university=university,
            registration_number=registration_number,
        ).exists():
            raise forms.ValidationError(
                "This registration number already exists at this university."
            )

        return registration_number

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class CompanyRegistrationForm(forms.Form):
    company_name = forms.CharField(
        max_length=200,
        required=True,
    )
    username = forms.CharField(
        max_length=150,
        required=True,
    )
    email = forms.EmailField(
        required=True,
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
    )
    location = forms.CharField(
        max_length=200,
        required=True,
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea,
    )
    website = forms.URLField(
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class UniversityRegistrationForm(forms.Form):
    university_name = forms.CharField(
        max_length=200,
        required=True,
        label="University Name",
    )
    website = forms.URLField(
        required=False,
        label="University Website",
    )
    logo = forms.ImageField(
        required=False,
        label="University Logo",
    )
    username = forms.CharField(
        max_length=150,
        required=True,
    )
    email = forms.EmailField(
        required=True,
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )

    def clean_university_name(self):
        university_name = self.cleaned_data["university_name"]

        if University.objects.filter(
            name__iexact=university_name
        ).exists():
            raise forms.ValidationError(
                "This university is already registered."
            )

        return university_name

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data
