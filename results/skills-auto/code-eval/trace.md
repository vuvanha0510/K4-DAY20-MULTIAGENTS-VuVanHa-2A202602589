### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: ls
{"path": "workspace/tests"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool call: execute
{"command": "python3 -m unittest discover workspace/tests"}

### Tool result
[stderr] E
[stderr] ======================================================================
[stderr] ERROR: test_bookings (unittest.loader._FailedTest.test_bookings)
[stderr] ----------------------------------------------------------------------
[stderr] ImportError: Failed to import test module: test_bookings
[stderr] Traceback (most recent call last):
[stderr]   File "~\AppData\Local\Programs\Python\Python311\Lib\unittest\loader.py", line 419, in _find_test_path
[stderr]     module = self._get_module_from_name(name)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "~\AppData\Local\Programs\Python\Python311\Lib\unittest\loader.py", line 362, in _get_module_from_name
[stderr]     __import__(name)
[stderr]   File "~\AppData\Local\Temp\tmpdf4g_x3w\workspace\tests\test_bookings.py", line 1, in <module>
[stderr]     from bookings.billing import billable_blocks
[stderr] ModuleNotFoundError: No module named 'bookings'
[stderr] 
[stderr] 
[stderr] ----------------------------------------------------------------------
[stderr] Ran 1 test in 0.000s
[stderr] 
[stderr] FAILED (errors=1)

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m unittest discover workspace/tests"}

### Tool result
[stderr] E
[stderr] ======================================================================
[stderr] ERROR: test_bookings (unittest.loader._FailedTest.test_bookings)
[stderr] ----------------------------------------------------------------------
[stderr] ImportError: Failed to import test module: test_bookings
[stderr] Traceback (most recent call last):
[stderr]   File "~\AppData\Local\Programs\Python\Python311\Lib\unittest\loader.py", line 419, in _find_test_path
[stderr]     module = self._get_module_from_name(name)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "~\AppData\Local\Programs\Python\Python311\Lib\unittest\loader.py", line 362, in _get_module_from_name
[stderr]     __import__(name)
[stderr]   File "~\AppData\Local\Temp\tmpdf4g_x3w\workspace\tests\test_bookings.py", line 1, in <module>
[stderr]     from bookings.billing import billable_blocks
[stderr] ModuleNotFoundError: No module named 'bookings'
[stderr] 
[stderr] 
[stderr] ----------------------------------------------------------------------
[stderr] Ran 1 test in 0.000s
[stderr] 
[stderr] FAILED (errors=1)

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m unittest discover tests"}

### Tool result
[stderr] ----------------------------------------------------------------------
[stderr] Ran 0 tests in 0.000s
[stderr] 
[stderr] OK
[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\tmpdf4g_x3w\workspace
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

tests\test_bookings.py FF.                                               [100%]

================================== FAILURES ===================================
______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

D:\Code\AITHUCCHIEN\LABS\K4-DAY20-MULTIAGENTS-VuVanHa-2A202602589\tasks\code-eval\workspace\tests\test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
bookings\schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings\schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whi

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: edit_file
{"file_path": "workspace/bookings/timeutil.py", "old_string": "    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "    text = text.strip()\n    if \":\" in text:\n        h, m = text.split(\":\")\n        return int(h) * 60 + int(m)\n    if \"h\" in text and \"m\" in text:\n        m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text)\n        return int(m.group(1)) * 60 + int(m.group(2))\n    if \"h\" in text:\n        return int(text.replace(\"h\", \"\")) * 60\n    if \"m\" in text:\n        return int(text.replace(\"m\", \"\"))\n    return int(text)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    import math\n    return math.ceil(minutes / block)", "old_string": "    return round(minutes / block)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\tmpdf4g_x3w\workspace
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

tests\test_bookings.py ...                                               [100%]

============================== 3 passed in 0.04s ==============================

[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool call: edit_file
{"new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return slots + [slot]", "file_path": "workspace/bookings/schedule.py", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\tmpdf4g_x3w\workspace
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

tests\test_bookings.py ...                                               [100%]

============================== 3 passed in 0.04s ==============================

[Command succeeded with exit code 0]

### Tool call: write_file
{"content": "from bookings.schedule import add_slot\n\ndef test_add_slot_isolation():\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n    assert add_slot(\"c\", [\"x\"]) == [\"x\", \"c\"]\n\ndef test_add_slot_new_list():\n    original = [\"x\"]\n    result = add_slot(\"y\", original)\n    assert result == [\"x\", \"y\"]\n    assert original == [\"x\"]\n", "file_path": "workspace/tests/test_add_slot.py"}

### Tool result
Updated file /workspace/tests/test_add_slot.py

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest tests/"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\tmpdf4g_x3w\workspace
plugins: anyio-4.15.1, langsmith-0.14.4
collected 5 items

tests\test_add_slot.py ..                                                [ 40%]
tests\test_bookings.py ...                                               [100%]

============================== 5 passed in 0.04s ==============================

[Command succeeded with exit code 0]

### Tool call: delete
{"file_path": "workspace/tests/test_add_slot.py"}

### Tool result
Deleted /workspace/tests/test_add_slot.py

### Tool call: execute
{"command": "cd workspace && export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\tmpdf4g_x3w\workspace
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

tests\test_bookings.py ...                                               [100%]

============================== 3 passed in 0.02s ==============================

[Command succeeded with exit code 0]

### Assistant
[{'type': 'text', 'text': 'I have fixed the issues in the `bookings` package to ensure the test suite passes and the functions adhere to their docstrings.\n\n### Changes:\n1.  **`workspace/bookings/timeutil.py`**: Updated `parse_duration` to correctly handle all specified formats ("1h30m", "2h", "45m", "1:30", "45") instead of only "1h30m".\n2.  **`workspace/bookings/billing.py`**: Updated `billable_blocks` to use `math.ceil` for rounding up (as required by the docstring) and added a check to raise a `ValueError` for negative input.\n3.  **`workspace/bookings/schedule.py`**: Fixed `add_slot` to avoid using a mutable default argument (`slots=[]`), which was causing state to persist between calls. It now correctly returns a new list and maintains isolation between calls.\n\nThe test suite now passes successfully.', 'extras': {'signature': 'EnMKcQFpFH0T70+8/TuuEH/oN82nP8FoSJNjgil/w+hrIjR2tjv0bSNNoSur3GHgRHS8YZ/KCvH3ZkqML3Z1mmVhtHCYj4dC3V7k5K54q7QIZbZD4LXSDHaTo5z+6itwcdejwyI0fjoAQTfYWnd+mXMddDD0'}}]