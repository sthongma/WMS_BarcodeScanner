#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console utilities for Windows consoles.

Currently includes a helper to disable QuickEdit Mode which can cause
the application to appear frozen when users click/drag in the console window.
"""

from __future__ import annotations

import os
import ctypes
from ctypes import wintypes


def disable_quick_edit() -> bool:
    """Disable QuickEdit Mode for the current Windows console.

    QuickEdit allows selecting text with the mouse, but it pauses the
    console's input processing, effectively freezing apps attached to
    that console until Enter/Esc is pressed. This function clears the
    QUICK_EDIT flag while keeping other console input flags intact.

    Returns:
        True if the mode was changed successfully (or not applicable),
        False if an attempt was made but failed.
    """
    # Only relevant on Windows consoles
    if os.name != 'nt':
        return True

    try:
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

        # Standard input handle ID for console
        STD_INPUT_HANDLE = -10

        # Input mode flags
        ENABLE_QUICK_EDIT = 0x0040
        ENABLE_EXTENDED_FLAGS = 0x0080

        h_stdin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        if h_stdin in (0, -1):  # INVALID_HANDLE_VALUE
            return False

        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode)) == 0:
            # No console attached or not a console handle
            return False

        current = mode.value
        # To modify QUICK_EDIT, EXTENDED_FLAGS must be set.
        new_mode = (current | ENABLE_EXTENDED_FLAGS) & (~ENABLE_QUICK_EDIT)

        if new_mode == current:
            # Already has QuickEdit disabled (or unchanged)
            return True

        if kernel32.SetConsoleMode(h_stdin, new_mode) == 0:
            return False

        return True
    except Exception:
        # Be conservative: never crash app just for console tuning
        return False
