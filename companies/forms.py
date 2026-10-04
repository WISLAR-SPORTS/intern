from django import forms
from internships.models import Application


class ApplicationReviewForm(forms.ModelForm):

    class Meta:
        model = Application

        fields = (
            "score",
            "reviewer_notes",
            "status",
        )

        widgets = {
            "score": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 100,
                    "step": "0.01",
                }
            ),

            "reviewer_notes": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Add internal review notes..."
                }
            ),

            "status": forms.Select(),
        }
