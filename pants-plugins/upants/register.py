from upants import subsystem

from upants.target_types import UPythonSourcePackage, UPythonDependency
from upants.goals import package_directory_image


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