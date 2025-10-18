from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import View

from ..forms.signin import SignIn as SignInForm


class SignIn(View):
    redirect_path = "/"
    signin_template = "gate/signin.html"

    def dispatch(self, request: HttpRequest, *args: ..., **kwargs: ...):
        if request.user.is_authenticated:
            if request.user.is_staff:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
                return redirect(to="/sa/")
            return redirect(to=self.redirect_path)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request=request,
            template_name=self.signin_template,
            context={"form": SignInForm()},
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        def template_renderer(*, form: SignInForm) -> HttpResponse:
            return render(
                request=request,
                context={"form": form},
                template_name=self.signin_template,
            )

        signin_form = SignInForm(request.POST)

        if signin_form.is_valid():
            username = signin_form.cleaned_data["username"]
            password = signin_form.cleaned_data["password"]

            if user := authenticate(
                request=request,
                username=username,
                password=password,
            ):
                if not user.is_active:
                    signin_form.add_error(
                        field="username", error="Please verify your email address."
                    )
                    return template_renderer(form=signin_form)

                login(request=request, user=user)

                return redirect(to=self.redirect_path)

            # else:
            signin_form.add_error(
                field="username",
                error=mark_safe(
                    f"Username and password combination didn't match. <a href={reverse_lazy('gate:password_reset_request')}>Reset password?</a>"
                ),
            )
            return template_renderer(form=signin_form)

        else:
            return template_renderer(form=signin_form)
