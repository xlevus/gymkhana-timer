from django.urls import reverse
from menu import Menu, MenuItem

Menu.add_item(
    "main",
    MenuItem(
        "Courses",
        reverse("index"),
        exact_url=True,
    ),
)
