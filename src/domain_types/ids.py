"""Domain identity types — NewType wrappers for type-safe IDs.

All IDs are externally injected; this module never generates them.
"""

from __future__ import annotations

from typing import NewType

MissionId = NewType("MissionId", str)
RobotId = NewType("RobotId", str)
EventId = NewType("EventId", str)
OperatorId = NewType("OperatorId", str)
RequestId = NewType("RequestId", str)
