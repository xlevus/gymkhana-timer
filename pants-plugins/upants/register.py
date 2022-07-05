from upants import subsystem

from upants.target_types import UPythonSourcePackage, UPythonDependency


def rules():
    return (
        *subsystem.rules(),
    )


def target_types():
    return (
        UPythonDependency,
        UPythonSourcePackage,
    )