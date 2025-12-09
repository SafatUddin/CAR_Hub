from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    whatsapp_number = forms.CharField(max_length=20, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'whatsapp_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Split name into first and last name
        name_parts = self.cleaned_data['name'].strip().split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, whatsapp_number=self.cleaned_data['whatsapp_number'])
        return user

class EditProfileForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=254, required=True)
    whatsapp_number = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            # Combine first and last name
            full_name = f"{self.instance.first_name} {self.instance.last_name}".strip()
            self.fields['name'].initial = full_name
            self.fields['email'].initial = self.instance.email
            if hasattr(self.instance, 'profile'):
                self.fields['whatsapp_number'].initial = self.instance.profile.whatsapp_number

    def save(self, commit=True):
        if not self.instance:
            return None
        
        # Split name into first and last name
        name_parts = self.cleaned_data['name'].strip().split(' ', 1)
        self.instance.first_name = name_parts[0]
        self.instance.last_name = name_parts[1] if len(name_parts) > 1 else ''
        self.instance.email = self.cleaned_data['email']
        
        if commit:
            self.instance.save()
            profile, created = UserProfile.objects.get_or_create(user=self.instance)
            profile.whatsapp_number = self.cleaned_data['whatsapp_number']
            profile.save()
        return self.instance
