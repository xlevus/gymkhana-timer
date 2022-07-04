from pants.engine.rules import SubsystemRule
from pants.option.subsystem import Subsystem


class UPythonSubsystem(Subsystem):
    options_scope = "micropython"
    help = "Micropython. Python for embedded systems."


def rules():
    return [SubsystemRule(UPythonSubsystem)]