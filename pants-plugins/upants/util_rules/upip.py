import itertools
from dataclasses import dataclass
from typing import Iterable, Tuple

from pants.engine.fs import Digest, DigestSubset, MergeDigests, PathGlobs, RemovePrefix
from pants.engine.process import Process, ProcessCacheScope, ProcessResult
from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import Targets
from pants.util.meta import frozen_after_init
from upants.target_types import UPythonDependency, UPythonDependencySpecs
from upants.util_rules.micropython_binary import UPythonBinary

INSTALL_DIR = "packages"


@frozen_after_init
@dataclass(unsafe_hash=True)
class UPipPackagesRequest:
    targets: Tuple[UPythonDependency, ...]

    def __init__(
        self,
        targets: Iterable[UPythonDependency],
    ) -> None:
        self.targets = tuple(targets)


@dataclass
class UPipPackagesResponse:
    digest: Digest


@frozen_after_init
@dataclass(unsafe_hash=True)
class UPipSourceRequest:
    requirements: Tuple[str]

    def __init__(self, requirements: Iterable[str]):
        self.requirements = tuple(requirements)


@rule
async def get_upip_source(request: UPipSourceRequest, upython: UPythonBinary) -> Digest:
    requirements = list(request.requirements)
    result = await Get(
        ProcessResult,
        Process(
            argv=[upython.path, "-m", "upip", "install", "-p", INSTALL_DIR]
            + requirements,
            description="Downloading upip packages: " + ", ".join(requirements),
            output_directories=[INSTALL_DIR],
        ),
    )
    return result.output_digest


@rule
async def upip_packages_request(request: UPipPackagesRequest) -> UPipPackagesResponse:
    digests = await MultiGet(
        Get(
            Digest,
            UPipSourceRequest,
            UPipSourceRequest(requirements=target[UPythonDependencySpecs].specs()),
        )
        for target in request.targets
    )

    joined = await Get(Digest, MergeDigests(digests))

    minus_header = await Get(
        Digest, DigestSubset(joined, PathGlobs(["**/*", "!**/@PaxHeader"]))
    )

    stripped = await Get(Digest, RemovePrefix(minus_header, INSTALL_DIR))

    return UPipPackagesResponse(stripped)


def rules():
    return [*collect_rules()]
