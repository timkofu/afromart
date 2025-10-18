import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import View

from ..forms import Email


class PasswordResetRequest(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request=request,
            template_name="gate/password_reset_request.html",
            context={"form": Email()},
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        email_form = Email(data=request.POST)

        if email_form.is_valid():
            email = email_form.cleaned_data["email"]

            if user := User.objects.filter(email=email, is_active=True).first():
                user_pk_hash = hashlib.sha256(
                    data=f"{user.pk}".encode(encoding="utf-8")
                ).hexdigest()

                message = render_to_string(
                    request=request,
                    template_name="gate/email/password_reset_request.tmpl",
                    context={
                        "email": email,
                        "password_reset_request_link": request.build_absolute_uri(
                            reverse_lazy(
                                viewname="gate:password_reset",
                                kwargs={"user_pk_hash": user_pk_hash},
                            ),  # pyright: ignore[reportArgumentType]
                        ),
                    },
                )

                cache_details = {  # pyright: ignore[reportUnknownVariableType]
                    "key": f"passwordreset_{user_pk_hash}",
                    "value": user.pk,
                    "timeout": 5 * 60,  # 5 minutes
                }

                if not cache.get(key=str(cache_details["key"])):  # pyright: ignore[reportUnknownArgumentType]
                    settings.THREAD_POOL.submit(
                        send_mail,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        subject="Password Reset Link",
                        message=message,
                        fail_silently=False,
                    )

                    cache.set(**cache_details)  # pyright: ignore[reportUnknownArgumentType]

                    return render(
                        request=request,
                        template_name="gate/password_reset_request.html",
                        context={"email_sent": True},
                    )
                else:
                    email_form.add_error(
                        field="email",
                        error="The password reset link we emailed you is still valid.",
                    )
                    return render(
                        request=request,
                        template_name="gate/password_reset_request.html",
                        context={"form": email_form},
                    )
            else:
                email_form.add_error(
                    field="email",
                    error=mark_safe(
                        "We couldn't find an active customer with that email address."  # Activate your account or <a href='{reverse_lazy('gate:signup')}'>sign up?</a>"
                    ),
                )

        return render(
            request=request,
            template_name="gate/password_reset_request.html",
            context={"form": email_form},
        )
