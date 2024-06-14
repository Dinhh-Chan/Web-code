from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'difficulty', 'tags']
class CodeSubmissionForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('Python', 'Python'),
        ('C', 'C'),
        ('C++', 'C++'),
    ]
    code = forms.CharField(widget=forms.Textarea, label='Code')
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label='Language')
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})