from pants.core.goals.package import BuiltPackage, PackageFieldSet, OutputPathField, BuiltPackageArtifact
from pants.engine.unions import UnionRule
from pants.engine.rules import Get, collect_rules, rule, MultiGet
from pants.engine.fs import AddPrefix, Digest, MergeDigests
from pants.engine.target import TransitiveTargets, TransitiveTargetsRequest, SourcesField
from pants.core.util_rules.stripped_source_files import StrippedSourceFiles
from pants.core.util_rules.source_files import SourceFilesRequest
from pants.engine.addresses import Address

from dataclasses import dataclass

from upants.target_types import UPythonCompatibleField, UPythonDependencySpecs, UPythonMainField
from upants.util_rules.upip import UPipPackagesRequest, UPipPackagesResponse


@dataclass(frozen=True)
class UPythonFieldSet(PackageFieldSet):
    required_fields = (UPythonMainField, OutputPathField)

    output_path: OutputPathField


@rule
async def package_upython_dir_image(field_set: UPythonFieldSet) -> BuiltPackage:
    transitive_targets = await Get(
        TransitiveTargets,
        TransitiveTargetsRequest([field_set.address]),
    )

    deps, all_sources = await MultiGet(
        Get(UPipPackagesResponse, UPipPackagesRequest(
            tgt for tgt in transitive_targets.closure if tgt.has_field(UPythonDependencySpecs)
        )),
    Get(
        StrippedSourceFiles,
        SourceFilesRequest((
            tgt.get(SourcesField) for tgt in transitive_targets.closure
        ))
    ))

    digest = await Get(Digest, MergeDigests([deps.digest, all_sources.snapshot.digest]))

    output_prefix = field_set.output_path.value_or_default(file_ending=None)

    prefixed = await Get(Digest, AddPrefix(digest, output_prefix))


    return BuiltPackage(prefixed, [ 
        BuiltPackageArtifact(output_prefix),
     ])


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, UPythonFieldSet),
    ]