from django import forms
from .models import InternshipField


class InternshipApplicationForm(forms.Form):

    cover_letter = forms.CharField(
        label="Cover Letter",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Write your cover letter..."
            }
        )
    )

    def __init__(self, *args, internship=None, **kwargs):

        super().__init__(*args, **kwargs)

        if not internship:
            return

        fields = internship.custom_fields.all().order_by(
            "order",
            "id"
        )

        for field in fields:

            field_name = f"field_{field.id}"

            common = {
                "label": field.label,
                "required": field.required,
            }

            if field.field_type == "text":

                form_field = forms.CharField(
                    **common,
                    widget=forms.TextInput(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            elif field.field_type == "textarea":

                form_field = forms.CharField(
                    **common,
                    widget=forms.Textarea(
                        attrs={
                            "class": "form-control",
                            "rows": 5
                        }
                    )
                )

            elif field.field_type == "number":

                form_field = forms.IntegerField(
                    **common,
                    widget=forms.NumberInput(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            elif field.field_type == "email":

                form_field = forms.EmailField(
                    **common,
                    widget=forms.EmailInput(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            elif field.field_type == "url":

                form_field = forms.URLField(
                    **common,
                    widget=forms.URLInput(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            elif field.field_type == "date":

                form_field = forms.DateField(
                    **common,
                    widget=forms.DateInput(
                        attrs={
                            "class": "form-control",
                            "type": "date"
                        }
                    )
                )

            elif field.field_type == "file":

                form_field = forms.FileField(
                    **common,
                    widget=forms.ClearableFileInput(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            elif field.field_type == "checkbox":

                form_field = forms.BooleanField(
                    **common,
                    widget=forms.CheckboxInput(
                        attrs={
                            "class": "form-checkbox"
                        }
                    )
                )

            elif field.field_type == "select":

                options = [
                    option.strip()
                    for option in field.options.split(",")
                    if option.strip()
                ]

                choices = [
                    (option, option)
                    for option in options
                ]

                form_field = forms.ChoiceField(
                    **common,
                    choices=choices,
                    widget=forms.Select(
                        attrs={
                            "class": "form-control"
                        }
                    )
                )

            else:
                continue

            self.fields[field_name] = form_field
from django import forms


class ApplicantEmailForm(forms.Form):

    subject = forms.CharField(
        max_length=200,
        label="Email Subject",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Congratulations on your internship application"
            }
        )
    )

    message = forms.CharField(
        label="Email Message",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 12,
                "placeholder": "Write your message to the selected applicants..."
            }
        )
    )
