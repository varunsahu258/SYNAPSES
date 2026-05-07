"""Test-discovery shim for importing the local SYNAPSES package.

``python -m unittest discover -s tests`` places the tests directory at the
front of ``sys.path``. On machines that also have an unrelated ``synapses``
namespace package installed, imports can resolve to that external package
instead of this repository's package. This shim makes the local package win when
unittest discovers modules from inside ``tests``.
"""

from pathlib import Path

_REAL_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "synapses"
_REAL_INIT = _REAL_PACKAGE_DIR / "__init__.py"

__file__ = str(_REAL_INIT)
__path__ = [str(_REAL_PACKAGE_DIR)]

exec(compile(_REAL_INIT.read_text(), str(_REAL_INIT), "exec"), globals())
