import os
from pants.engine.target import Target, COMMON_TARGET_FIELDS, Dependencies, AsyncFieldMixin, SecondaryOwnerMixin, Field
from pants.source.filespec import Filespec
from pants.core.goals.package import OutputPathField


class UPythonDependency(Target):
    alias = "upython_requirement"

    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
    )
    help = "A micropython dependency"



class UPythonMainField(AsyncFieldMixin, SecondaryOwnerMixin, Field):
    alias = "upython_main"
    default = "main.py"
    help = (
        "Set which file to rename to 'main.py'."
    )

    @property
    def filespec(self) -> Filespec:
        full_glob = os.path.join(self.address.spec_path, self.value.module)
        return {"includes": [full_glob]}


class UPythonSourcePackage(Target):
    alias = "upython_directory_image"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        OutputPathField,
        UPythonMainField,
        Dependencies,
    )
    help = "A micropython source package."
