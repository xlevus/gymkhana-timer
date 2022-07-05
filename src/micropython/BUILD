python_sources(
    name="src"
)

upython_requirement(name="mqtt", requirements=["micropython-mqtt"])

upython_executable(
    name="timer",
    dependencies=[
        ":src",
        ":mqtt",
    ],
)