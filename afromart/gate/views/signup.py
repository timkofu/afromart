import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import View

from ..forms import SignUp as SignUpForm


class SignUp(View):
    redirect_path = "/"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to=self.redirect_path)

        return render(
            request=request,
            template_name="gate/signup.html",
            context={"form": SignUpForm()},
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to=self.redirect_path)

        registration_form = SignUpForm(request.POST)
        if not registration_form.is_valid():
            return render(
                request=request,
                template_name="gate/signup.html",
                context={"form": registration_form},
            )

        email = registration_form.cleaned_data["email"]
        username = registration_form.cleaned_data["username"]
        password = registration_form.cleaned_data["password"]

        if User.objects.filter(username=username).exists():
            registration_form.add_error(
                field="username",
                error="This username is already taken. Please choose a different one.",
            )
            return render(
                request=request,
                template_name="gate/signup.html",
                context={"form": registration_form},
            )

        if User.objects.filter(email=email).exists():
            registration_form.add_error(
                field="email",
                error=mark_safe(
                    f"A customer with this email address already exists. Would you like to <a href={reverse_lazy('gate:signin')}>log in</a> instead?"
                ),
            )
            return render(
                request=request,
                template_name="gate/signup.html",
                context={"form": registration_form},
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=username, password=password, email=email, is_active=False
            )

            user_pk_hash = hashlib.sha256(
                data=f"{user.pk}".encode(encoding="utf-8")
            ).hexdigest()

            cache.set(
                key=f"signup_{user_pk_hash}",
                value=user.pk,
                timeout=60 * 60 * 24 * 3,  # 3 days
            )

            message = render_to_string(
                request=request,
                template_name="gate/email/signup_verify.tmpl",
                context={
                    "email": email,
                    "verification_link": request.build_absolute_uri(
                        reverse_lazy(
                            viewname="gate:signup_verify",
                            kwargs={"user_pk_hash": user_pk_hash},
                        ),  # pyright: ignore[reportArgumentType]
                    ),
                },
            )

            settings.THREAD_POOL.submit(
                send_mail,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                subject="Welcome! 🎉",
                message=message,
                fail_silently=False,
            )

        return render(request=request, template_name="gate/signup_verify.html")
