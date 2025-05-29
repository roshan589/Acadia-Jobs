from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, CreateJob, ApplyJob
# forms.py (add this import)
from django.contrib.auth.forms import SetPasswordForm


from django.contrib.auth import get_user_model


User = get_user_model()
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class CreateParentForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'parent_expiry_date']

class VerificationCode(forms.Form):
    verification_code = forms.CharField(max_length=6)


class JobPost(forms.ModelForm):
    class Meta:
        model = CreateJob
        fields = ['title', 'position', 'companyName','jobType', 'location', 'applicationDeadline', 'description']



class JobApplyForm(forms.ModelForm):
    class Meta:
        model = ApplyJob
        fields = ['first_name', 'last_name', 'email','address','city','state', 'phone_no', 'availability_start_date', 'availability_end_date', 'resume']
        resume = forms.FileField(required=True)


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = ApplyJob
        fields = ['job_status']




class JobFilterForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, label='Search by Job Title')
    posted_on = forms.DateField(required=False, widget=forms.SelectDateWidget, label='Date Posted')
