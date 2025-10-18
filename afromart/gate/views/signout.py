from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST


@login_required
@require_POST
def sign_out(request: HttpRequest) -> HttpResponse:
    logout(request=request)
    return HttpResponseRedirect(redirect_to=reverse_lazy(viewname="gate:signin"))
