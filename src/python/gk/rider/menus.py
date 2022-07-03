from typing import TYPE_CHECKING
from menu import Menu, MenuItem
from django.urls import reverse

if TYPE_CHECKING:
    from django.http import HttpRequest


def logged_in(request: "HttpRequest"):
    return request.user.is_authenticated

def logged_out(request: "HttpRequest"):
    return not logged_in(request)

profile = MenuItem(
    "My Account",
    reverse("rider-profile"),
    check=logged_in,
    exact_url=True,
    children=[
    ]
)

Menu.add_item("account_nav", profile)
Menu.add_item("account_nav", MenuItem(
    "Log In",
    reverse("account_login"),
    check=logged_out,
    exact_url=True,
))


Menu.add_item("account", profile)
Menu.add_item("account", MenuItem(
    "Log Out",
    reverse("account_logout"),
    check=logged_in,
    exact_url=True,
))