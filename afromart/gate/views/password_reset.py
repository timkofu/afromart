from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View

from ..forms import PasswordResetActionForm


class PasswordReset(View):
    def dispatch(
        self, request: HttpRequest, user_pk_hash: str, *args: ..., **kwargs: ...
    ):
        if request.user.is_anonymous:
            if not cache.get(key=f"passwordreset_{user_pk_hash}"):
                return render(
                    request=request,
                    template_name="gate/password_reset.html",
                    context={"password_reset_expired": True},
                )

        return super().dispatch(request, user_pk_hash, *args, **kwargs)

    def get(self, request: HttpRequest, user_pk_hash: str) -> HttpResponse:
        password_reset_form = PasswordResetActionForm()
        return render(
            request=request,
            template_name="gate/password_reset.html",
            context={
                "form": password_reset_form,
                "user_pk_hash": user_pk_hash,
                "password_reset_live": True,
            },
        )

    def post(self, request: HttpRequest, user_pk_hash: str) -> HttpResponse:
        password_reset_form = PasswordResetActionForm(data=request.POST)

        if password_reset_form.is_valid():
            password = password_reset_form.cleaned_data["password2"]
            authenticated = request.user.is_authenticated
            cache_key = f"passwordreset_{user_pk_hash}"

            user = (
                request.user
                if authenticated
                else User.objects.get(pk=int(cache.get(key=cache_key)))
            )

            with transaction.atomic():
                user.set_password(raw_password=password)
                user.save()

                if authenticated:
                    logout(request=request)
                    return redirect(to=reverse_lazy("gate:signin"))  # pyright: ignore[reportArgumentType]

                cache.delete(key=cache_key)

            return render(
                request=request,
                template_name="gate/password_reset.html",
                context={"password_reset_successful": True},
            )

        return render(
            request=request,
            template_name="gate/password_reset.html",
            context={
                "form": password_reset_form,
                "user_pk_hash": user_pk_hash,
                "password_reset_live": True,
            },
        )
