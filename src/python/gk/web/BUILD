pex_binary(
    name="bin",
    entry_point="main.py",
    restartable=True,
)

python_sources(
    name="src",
    dependencies=[
        "//src/python/gk/web/templates"
    ]
)

docker_image(
    name="web",
    image_tags=["latest"],
)

python_tests(
    name="tests",
)
