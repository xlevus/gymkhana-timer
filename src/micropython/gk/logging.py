
_ENABLED = False

DEBUG = "DBG"
INFO = "INF"
WARN = "WRN"
ERROR = "ERR"


def enable():
    global _ENABLED
    _ENABLED = True


def log(level: str, message: str) -> None:
    if _ENABLED:
        print(level, ":", message)