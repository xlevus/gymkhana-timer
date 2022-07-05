python_sources(
    name="src"
)

upython_requirement(name="mqtt", requirements=["micropython-mqtt"])

upython_directory_image(
    name="timer",
    dependencies=[
        ":src",
        ":mqtt",
    ],
)