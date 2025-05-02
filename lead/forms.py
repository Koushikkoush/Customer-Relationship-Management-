from django import forms

from .models import Lead, Comment, LeadFile

class AddLeadForm(forms.ModelForm):
    client_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_client_name',
            'placeholder': 'Lead Name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email'
        })
    )

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_phone_number'
        })
    )

    service = forms.ChoiceField(
        choices=Lead.SERVICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_service'
        })
    )

    custom_service = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_custom_service',
            'placeholder': 'Specify other service'
        })
    )

    class Meta:
        model = Lead
        fields = ('client_name', 'email', 'phone_number', 'service', 'custom_service', 'description', 'priority', 'status')

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AddFileForm(forms.ModelForm):
    class Meta:
        model = LeadFile
        fields = ('file',)