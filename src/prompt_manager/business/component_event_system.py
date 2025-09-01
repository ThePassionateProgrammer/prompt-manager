"""
Component Event System

Event system for handling component interactions and cascading updates.
This decouples components from each other and makes the system more extensible.
"""

from typing import Dict, Any, List, Callable, Optional
from enum import Enum


class EventType(Enum):
    """Types of events that can occur in the component system."""
    COMPONENT_CHANGED = "component_changed"
    COMPONENT_ENABLED = "component_enabled"
    COMPONENT_DISABLED = "component_disabled"
    CASCADE_UPDATE = "cascade_update"
    TEMPLATE_PARSED = "template_parsed"
    FINAL_PROMPT_GENERATED = "final_prompt_generated"


class ComponentEvent:
    """Represents an event in the component system."""
    
    def __init__(self, event_type: EventType, source_component_id: str, 
                 data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.source_component_id = source_component_id
        self.data = data or {}
        self.timestamp = None  # Could be set by event bus
    
    def __str__(self):
        return f"ComponentEvent({self.event_type.value}, {self.source_component_id})"


class EventBus:
    """Event bus for handling component events."""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
    
    def subscribe(self, event_type: EventType, listener: Callable[[ComponentEvent], None]):
        """Subscribe to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type: EventType, listener: Callable[[ComponentEvent], None]):
        """Unsubscribe from an event type."""
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
    
    def publish(self, event: ComponentEvent):
        """Publish an event to all subscribers."""
        if event.event_type in self._listeners:
            for listener in self._listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    # Log error but don't stop other listeners
                    print(f"Error in event listener: {e}")
    
    def get_listener_count(self, event_type: EventType) -> int:
        """Get the number of listeners for an event type."""
        return len(self._listeners.get(event_type, []))


class CascadingEventHandler:
    """Handles cascading events between components."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.component_states: Dict[str, Dict[str, Any]] = {}
    
    def handle_component_changed(self, event: ComponentEvent):
        """Handle component change events and trigger cascading updates."""
        component_id = event.source_component_id
        new_value = event.data.get("value", "")
        
        # Update component state
        if component_id not in self.component_states:
            self.component_states[component_id] = {}
        
        self.component_states[component_id]["value"] = new_value
        
        # Trigger cascade update
        cascade_event = ComponentEvent(
            EventType.CASCADE_UPDATE,
            component_id,
            {
                "changed_component": component_id,
                "new_value": new_value,
                "affected_components": self._get_downstream_components(component_id)
            }
        )
        
        self.event_bus.publish(cascade_event)
    
    def _get_downstream_components(self, component_id: str) -> List[str]:
        """Get list of components that should be updated when this component changes."""
        # This is a simplified implementation
        # In a real system, this would use the component hierarchy
        return [f"{component_id}_downstream"]
    
    def get_component_state(self, component_id: str) -> Dict[str, Any]:
        """Get the current state of a component."""
        return self.component_states.get(component_id, {})
    
    def set_component_state(self, component_id: str, state: Dict[str, Any]):
        """Set the state of a component."""
        self.component_states[component_id] = state


class ComponentEventLogger:
    """Logs component events for debugging and monitoring."""
    
    def __init__(self):
        self.events: List[ComponentEvent] = []
        self.max_events = 100  # Keep last 100 events
    
    def log_event(self, event: ComponentEvent):
        """Log an event."""
        self.events.append(event)
        
        # Keep only the last max_events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_recent_events(self, count: int = 10) -> List[ComponentEvent]:
        """Get the most recent events."""
        return self.events[-count:] if self.events else []
    
    def get_events_by_type(self, event_type: EventType) -> List[ComponentEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]
    
    def clear_events(self):
        """Clear all logged events."""
        self.events.clear()
