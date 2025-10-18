from django import forms


class Email(forms.Form):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address ...",
            }
        ),
    )
