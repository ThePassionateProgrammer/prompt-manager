"""
Tests for Component Event System

Tests the event-driven architecture for component interactions.
"""

import pytest
from src.prompt_manager.business.component_event_system import (
    EventType, ComponentEvent, EventBus, CascadingEventHandler, ComponentEventLogger
)


class TestEventType:
    """Test the EventType enum."""
    
    def test_event_types_are_defined(self):
        """Test that all expected event types are defined."""
        # Given: EventType enum
        
        # Then: Should have all expected event types
        assert EventType.COMPONENT_CHANGED.value == "component_changed"
        assert EventType.COMPONENT_ENABLED.value == "component_enabled"
        assert EventType.COMPONENT_DISABLED.value == "component_disabled"
        assert EventType.CASCADE_UPDATE.value == "cascade_update"
        assert EventType.TEMPLATE_PARSED.value == "template_parsed"
        assert EventType.FINAL_PROMPT_GENERATED.value == "final_prompt_generated"


class TestComponentEvent:
    """Test the ComponentEvent class."""
    
    def test_can_create_component_event(self):
        """Test creating a component event."""
        # Given: Event parameters
        event_type = EventType.COMPONENT_CHANGED
        component_id = "role_combo_box"
        data = {"value": "Manager"}
        
        # When: Creating a component event
        event = ComponentEvent(event_type, component_id, data)
        
        # Then: Should have correct values
        assert event.event_type == event_type
        assert event.source_component_id == component_id
        assert event.data == data
        assert event.timestamp is None
    
    def test_can_create_event_without_data(self):
        """Test creating a component event without data."""
        # Given: Event parameters without data
        event_type = EventType.COMPONENT_ENABLED
        component_id = "role_combo_box"
        
        # When: Creating a component event
        event = ComponentEvent(event_type, component_id)
        
        # Then: Should have empty data dict
        assert event.event_type == event_type
        assert event.source_component_id == component_id
        assert event.data == {}
    
    def test_event_string_representation(self):
        """Test the string representation of an event."""
        # Given: A component event
        event = ComponentEvent(EventType.COMPONENT_CHANGED, "test_component")
        
        # When: Converting to string
        event_str = str(event)
        
        # Then: Should have expected format
        assert "ComponentEvent" in event_str
        assert "component_changed" in event_str
        assert "test_component" in event_str


class TestEventBus:
    """Test the EventBus class."""
    
    def test_can_create_event_bus(self):
        """Test creating an event bus."""
        # Given: An event bus
        event_bus = EventBus()
        
        # Then: Should have listeners for all event types
        for event_type in EventType:
            assert event_bus.get_listener_count(event_type) == 0
    
    def test_can_subscribe_to_events(self):
        """Test subscribing to events."""
        # Given: An event bus and a listener
        event_bus = EventBus()
        received_events = []
        
        def listener(event):
            received_events.append(event)
        
        # When: Subscribing to an event type
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener)
        
        # Then: Should have one listener
        assert event_bus.get_listener_count(EventType.COMPONENT_CHANGED) == 1
    
    def test_can_publish_events(self):
        """Test publishing events to subscribers."""
        # Given: An event bus with a subscriber
        event_bus = EventBus()
        received_events = []
        
        def listener(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener)
        
        # When: Publishing an event
        event = ComponentEvent(EventType.COMPONENT_CHANGED, "test_component")
        event_bus.publish(event)
        
        # Then: Listener should receive the event
        assert len(received_events) == 1
        assert received_events[0] == event
    
    def test_multiple_listeners_receive_events(self):
        """Test that multiple listeners receive the same event."""
        # Given: An event bus with multiple subscribers
        event_bus = EventBus()
        listener1_events = []
        listener2_events = []
        
        def listener1(event):
            listener1_events.append(event)
        
        def listener2(event):
            listener2_events.append(event)
        
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener1)
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener2)
        
        # When: Publishing an event
        event = ComponentEvent(EventType.COMPONENT_CHANGED, "test_component")
        event_bus.publish(event)
        
        # Then: Both listeners should receive the event
        assert len(listener1_events) == 1
        assert len(listener2_events) == 1
        assert listener1_events[0] == event
        assert listener2_events[0] == event
    
    def test_can_unsubscribe_from_events(self):
        """Test unsubscribing from events."""
        # Given: An event bus with a subscriber
        event_bus = EventBus()
        received_events = []
        
        def listener(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener)
        
        # When: Unsubscribing and publishing an event
        event_bus.unsubscribe(EventType.COMPONENT_CHANGED, listener)
        event = ComponentEvent(EventType.COMPONENT_CHANGED, "test_component")
        event_bus.publish(event)
        
        # Then: Listener should not receive the event
        assert len(received_events) == 0
        assert event_bus.get_listener_count(EventType.COMPONENT_CHANGED) == 0
    
    def test_listeners_only_receive_subscribed_event_types(self):
        """Test that listeners only receive events they're subscribed to."""
        # Given: An event bus with a subscriber to one event type
        event_bus = EventBus()
        received_events = []
        
        def listener(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.COMPONENT_CHANGED, listener)
        
        # When: Publishing a different event type
        event = ComponentEvent(EventType.COMPONENT_ENABLED, "test_component")
        event_bus.publish(event)
        
        # Then: Listener should not receive the event
        assert len(received_events) == 0


