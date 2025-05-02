from django import forms
from django.core.exceptions import ValidationError
import re

from .models import Client, Comment, ClientFile

from django import forms
from .models import Client

class AddClientForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Company Name"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "E-mail"})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Phone Number"})
    )
    service = forms.ChoiceField(
        choices=Client.SERVICE_CHOICES,
        widget=forms.Select(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100"})
    )
    contacted_person_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Contacted Person"})
    )
    custom_service = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Other (Specify)"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": "5", "class": "w-full bg-gray-100 rounded-xl", "placeholder": "Description"})
    )
    approved_cost = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Approved Cost"})
    )
    gst_service_percentage = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "GST/Service (%)"})
    )
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    working_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "w-full py-4 px-6 rounded-xl bg-gray-100", "placeholder": "Working Days"})
    )

    class Meta:
        model = Client
        fields = '__all__'


    def clean_cost_range(self):
        cost_range = self.cleaned_data.get('cost_range')
        if not cost_range:
            return cost_range
            
        # Check if it matches the pattern (e.g., "200000-300000")
        pattern = r'^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*$'
        match = re.match(pattern, cost_range)
        
        if match:
            min_cost = float(match.group(1))
            max_cost = float(match.group(2))
            
            if min_cost > max_cost:
                raise ValidationError("Minimum cost cannot be greater than maximum cost.")
                
            # Store these values to be used in the save method
            self.min_cost = min_cost
            self.max_cost = max_cost
            return cost_range
        else:
            raise ValidationError("Invalid cost range format. Use format: 'min-max' (e.g., '200000-300000')")
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set min_cost and max_cost if cost_range was provided
        if hasattr(self, 'min_cost') and hasattr(self, 'max_cost'):
            instance.min_cost = self.min_cost
            instance.max_cost = self.max_cost
        
        if commit:
            instance.save()
        return instance


class AddCommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows":"5", "class": "w-full bg-gray-100 rounded-xl"})
    )

    class Meta:
        model = Comment
        fields = ('content',)

class AddFileForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment about this file...'}),
        required=False
    )
    
    class Meta:
        model = ClientFile
        fields = ('file', 'comment',)