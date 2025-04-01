python_requirements(
    name="requirements.txt",
    module_mapping={
        "django-environ": ["environ"],
        "django-allauth": ["allauth"],
        "django-simple-menu": ["simple_menu"],
    },
    overrides={
        "django-allauth": {
            "dependencies": [":requirements.txt#requests", ":requirements.txt#jwt"],
        }
    },
)
