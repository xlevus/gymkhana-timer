from pants.core.goals.package import BuiltPackage, PackageFieldSet, OutputPathField, BuiltPackageArtifact
from pants.engine.unions import UnionRule
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.fs import AddPrefix, Digest
from pants.engine.target import TransitiveTargets, TransitiveTargetsRequest, SourcesField
from pants.core.util_rules.stripped_source_files import StrippedSourceFiles
from pants.core.util_rules.source_files import SourceFilesRequest
from pants.engine.addresses import Address

from dataclasses import dataclass

from upants.target_types import UPythonMainField


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

    all_sources = await Get(
        StrippedSourceFiles,
        SourceFilesRequest((
            tgt.get(SourcesField) for tgt in transitive_targets.closure
        ))
    )

    output_prefix = field_set.output_path.value_or_default(file_ending=None)

    prefixed = await Get(Digest, AddPrefix(all_sources.snapshot.digest, output_prefix))

    return BuiltPackage(prefixed, [ 
        BuiltPackageArtifact(output_prefix),
     ])

    import pdb; pdb.set_trace()


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, UPythonFieldSet),
    ]