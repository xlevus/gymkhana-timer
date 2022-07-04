from pants.engine.target import Target, COMMON_TARGET_FIELDS, Dependencies


class UPythonDependency(Target):
    alias = "upython_requirement"

    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
    )
    help = "A micropython dependency"