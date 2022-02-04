from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from stucon.models import Student, Cohort, Team

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ["source", "candidate_number", "cohort", "status"]


class StudentImageForm(ModelForm):
    class Meta:
        model = Student
        fields = ["image"]


class StatusForm(ModelForm):
    class Meta:
        model = Student
        fields = ["status"]


class NewStudentUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
        ]
