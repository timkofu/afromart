from django.urls import path

from .views import (
    PasswordReset,
    PasswordResetRequest,
    SignIn,
    SignUp,
    sign_out,
    signup_verify,
)

app_name = "gate"

urlpatterns = [
    path(route="signin/", view=SignIn.as_view(), name="signin"),
    path(route="signout/", view=sign_out, name="signout"),
    path(
        route="password_reset_request/",
        view=PasswordResetRequest.as_view(),
        name="password_reset_request",
    ),
    path(
        route="password_reset/<str:user_pk_hash>",
        view=PasswordReset.as_view(),
        name="password_reset",
    ),
    path(route="signup/", view=SignUp.as_view(), name="signup"),
    path(
        route="signup_verify/<str:user_pk_hash>",
        view=signup_verify,
        name="signup_verify",
    ),
]
