"""Make this lesson's modules importable from its tests, BUGS/ and challenges/."""

import sys
from pathlib import Path

_HERE = Path(__file__).parent
for folder in (_HERE, _HERE / "BUGS", _HERE / "challenges"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
