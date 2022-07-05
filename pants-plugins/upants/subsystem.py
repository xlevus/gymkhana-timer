import os

from pants.engine.rules import SubsystemRule
from pants.option.subsystem import Subsystem
from pants.util.memo import memoized_method
from pants.util.strutil import softwrap
from pants.option.option_types import StrListOption
from pants.util.ordered_set import OrderedSet

from pants.engine.environment import Environment

class UPythonSubsystem(Subsystem):
    options_scope = "micropython"
    help = "Micropython. Python for embedded systems."

    _executable_search_paths = StrListOption(
        "--executable-search-paths",
        default=["<PATH>"],
        help=softwrap(
            """
            The PATH value that will be used to find the Docker client and any tools required.
            The special string `"<PATH>"` will expand to the contents of the PATH env var.
            """
        ),
        advanced=True,
        metavar="<binary-paths>",
    )

    @memoized_method
    def executable_search_path(self, env: Environment) -> tuple[str, ...]:
        def iter_path_entries():
            for entry in self._executable_search_paths:
                if entry == "<PATH>":
                    path = env.get("PATH")
                    if path:
                        yield from path.split(os.pathsep)
                else:
                    yield entry

        return tuple(OrderedSet(iter_path_entries()))


def rules():
    return [SubsystemRule(UPythonSubsystem)]