from typing import TYPE_CHECKING
from menu import Menu, MenuItem
from django.urls import reverse

if TYPE_CHECKING:
    from django.http import HttpRequest


def logged_in(request: "HttpRequest"):
    return request.user.is_authenticated

def has_password(request: "HttpRequest"):
    return request.user.is_authenticated and request.user.has_usable_password()


def not_(func):
    return lambda request: not func(request) 



Menu.add_item("account_nav", MenuItem(
    "My Account",
    reverse("rider-profile"),
    check=logged_in,
    exact_url=False,
    children=[
    ]
))
Menu.add_item("account_nav", MenuItem(
    "Log In",
    reverse("account_login"),
    check=not_(logged_in),
    exact_url=True,
))


Menu.add_item("account", MenuItem(
    "My Account",
    reverse("rider-profile"),
    check=logged_in,
    exact_url=True,
    children=[
    ]
))
Menu.add_item("account", MenuItem(
    "Change Password",
    reverse("account_change_password"),
    check=has_password,
    exact_url=True,
))
Menu.add_item("account", MenuItem(
    "Set Password",
    reverse("account_set_password"),
    check=not_(has_password),
    exact_url=True,
))
Menu.add_item("account", MenuItem(
    "Account Connections",
    reverse("socialaccount_connections"),
    check=logged_in,
    exact_url=True,
))
Menu.add_item("account", MenuItem(
    "Log Out",
    reverse("account_logout"),
    check=logged_in,
    exact_url=True,
))