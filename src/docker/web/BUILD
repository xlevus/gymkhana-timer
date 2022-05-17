shell_source(name="entrypoint", source="entrypoint.sh")

docker_image(
    source="Dockerfile",
    dependencies=[
        "src/python/gk/web:gunicorn",
        "src/python/gk/web:manage",
        ":entrypoint",
    ]
)
