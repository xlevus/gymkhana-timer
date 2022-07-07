import os
from typing import List

from pants.backend.python.target_types import PythonSourceTarget
from pants.core.goals.package import OutputPathField
from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    AsyncFieldMixin,
    BoolField,
    Dependencies,
    Field,
    SecondaryOwnerMixin,
    StringSequenceField,
    Target,
)
from pants.source.filespec import Filespec


class UPythonDependencySpecs(AsyncFieldMixin, StringSequenceField):
    alias = "requirements"
    requred = False
    help = "List of requirements."

    def specs(self) -> List[str]:
        if self.value is None:
            return [self.address.target_name]
        return self.value


class UPythonDependency(Target):
    alias = "upython_requirement"

    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
        UPythonDependencySpecs,
    )
    help = "A micropython dependency"


class UPythonCompatibleField(BoolField):
    alias = "upython_compatible"
    help = "Is the python source upython compatible?"
    required = False
    default = True


class UPythonMainField(AsyncFieldMixin, SecondaryOwnerMixin, Field):
    alias = "upython_main"
    default = "main.py"
    help = "Set which file to rename to 'main.py'."

    @property
    def filespec(self) -> Filespec:
        full_glob = os.path.join(self.address.spec_path, self.value.module)
        return {"includes": [full_glob]}


class UPythonSourcePackage(Target):
    alias = "upython_directory_image"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        UPythonMainField,
        OutputPathField,
        Dependencies,
    )
    help = "A micropython source package."


def target_types():
    return [
        UPythonDependency,
        UPythonSourcePackage,
    ]


def rules():
    return [PythonSourceTarget.register_plugin_field(UPythonCompatibleField)]
