import hashlib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client
from django.urls import reverse_lazy
from django.utils.functional import Promise


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username="customer", password="secret", email="customer@gmail.com"
    )


@pytest.fixture
def inactive_user() -> User:
    return User.objects.create_user(
        username="customer", password="secret", is_active=False
    )


@pytest.fixture
def password_reset_request_url() -> Promise:
    return reverse_lazy("gate:password_reset_request")


@pytest.fixture
def password_reset_url(user: User) -> Promise:
    user_pk_hash: str = hashlib.sha256(f"{user.pk}".encode("utf-8")).hexdigest()
    cache.set(key=f"passwordreset_{user_pk_hash}", value=user.pk, timeout=300)
    return reverse_lazy("gate:password_reset", kwargs={"user_pk_hash": user_pk_hash})


@pytest.fixture
def signin_url() -> Promise:
    return reverse_lazy("gate:signin")


@pytest.fixture
def signout_url() -> Promise:
    return reverse_lazy("gate:signout")


@pytest.fixture
def signup_url() -> Promise:
    return reverse_lazy("gate:signup")


@pytest.fixture
def signup_verify_url(inactive_user: User) -> Callable[[], Promise]:
    user_pk_hash: str = hashlib.sha256(
        f"{inactive_user.pk}".encode("utf-8")
    ).hexdigest()
    cache.set(key=f"signup_{user_pk_hash}", value=inactive_user.pk)
    return partial(reverse_lazy, "gate:signup_verify", args=(user_pk_hash,))


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_request_loads(
    client: Client, password_reset_request_url: str
) -> None:
    response = client.get(password_reset_request_url)
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
@patch("concurrent.futures.ThreadPoolExecutor")
def test_password_reset_request_sends_email(
    mock_executor: ThreadPoolExecutor,
    client: Client,
    password_reset_request_url: str,
    user: User,
) -> None:
    response = client.post(password_reset_request_url, {"email": "customer@gmail.com"})
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_request_no_email(
    client: Client, password_reset_request_url: str
) -> None:
    response = client.post(password_reset_request_url)
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_request_nonexistent_email(
    client: Client, password_reset_request_url: str
) -> None:
    response = client.post(password_reset_request_url, {"email": "supplier@gmail.com"})
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_request_link_already_sent(
    client: Client, password_reset_request_url: str, user: User
) -> None:
    cache.set(f"password_reset_{user.pk}", "1", timeout=300)
    response = client.post(password_reset_request_url, {"email": "customer@gmail.com"})
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_loads(client: Client, password_reset_url: str) -> None:
    response = client.get(password_reset_url)
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_success_unloggedin(
    client: Client, password_reset_url: str
) -> None:
    response = client.post(
        password_reset_url, {"password1": "secret123#$", "password2": "secret123#$"}
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_invalid_form(client: Client, password_reset_url: str) -> None:
    response = client.post(
        password_reset_url, {"password1": "secret", "password2": "secret"}
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_loggedin(
    client: Client, password_reset_url: str, user: User
) -> None:
    client.login(username="customer", password="secret")
    response = client.post(
        password_reset_url, {"password1": "secret123#$", "password2": "secret123#$"}
    )
    assert response.status_code == 302


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_password_reset_no_token(
    client: Client, password_reset_url: str, user: User
) -> None:
    user_pk_hash: str = hashlib.sha256(f"{user.pk}".encode("utf-8")).hexdigest()
    cache.delete(f"passwordreset_{user_pk_hash}")
    assert client.get(password_reset_url).status_code == 200
    assert client.post(password_reset_url).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_loads(client: Client, signin_url: str) -> None:
    response = client.get(signin_url)
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_success(client: Client, signin_url: str, user: User) -> None:
    response = client.post(signin_url, {"username": "customer", "password": "secret"})
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_unverified(client: Client, signin_url: str, user: User) -> None:
    user.is_active = False
    user.save()
    response = client.post(signin_url, {"username": "customer", "password": "secret"})
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_invalid_credentials(
    client: Client, signin_url: str, user: User
) -> None:
    response = client.post(signin_url, {"username": "customer", "password": "wrong"})
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_invalid_form(client: Client, signin_url: str) -> None:
    response = client.post(signin_url)
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signin_redirect_authenticated(
    client: Client, signin_url: str, user: User
) -> None:
    client.force_login(user)
    assert client.get(signin_url).status_code == 302


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signout(client: Client, signout_url: str, user: User) -> None:
    client.login(username="customer", password="secret")
    assert client.post(signout_url).status_code == 302


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_verify_success(
    client: Client, signup_verify_url: Callable[[], str]
) -> None:
    response = client.get(signup_verify_url())
    assert response.status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_verify_once(
    client: Client, signup_verify_url: Callable[[], str]
) -> None:
    client.get(signup_verify_url())
    assert client.get(signup_verify_url()).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_verify_invalid_hash(client: Client) -> None:
    invalid_url = reverse_lazy("gate:signup_verify", args=("invalid_hash",))
    assert client.get(invalid_url).status_code == 404


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_loads(client: Client, signup_url: str) -> None:
    assert client.get(signup_url).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_invalid_form(client: Client, signup_url: str) -> None:
    assert client.post(signup_url).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_valid_form(client: Client, signup_url: str) -> None:
    data: dict[str, str] = {
        "email": "new@gmail.com",
        "username": "new",
        "password": "secret123",
    }
    assert client.post(signup_url, data).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_redirect_loggedin(client: Client, signup_url: str, user: User) -> None:
    client.login(username="customer", password="secret")
    assert client.get(signup_url).status_code == 302
    assert client.post(signup_url).status_code == 302


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_username_in_use(client: Client, signup_url: str, user: User) -> None:
    data: dict[str, str] = {
        "email": "new@gmail.com",
        "username": "customer",
        "password": "secret123",
    }
    assert client.post(signup_url, data).status_code == 200


@pytest.mark.skip(reason="Stable")
@pytest.mark.django_db
def test_signup_email_in_use(client: Client, signup_url: str, user: User) -> None:
    data: dict[str, str] = {
        "email": "customer@gmail.com",
        "username": "new",
        "password": "secret123",
    }
    assert client.post(signup_url, data).status_code == 200
