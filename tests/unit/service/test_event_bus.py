"""TC-EVENT-001/002: Event bus tests."""

from __future__ import annotations

from domain_types.events import BaseEvent, EventType
from service.event_bus import EventBus


class TestEventBus:
    def test_tc_event_001_publish_subscribe_roundtrip(self) -> None:
        """TC-EVENT-001: Event publish/subscribe roundtrip."""
        bus = EventBus()
        received: list[BaseEvent] = []
        bus.subscribe(EventType.THERMAL_ALIVE, received.append)

        evt = BaseEvent(
            event_id="E-001",
            mission_id="M-001",
            robot_id="R-001",
            event_type=EventType.THERMAL_ALIVE,
            timestamp_ms=1000,
            source_module="detector",
        )
        bus.publish(evt)
        assert len(received) == 1
        assert received[0] is evt

    def test_subscribe_all(self) -> None:
        bus = EventBus()
        received: list[BaseEvent] = []
        bus.subscribe_all(received.append)

        bus.publish(BaseEvent("E-1", "M", "R", EventType.THERMAL_ALIVE, 100, "test"))
        bus.publish(BaseEvent("E-2", "M", "R", EventType.GAS_HAZARD, 200, "test"))
        assert len(received) == 2

    def test_no_cross_delivery(self) -> None:
        bus = EventBus()
        thermal: list[BaseEvent] = []
        gas: list[BaseEvent] = []
        bus.subscribe(EventType.THERMAL_ALIVE, thermal.append)
        bus.subscribe(EventType.GAS_HAZARD, gas.append)

        bus.publish(BaseEvent("E-1", "M", "R", EventType.THERMAL_ALIVE, 100, "test"))
        assert len(thermal) == 1
        assert len(gas) == 0

    def test_tc_event_002_ordering_by_timestamp(self) -> None:
        """TC-EVENT-002: Event ordering by timestamp."""
        bus = EventBus()
        bus.publish(BaseEvent("E-1", "M", "R", EventType.THERMAL_ALIVE, 300, "test"))
        bus.publish(BaseEvent("E-2", "M", "R", EventType.GAS_HAZARD, 100, "test"))
        bus.publish(BaseEvent("E-3", "M", "R", EventType.SLAM_FAILURE, 200, "test"))

        history = bus.get_history()
        assert len(history) == 3
        sorted_h = sorted(history, key=lambda e: e.timestamp_ms)
        assert sorted_h[0].event_id == "E-2"
        assert sorted_h[1].event_id == "E-3"
        assert sorted_h[2].event_id == "E-1"

    def test_clear(self) -> None:
        bus = EventBus()
        received: list[BaseEvent] = []
        bus.subscribe(EventType.THERMAL_ALIVE, received.append)
        bus.publish(BaseEvent("E-1", "M", "R", EventType.THERMAL_ALIVE, 100, "test"))
        bus.clear()
        bus.publish(BaseEvent("E-2", "M", "R", EventType.THERMAL_ALIVE, 200, "test"))
        assert len(received) == 1
        assert len(bus.get_history()) == 1

    def test_multiple_handlers_same_type(self) -> None:
        bus = EventBus()
        a: list[str] = []
        b: list[str] = []
        bus.subscribe(EventType.GAS_HAZARD, lambda e: a.append(e.event_id))
        bus.subscribe(EventType.GAS_HAZARD, lambda e: b.append(e.event_id))
        bus.publish(BaseEvent("E-1", "M", "R", EventType.GAS_HAZARD, 100, "test"))
        assert a == ["E-1"]
        assert b == ["E-1"]
