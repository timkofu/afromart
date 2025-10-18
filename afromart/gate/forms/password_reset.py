from django import forms
from django.contrib.auth.password_validation import validate_password


class PasswordResetActionForm(forms.Form):
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password ...",
            }
        ),
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password ...",
            }
        ),
    )

    def clean_password2(self) -> str:
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        validate_password(password=password2)

        return password2
