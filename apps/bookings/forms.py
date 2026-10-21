from django import forms
from .models import BookingRequest

class BookingRequestForm(forms.ModelForm):
    honeypot = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "tabindex": "-1", "aria-hidden": "true"}
        ),
    )

    def clean_honeypot(self):
        value = self.cleaned_data.get("honeypot", "")
        if value:
            raise forms.ValidationError("Invalid submission.")
        return ""

    class Meta:
        model = BookingRequest
        fields = [
            'full_name', 'email', 'phone', 'company_or_project',
            'service_requested', 'studio_space', 'preferred_date',
            'estimated_budget', 'project_details'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name *',
                'required': True,
                'id': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address *',
                'required': True,
                'id': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number *',
                'required': True,
                'id': 'phone'
            }),
            'company_or_project': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company / Brand Name',
                'id': 'company'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'date'
            }),
            'estimated_budget': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated Budget (e.g. R1,300 - R5,000)',
                'id': 'budget'
            }),
            'project_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about your visual concept, equipment needs, or timeline *',
                'required': True,
                'id': 'message'
            }),
        }
