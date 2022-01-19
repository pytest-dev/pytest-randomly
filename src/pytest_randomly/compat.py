from __future__ import annotations

import hashlib
import sys
from functools import partial

if sys.version_info >= (3, 9):
    md5 = partial(hashlib.md5, usedforsecurity=False)
else:
    md5 = hashlib.md5
