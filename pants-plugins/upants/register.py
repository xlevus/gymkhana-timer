from upants import subsystem
from upants.goals import package_directory_image
from upants.target_types import UPythonDependency, UPythonSourcePackage


def rules():
    return (
        *subsystem.rules(),
        *package_directory_image.rules(),
    )


def target_types():
    return (
        UPythonDependency,
        UPythonSourcePackage,
    )
