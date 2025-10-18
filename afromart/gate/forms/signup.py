import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class SignUp(forms.Form):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email address"}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if (length := len(username)) < 8 or length > 21:
            raise ValidationError(
                "Username needs to be at least 8 and at most 21 characters."
            )

        if not re.match(pattern=r"^[a-zA-Z0-9]+$", string=username, flags=re.ASCII):
            raise ValidationError("Username can only contain letters and numbers.")

        return username

    def clean_password(self):
        MAX_LENGTH = 21

        password = self.cleaned_data["password"]

        # Check maximum length
        if len(password) > MAX_LENGTH:
            raise forms.ValidationError(
                f"Password must not exceed {MAX_LENGTH} characters."
            )

        validate_password(password=password)

        return password

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        domain = email.split("@")[1]

        if domain not in ("gmail.com", "googlemail.com"):
            raise ValidationError("Please use your GMail email address.")

        return email
