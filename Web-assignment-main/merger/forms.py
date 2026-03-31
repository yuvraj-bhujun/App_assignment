from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



class SignUpForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        error_messages={'required': 'First name is required.'}
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        error_messages={'required': 'Last name is required.'}
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        error_messages={'required': 'Phone number is required.'}
    )
    
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={'required': 'Username is required.'}
    )
    
    password = forms.CharField(
        min_length=8,
        required=True,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    
    confirm_password = forms.CharField(
        required=True,
        error_messages={'required': 'Please confirm your password.'}
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        if phone and len(phone) < 8:
            raise forms.ValidationError("Phone number must be at least 8 digits long.")
        return phone
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)  
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            phone=cleaned_data['phone_number']
        )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    password = forms.CharField(
        required=True,
        error_messages={'required': 'Password is required.'}
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """Validate email and password combination"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, 
                username=email, 
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password!")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            elif hasattr(self.user_cache, 'is_suspended') and self.user_cache.is_suspended:
                raise forms.ValidationError("This account has been suspended.")

        return cleaned_data

    def get_user(self):
        return self.user_cache
from .models import Payment



class PaymentForm(forms.Form):

    card_number = forms.CharField(
        max_length=19,
        min_length=19,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9123 1234'}),
        label="Card Number"
    )

    card_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'}),
        label="Card Name"
    )

    expiry_date = forms.CharField(
        max_length=5,
        min_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}),
        label="Expiry Date"
    )

    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={'placeholder': '123'}),
        label="CVV"
    )

    # VALIDATIONS
    def clean_card_number(self):
        number = self.cleaned_data.get('card_number', '')

        # Check exact length including spaces
        if len(number) != 19:
            raise forms.ValidationError("Card number must be 16 digits with spaces (format: 1234 5678 9123 1234).")

        # Check pattern: groups of 4 digits separated by spaces
        import re
        if not re.fullmatch(r'\d{4} \d{4} \d{4} \d{4}', number):
            raise forms.ValidationError("Card number format must be 1234 5678 9123 1234.")

        return number


    def clean_card_name(self):
        name = self.cleaned_data.get('card_name', '')
        if not all(c.isalpha() or c.isspace() for c in name):
            raise forms.ValidationError("Name must contain only letters and spaces.")
        if len(name) < 2:
            raise forms.ValidationError("Name is too short.")
        return name

    def clean_expiry_date(self):
        value = self.cleaned_data['expiry_date']

        # Check format MM/YY
        if len(value) != 5 or value[2] != '/':
            raise forms.ValidationError("Expiry must be in MM/YY format.")

        mm, yy = value.split('/')

        if not (mm.isdigit() and yy.isdigit()):
            raise forms.ValidationError("Invalid expiry date.")

        month = int(mm)
        year = int("20" + yy)

        if not 1 <= month <= 12:
            raise forms.ValidationError("Month must be between 01 and 12.")

        # Current date
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # Max year allowed (real banking cards)
        max_year = current_year + 10

        # Year range check
        if year < current_year or year > max_year:
            raise forms.ValidationError("Expiry year is not valid.")

        # Past date check
        if year == current_year and month <= current_month:
            raise forms.ValidationError("Expiry date cannot be in the past.")

        return value



    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv', '')
        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError("CVV must be exactly 3 digits.")
        return cvv


ACTIVITY_TYPE_CHOICES = [
    ('Scuba diving', 'Scuba diving'),
    ('Catamaran', 'Catamaran'),
    ('Speed boat', 'Speed boat'),
    ('Water ski', 'Water ski'),
    ('Dolphin watching', 'Dolphin watching'),
]


class ActivityForm(forms.Form):
    """
    Form for validating activity data from POST requests.
    This form is used for backend validation only.
    The HTML template uses manual form inputs.
    """
    
    # Hidden field for edit mode
    activity_id = forms.IntegerField(required=False)
    
    # Activity details
    name = forms.CharField(
        max_length=200,
        required=True,
        error_messages={'required': 'Activity name is required'}
    )
    
    activity_type = forms.ChoiceField(
        choices=ACTIVITY_TYPE_CHOICES,
        required=True
    )
    
    location = forms.CharField(
        max_length=200,
        required=False
    )
    
    description = forms.CharField(
        required=True,
        error_messages={'required': 'Description is required'}
    )
    
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0,
        error_messages={'required': 'Price is required'}
    )
    
    duration = forms.CharField(
        max_length=100,
        required=False
    )
    
    max_participants = forms.IntegerField(
        required=False,
        min_value=1
    )
    
    # Images field (for multiple file upload)
    images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'allow_multiple_selected': True
        })
    )
    
    def clean_price(self):
        """Ensure price is not negative"""
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    
    def clean_max_participants(self):
        """Ensure max participants is at least 1 if provided"""
        max_participants = self.cleaned_data.get('max_participants')
        if max_participants is not None and max_participants < 1:
            raise forms.ValidationError('Max participants must be at least 1.')
        return max_participants


class ContactForm(forms.Form):
    """
    Form for contact page submissions
    """
    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Name is required.'}
    )
    
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        error_messages={'required': 'Subject is required.'}
    )
    
    message = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': 'Message is required.'}
    )
    
    def clean_message(self):
        """Ensure message is at least 10 characters"""
        message = self.cleaned_data.get('message')
        if message and len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message
