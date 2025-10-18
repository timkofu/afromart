from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def signup_verify(request: HttpRequest, user_pk_hash: str) -> HttpResponse:
    if user := User.objects.filter(pk=cache.get(key=f"signup_{user_pk_hash}")).first():
        if user.is_active:
            return HttpResponse(status=200, content="Customer already verified.")

        with transaction.atomic():
            user.is_active = True
            user.save()

        return render(
            request=request,
            template_name="gate/signup_verified.html",
        )

    return HttpResponse(status=404, content="Not Found.")
