python_requirements(
    name="requirements.txt",
    module_mapping={
        "django-gcloud-connectors": ["gcloudc"],
    },
    overrides={
        "google-cloud-datastore": {
            "dependencies": [":requirements.txt#setuptools"],
        },
    }
)

