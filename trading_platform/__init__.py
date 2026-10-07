"""
BullMonk Trading Platform package root.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure trading_platform root directory is in sys.path
_platform_root = str(Path(__file__).resolve().parent)
if _platform_root not in sys.path:
    sys.path.insert(0, _platform_root)
