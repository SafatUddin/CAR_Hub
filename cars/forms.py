from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
import re
import dns.resolver
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

def validate_email_domain(email):
    """Validate email by checking if domain has MX records"""
    try:
        domain = email.split('@')[1]
        # Check if domain has MX records (mail servers)
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False
    except Exception:
        # If DNS check fails for any other reason, allow it (don't block valid emails due to DNS issues)
        return True

def validate_whatsapp_number(number):
    """Validate WhatsApp number format with country code"""
    if not number:
        return True, ""
    
    clean_number = number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Must start with + and have 10-15 digits
    if not re.match(r'^\+\d{10,15}$', clean_number):
        return False, "WhatsApp number must start with + followed by country code and phone number (e.g., +8801712345678)"
    
    # Check for common country codes to ensure it's a valid format
    # Bangladesh: +880, India: +91, USA: +1, UK: +44, etc.
    common_country_codes = ['+1', '+7', '+20', '+27', '+30', '+31', '+32', '+33', '+34', '+36', '+39', '+40', 
                           '+41', '+43', '+44', '+45', '+46', '+47', '+48', '+49', '+51', '+52', '+53', '+54',
                           '+55', '+56', '+57', '+58', '+60', '+61', '+62', '+63', '+64', '+65', '+66', '+81',
                           '+82', '+84', '+86', '+90', '+91', '+92', '+93', '+94', '+95', '+98', '+212', '+213',
                           '+216', '+218', '+220', '+221', '+222', '+223', '+224', '+225', '+226', '+227', '+228',
                           '+229', '+230', '+231', '+232', '+233', '+234', '+235', '+236', '+237', '+238', '+239',
                           '+240', '+241', '+242', '+243', '+244', '+245', '+246', '+248', '+249', '+250', '+251',
                           '+252', '+253', '+254', '+255', '+256', '+257', '+258', '+260', '+261', '+262', '+263',
                           '+264', '+265', '+266', '+267', '+268', '+269', '+290', '+291', '+297', '+298', '+299',
                           '+350', '+351', '+352', '+353', '+354', '+355', '+356', '+357', '+358', '+359', '+370',
                           '+371', '+372', '+373', '+374', '+375', '+376', '+377', '+378', '+380', '+381', '+382',
                           '+383', '+385', '+386', '+387', '+389', '+420', '+421', '+423', '+500', '+501', '+502',
                           '+503', '+504', '+505', '+506', '+507', '+508', '+509', '+590', '+591', '+592', '+593',
                           '+594', '+595', '+596', '+597', '+598', '+599', '+670', '+672', '+673', '+674', '+675',
                           '+676', '+677', '+678', '+679', '+680', '+681', '+682', '+683', '+685', '+686', '+687',
                           '+688', '+689', '+690', '+691', '+692', '+850', '+852', '+853', '+855', '+856', '+870',
                           '+880', '+886', '+960', '+961', '+962', '+963', '+964', '+965', '+966', '+967', '+968',
                           '+970', '+971', '+972', '+973', '+974', '+975', '+976', '+977', '+992', '+993', '+994',
                           '+995', '+996', '+998']
    
    has_valid_code = any(clean_number.startswith(code) for code in common_country_codes)
    if not has_valid_code:
        return False, "Please use a valid country code (e.g., +880 for Bangladesh, +91 for India, +1 for USA/Canada)"
    
    return True, ""

class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    whatsapp_number = forms.CharField(max_length=20, required=False, help_text='Optional. Format: +8801XXXXXXXXX')

    class Meta:
        model = User
        fields = ('name', 'email', 'whatsapp_number', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        # Validate email format
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        # Check if domain has valid MX records (can receive emails)
        if not validate_email_domain(email):
            raise forms.ValidationError("This email domain does not exist or cannot receive emails. Please check your email address.")
        
        return email
    
    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number', '').strip()
        if whatsapp:
            is_valid, error_msg = validate_whatsapp_number(whatsapp)
            if not is_valid:
                raise forms.ValidationError(error_msg)
        return whatsapp

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use full name as first_name
        user.first_name = self.cleaned_data['name'].strip()
        user.email = self.cleaned_data['email']
        
        # Generate unique username from name
        base_username = name_parts[0].lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        
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
            # Use first_name as full name
            self.fields['name'].initial = self.instance.first_name
            self.fields['email'].initial = self.instance.email
            if hasattr(self.instance, 'profile'):
                self.fields['whatsapp_number'].initial = self.instance.profile.whatsapp_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is taken by another user
        if self.instance and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This email is already registered by another user.")
        
        # Validate email format
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        # Check if domain has valid MX records (can receive emails)
        if not validate_email_domain(email):
            raise forms.ValidationError("This email domain does not exist or cannot receive emails. Please check your email address.")
        
        return email
    
    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number', '').strip()
        if whatsapp:
            is_valid, error_msg = validate_whatsapp_number(whatsapp)
            if not is_valid:
                raise forms.ValidationError(error_msg)
        return whatsapp

    def save(self, commit=True):
        if not self.instance:
            return None
        
        # Use full name as first_name
        self.instance.first_name = self.cleaned_data['name'].strip()
        self.instance.email = self.cleaned_data['email']
        
        if commit:
            self.instance.save()
            profile, created = UserProfile.objects.get_or_create(user=self.instance)
            profile.whatsapp_number = self.cleaned_data['whatsapp_number']
            profile.save()
        return self.instance
