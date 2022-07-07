from dataclasses import dataclass

from pants.core.util_rules.system_binaries import (
    BinaryPath,
    BinaryPathRequest,
    BinaryPaths,
    BinaryPathTest,
)
from pants.engine.environment import Environment, EnvironmentRequest
from pants.engine.rules import Get, collect_rules, rule
from upants.subsystem import UPythonSubsystem


@dataclass
class UPythonBinary(BinaryPath):
    pass


@dataclass(frozen=True)
class UPythonBinaryRequest:
    pass


@rule(desc="Finding `micropython` binary.")
async def find_upython(
    request: UPythonBinaryRequest, upython: UPythonSubsystem
) -> UPythonBinary:
    env = await Get(Environment, EnvironmentRequest(["PATH"]))
    search_path = upython.executable_search_path(env)

    request = BinaryPathRequest(
        binary_name="micropython",
        search_path=search_path,
        test=BinaryPathTest(args=["-v"]),
    )
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(
        request, rationale="interact with micropython"
    )

    return UPythonBinary(first_path.path, first_path.fingerprint)


@rule
async def get_upython() -> UPythonBinary:
    return await Get(UPythonBinary, UPythonBinaryRequest())


def rules():
    return collect_rules()
