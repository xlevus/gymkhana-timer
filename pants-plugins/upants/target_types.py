from pants.engine.target import Target, COMMON_TARGET_FIELDS, Dependencies
from pants.backend.python.target_types import PythonSourceTarget, PythonSourcesGeneratorTarget


class UPythonDependency(Target):
    alias = "upython_requirement"

    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
    )
    help = "A micropython dependency"


class UPythonSourcePackage(Target):
    alias = "upython_executable"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
    )
    help = "A micropython source package."