class TestCascadingEventHandler:
    """Test the CascadingEventHandler class."""
    
    def test_can_create_cascading_event_handler(self):
        """Test creating a cascading event handler."""
        # Given: An event bus
        event_bus = EventBus()
        
        # When: Creating a cascading event handler
        handler = CascadingEventHandler(event_bus)
        
        # Then: Should be created successfully
        assert handler.event_bus == event_bus
        assert handler.component_states == {}
    
    def test_can_handle_component_changed_event(self):
        """Test handling a component changed event."""
        # Given: A cascading event handler and event bus
        event_bus = EventBus()
        handler = CascadingEventHandler(event_bus)
        received_cascade_events = []
        
        def cascade_listener(event):
            received_cascade_events.append(event)
        
        event_bus.subscribe(EventType.CASCADE_UPDATE, cascade_listener)
        
        # When: Handling a component changed event
        component_event = ComponentEvent(
            EventType.COMPONENT_CHANGED,
            "role_combo_box",
            {"value": "Manager"}
        )
        handler.handle_component_changed(component_event)
        
        # Then: Should update component state and trigger cascade
        assert handler.get_component_state("role_combo_box")["value"] == "Manager"
        assert len(received_cascade_events) == 1
        assert received_cascade_events[0].event_type == EventType.CASCADE_UPDATE
        assert received_cascade_events[0].data["changed_component"] == "role_combo_box"
        assert received_cascade_events[0].data["new_value"] == "Manager"
    
    def test_can_get_and_set_component_state(self):
        """Test getting and setting component state."""
        # Given: A cascading event handler
        event_bus = EventBus()
        handler = CascadingEventHandler(event_bus)
        
        # When: Setting component state
        state = {"value": "Manager", "enabled": True}
        handler.set_component_state("role_combo_box", state)
        
        # Then: Should be able to get the state
        retrieved_state = handler.get_component_state("role_combo_box")
        assert retrieved_state == state
    
    def test_get_component_state_returns_empty_dict_for_unknown_component(self):
        """Test getting state for unknown component returns empty dict."""
        # Given: A cascading event handler
        event_bus = EventBus()
        handler = CascadingEventHandler(event_bus)
        
        # When: Getting state for unknown component
        state = handler.get_component_state("unknown_component")
        
        # Then: Should return empty dict
        assert state == {}


class TestComponentEventLogger:
    """Test the ComponentEventLogger class."""
    
    def test_can_create_event_logger(self):
        """Test creating an event logger."""
        # Given: An event logger
        logger = ComponentEventLogger()
        
        # Then: Should be created with empty events list
        assert logger.events == []
        assert logger.max_events == 100
    
    def test_can_log_events(self):
        """Test logging events."""
        # Given: An event logger and events
        logger = ComponentEventLogger()
        event1 = ComponentEvent(EventType.COMPONENT_CHANGED, "component1")
        event2 = ComponentEvent(EventType.COMPONENT_ENABLED, "component2")
        
        # When: Logging events
        logger.log_event(event1)
        logger.log_event(event2)
        
        # Then: Should have logged events
        assert len(logger.events) == 2
        assert logger.events[0] == event1
        assert logger.events[1] == event2
    
    def test_can_get_recent_events(self):
        """Test getting recent events."""
        # Given: An event logger with events
        logger = ComponentEventLogger()
        events = [
            ComponentEvent(EventType.COMPONENT_CHANGED, f"component{i}")
            for i in range(5)
        ]
        
        for event in events:
            logger.log_event(event)
        
        # When: Getting recent events
        recent_events = logger.get_recent_events(3)
        
        # Then: Should return the 3 most recent events
        assert len(recent_events) == 3
        assert recent_events[0] == events[2]  # component2
        assert recent_events[1] == events[3]  # component3
        assert recent_events[2] == events[4]  # component4
    
    def test_can_get_events_by_type(self):
        """Test getting events by type."""
        # Given: An event logger with mixed event types
        logger = ComponentEventLogger()
        changed_events = [
            ComponentEvent(EventType.COMPONENT_CHANGED, f"component{i}")
            for i in range(3)
        ]
        enabled_events = [
            ComponentEvent(EventType.COMPONENT_ENABLED, f"component{i}")
            for i in range(2)
        ]
        
        for event in changed_events + enabled_events:
            logger.log_event(event)
        
        # When: Getting events by type
        retrieved_changed = logger.get_events_by_type(EventType.COMPONENT_CHANGED)
        retrieved_enabled = logger.get_events_by_type(EventType.COMPONENT_ENABLED)
        
        # Then: Should return correct events
        assert len(retrieved_changed) == 3
        assert len(retrieved_enabled) == 2
        assert all(event.event_type == EventType.COMPONENT_CHANGED for event in retrieved_changed)
        assert all(event.event_type == EventType.COMPONENT_ENABLED for event in retrieved_enabled)
    
    def test_can_clear_events(self):
        """Test clearing all events."""
        # Given: An event logger with events
        logger = ComponentEventLogger()
        events = [
            ComponentEvent(EventType.COMPONENT_CHANGED, f"component{i}")
            for i in range(3)
        ]
        
        for event in events:
            logger.log_event(event)
        
        assert len(logger.events) == 3
        
        # When: Clearing events
        logger.clear_events()
        
        # Then: Should have no events
        assert len(logger.events) == 0
