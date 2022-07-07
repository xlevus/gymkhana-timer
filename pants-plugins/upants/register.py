from upants import subsystem
from upants import target_types as targets
from upants.goals import package_directory_image
from upants.util_rules import micropython_binary, upip


def rules():
    return (
        *targets.rules(),
        *subsystem.rules(),
        *upip.rules(),
        *micropython_binary.rules(),
        *package_directory_image.rules(),
    )


def target_types():
    return (*targets.target_types(),)
