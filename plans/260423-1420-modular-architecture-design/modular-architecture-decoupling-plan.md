# Focus Garden - Modular Architecture & Decoupling Plan

**Date**: 2026-04-23
**Status**: Planning Phase
**Goal**: Completely independent modules for parallel development

---

## Executive Summary

Current architecture has tight coupling between UI, Core, and Database layers. This plan defines a modular architecture with:
- **Domain-driven modules** with Single Responsibility Principle
- **Interface-based communication** using Dependency Injection
- **Event-driven integration** via Observer Pattern
- **Mock implementations** for parallel testing
- **Clear module boundaries** with zero cross-implementation dependencies

---

## 1. Module Boundaries (Domain-Driven Design)

### Module 1: `core-domain` (Business Logic)
**Responsibility**: Core business rules and domain models
- **Dependencies**: None (pure Python)
- **Contains**:
  - Domain entities (Session, Distraction, StudyZone)
  - Business rules (validation, state machine)
  - Value objects (TimeRange, KeywordSet)
  - Domain events (SessionStarted, DistractionDetected)

### Module 2: `tracking-engine` (Window Monitoring)
**Responsibility**: System window monitoring and detection
- **Dependencies**: `core-domain` (interfaces only)
- **Contains**:
  - Window monitor implementation
  - Focus state machine
  - Browser title parsing
  - Keyword matching logic

### Module 3: `data-persistence` (Database Layer)
**Responsibility**: Data storage and retrieval
- **Dependencies**: `core-domain` (interfaces only)
- **Contains**:
  - SQLAlchemy models
  - Repository implementations
  - Database migrations
  - Connection management

### Module 4: `application-services` (Use Cases)
**Responsibility**: Orchestrate business workflows
- **Dependencies**: All other modules (via interfaces)
- **Contains**:
  - Session management service
  - Distraction tracking service
  - Statistics calculation service
  - Event handlers

### Module 5: `ui-presentation` (User Interface)
**Responsibility**: User interaction and display
- **Dependencies**: `application-services` (interfaces only)
- **Contains**:
  - PyQt6 widgets
  - View models
  - Event bindings
  - Navigation logic

### Module 6: `cross-cutting-concerns`
**Responsibility**: Shared utilities and infrastructure
- **Dependencies**: None
- **Contains**:
  - Logging configuration
  - Error handling
  - Configuration management
  - Testing utilities

---

## 2. Contract/Interface Design

### File: `shared/interfaces.py`

```python
"""
Shared interfaces for all module communication.
All modules depend on these abstractions, not concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# DOMAIN ENTITIES (Shared across all modules)
# ============================================================================

class SessionState(Enum):
    """Session lifecycle states"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class FocusState(Enum):
    """Focus tracking states"""
    FOCUSING = "focusing"
    DISTRACTED = "distraction_detected"


@dataclass(frozen=True)
class DistractionEvent:
    """Domain event for distraction detection"""
    session_id: int
    app_name: str
    duration_seconds: int
    detected_at: int  # Unix timestamp


@dataclass(frozen=True)
class WindowInfo:
    """Window information from OS"""
    title: str
    app_name: str
    is_browser: bool


@dataclass(frozen=True)
class SessionConfig:
    """Configuration for a new session"""
    subject: str
    target_duration_minutes: int
    allowed_keywords: List[str]


@dataclass(frozen=True)
class SessionSummary:
    """Summary of completed session"""
    session_id: int
    subject: str
    target_minutes: int
    actual_seconds: int
    distraction_count: int
    total_distraction_seconds: int
    state: SessionState


# ============================================================================
# REPOSITORY INTERFACES (Data Persistence Contract)
# ============================================================================

class ISessionRepository(ABC):
    """Session data access contract"""

    @abstractmethod
    def create(self, config: SessionConfig) -> int:
        """Create new session, return session_id"""
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[SessionSummary]:
        """Get session by ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[SessionSummary]:
        """Get all sessions"""
        pass

    @abstractmethod
    def update_state(self, session_id: int, state: SessionState) -> None:
        """Update session state"""
        pass

    @abstractmethod
    def update_duration(self, session_id: int, actual_seconds: int) -> None:
        """Update actual duration"""
        pass


class IDistractionRepository(ABC):
    """Distraction data access contract"""

    @abstractmethod
    def save(self, event: DistractionEvent) -> None:
        """Save distraction event"""
        pass

    @abstractmethod
    def get_by_session(self, session_id: int) -> List[DistractionEvent]:
        """Get all distractions for session"""
        pass

    @abstractmethod
    def get_stats(self, session_id: int) -> dict:
        """Get distraction statistics"""
        pass


# ============================================================================
# TRACKING ENGINE INTERFACES (Window Monitoring Contract)
# ============================================================================

class IWindowMonitor(ABC):
    """OS window monitoring contract"""

    @abstractmethod
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get currently active window"""
        pass


class IKeywordMatcher(ABC):
    """Keyword matching contract"""

    @abstractmethod
    def is_match(self, title: str, keywords: List[str]) -> bool:
        """Check if title matches keywords"""
        pass


class IBrowserParser(ABC):
    """Browser title parsing contract"""

    @abstractmethod
    def parse(self, title: str) -> Optional[str]:
        """Extract site name from browser title"""
        pass

    @abstractmethod
    def is_browser(self, title: str) -> bool:
        """Check if title is from browser"""
        pass


class IFocusTracker(ABC):
    """Focus tracking state machine contract"""

    # Events to subscribe
    ON_FOCUS_STATE_CHANGED = "focus_state_changed"
    ON_DISTRACTION_DETECTED = "distraction_detected"

    @abstractmethod
    def start_tracking(self, keywords: List[str]) -> None:
        """Start focus tracking"""
        pass

    @abstractmethod
    def stop_tracking(self) -> None:
        """Stop focus tracking"""
        pass

    @abstractmethod
    def get_current_state(self) -> FocusState:
        """Get current focus state"""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to tracking events"""
        pass

    @abstractmethod
    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from events"""
        pass


# ============================================================================
# APPLICATION SERVICE INTERFACES (Use Case Contracts)
# ============================================================================

class ISessionService(ABC):
    """Session management use cases"""

    # Events
    ON_SESSION_CREATED = "session_created"
    ON_SESSION_UPDATED = "session_updated"
    ON_SESSION_COMPLETED = "session_completed"

    @abstractmethod
    def create_session(self, config: SessionConfig) -> int:
        """Create new session"""
        pass

    @abstractmethod
    def start_session(self, session_id: int) -> None:
        """Start session tracking"""
        pass

    @abstractmethod
    def complete_session(self, session_id: int, actual_seconds: int) -> SessionSummary:
        """Complete session and calculate summary"""
        pass

    @abstractmethod
    def fail_session(self, session_id: int, reason: str) -> None:
        """Mark session as failed"""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to session events"""
        pass


class IDistractionService(ABC):
    """Distraction tracking use cases"""

    # Events
    ON_DISTRACTION_RECORDED = "distraction_recorded"

    @abstractmethod
    def record_distraction(self, event: DistractionEvent) -> None:
        """Record distraction event"""
        pass

    @abstractmethod
    def get_session_distractions(self, session_id: int) -> List[DistractionEvent]:
        """Get all distractions for session"""
        pass

    @abstractmethod
    def get_statistics(self, session_id: int) -> dict:
        """Get distraction statistics"""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to distraction events"""
        pass


class IStatisticsService(ABC):
    """Analytics and reporting use cases"""

    @abstractmethod
    def calculate_session_summary(self, session_id: int) -> SessionSummary:
        """Calculate complete session summary"""
        pass

    @abstractmethod
    def get_productivity_score(self, session_id: int) -> float:
        """Calculate productivity score (0.0 - 1.0)"""
        pass

    @abstractmethod
    def get_daily_stats(self, date: str) -> dict:
        """Get daily statistics"""
        pass


# ============================================================================
# UI PRESENTATION INTERFACES (View Model Contracts)
# ============================================================================

class ICreateSessionViewModel(ABC):
    """View model for session creation"""

    # Events
    ON_SESSION_STARTED = "session_started"
    ON_VALIDATION_ERROR = "validation_error"

    @abstractmethod
    def validate_input(self, subject: str, duration: int, keywords: List[str]) -> bool:
        """Validate session input"""
        pass

    @abstractmethod
    def start_session(self, config: SessionConfig) -> int:
        """Start new session"""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to events"""
        pass


class ISessionHistoryViewModel(ABC):
    """View model for session history"""

    @abstractmethod
    def load_sessions(self) -> List[SessionSummary]:
        """Load all sessions"""
        pass

    @abstractmethod
    def get_session_details(self, session_id: int) -> SessionSummary:
        """Get session details"""
        pass


class IFocusTrackingViewModel(ABC):
    """View model for live focus tracking"""

    # Events
    ON_FOCUS_STATE_CHANGED = "focus_state_changed"
    ON_TIME_UPDATED = "time_updated"

    @abstractmethod
    def get_current_state(self) -> dict:
        """Get current tracking state"""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to tracking events"""
        pass
```

---

## 3. Module Directory Structure

```
focus_garden/
├── shared/                          # Shared interfaces & contracts
│   ├── __init__.py
│   ├── interfaces.py                # All abstract interfaces
│   ├── domain_entities.py           # Data classes & enums
│   ├── events.py                    # Event system
│   └── exceptions.py                # Custom exceptions
│
├── core_domain/                     # Module 1: Business Logic
│   ├── __init__.py
│   ├── validators/                  # Business rule validators
│   │   ├── session_validator.py
│   │   └── keyword_validator.py
│   ├── state_machines/              # Domain logic
│   │   └── focus_state_machine.py
│   └── value_objects/               # Value objects
│       └── time_range.py
│
├── tracking_engine/                 # Module 2: Window Monitoring
│   ├── __init__.py
│   ├── implementations/
│   │   ├── window_monitor.py        # IWindowMonitor impl
│   │   ├── keyword_matcher.py       # IKeywordMatcher impl
│   │   ├── browser_parser.py        # IBrowserParser impl
│   │   └── focus_tracker.py         # IFocusTracker impl
│   └── mocks/                       # Mock implementations
│       ├── mock_window_monitor.py
│       ├── mock_keyword_matcher.py
│       └── mock_focus_tracker.py
│
├── data_persistence/                # Module 3: Database Layer
│   ├── __init__.py
│   ├── models/                      # SQLAlchemy models
│   │   ├── session_model.py
│   │   └── distraction_model.py
│   ├── repositories/                # Repository implementations
│   │   ├── session_repository.py    # ISessionRepository impl
│   │   └── distraction_repository.py # IDistractionRepository impl
│   ├── migrations/                  # DB migrations
│   │   └── migration_001_init.py
│   └── mocks/                       # Mock implementations
│       ├── mock_session_repository.py
│       └── mock_distraction_repository.py
│
├── application_services/            # Module 4: Use Cases
│   ├── __init__.py
│   ├── services/
│   │   ├── session_service.py       # ISessionService impl
│   │   ├── distraction_service.py   # IDistractionService impl
│   │   └── statistics_service.py    # IStatisticsService impl
│   ├── event_bus/                   # Event system
│   │   └── event_bus.py
│   └── di_container/                # Dependency Injection
│       └── container.py
│
├── ui_presentation/                 # Module 5: User Interface
│   ├── __init__.py
│   ├── views/                       # PyQt6 widgets
│   │   ├── main_window.py
│   │   ├── create_session_view.py
│   │   └── history_view.py
│   ├── viewmodels/                  # View models
│   │   ├── create_session_viewmodel.py
│   │   ├── history_viewmodel.py
│   │   └── tracking_viewmodel.py
│   └── styles/                      # UI styling
│       └── theme.py
│
├── cross_cutting/                   # Module 6: Shared Infrastructure
│   ├── __init__.py
│   ├── logging/
│   │   └── logger.py
│   ├── config/
│   │   └── settings.py
│   └── utils/
│       └── helpers.py
│
└── main.py                          # Application entry point
```

---

## 4. Mocking Mechanism for Parallel Coding

### Mock: `tracking_engine/mocks/mock_focus_tracker.py`

```python
"""Mock FocusTracker for UI development without real tracking."""
from shared.interfaces import IFocusTracker, FocusState, WindowInfo
from typing import List, Callable, Dict
import time


class MockFocusTracker(IFocusTracker):
    """Mock implementation for parallel UI development."""

    def __init__(self):
        self._state = FocusState.FOCUSING
        self._callbacks: Dict[str, List[Callable]] = {}
        self._is_tracking = False
        self._mock_timer = None

    def start_tracking(self, keywords: List[str]) -> None:
        """Start mock tracking with simulated behavior."""
        self._is_tracking = True
        print(f"[MOCK] Tracking started with keywords: {keywords}")

        # Simulate distractions every 10 seconds
        def simulate():
            if self._is_tracking:
                # Simulate distraction
                self._state = FocusState.DISTRACTED
                self._emit(self.ON_DISTRACTION_DETECTED, "Mock Browser", 5)

                # Return to focusing after 5 seconds
                time.sleep(5)
                self._state = FocusState.FOCUSING
                self._emit(self.ON_FOCUS_STATE_CHANGED, self._state)

    def stop_tracking(self) -> None:
        """Stop mock tracking."""
        self._is_tracking = False
        print("[MOCK] Tracking stopped")

    def get_current_state(self) -> FocusState:
        """Get current mock state."""
        return self._state

    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to mock events."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from mock events."""
        if event in self._callbacks:
            self._callbacks[event].remove(callback)

    def _emit(self, event: str, *args) -> None:
        """Emit event to subscribers."""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args)


# Usage example for UI development:
if __name__ == "__main__":
    tracker = MockFocusTracker()

    def on_distraction(app, duration):
        print(f"[MOCK] Distraction: {app} for {duration}s")

    tracker.subscribe(tracker.ON_DISTRACTION_DETECTED, on_distraction)
    tracker.start_tracking(["vscode", "chrome"])
```

### Mock: `data_persistence/mocks/mock_session_repository.py`

```python
"""Mock SessionRepository for testing without database."""
from shared.interfaces import ISessionRepository, SessionConfig, SessionSummary, SessionState
from typing import List, Optional


class MockSessionRepository(ISessionRepository):
    """In-memory session storage for testing."""

    def __init__(self):
        self._sessions: dict = {}
        self._id_counter = 1

    def create(self, config: SessionConfig) -> int:
        """Create mock session."""
        session_id = self._id_counter
        self._id_counter += 1

        self._sessions[session_id] = {
            "id": session_id,
            "config": config,
            "state": SessionState.CREATED,
            "actual_seconds": 0,
            "distractions": []
        }
        print(f"[MOCK] Created session {session_id}: {config.subject}")
        return session_id

    def get_by_id(self, session_id: int) -> Optional[SessionSummary]:
        """Get mock session."""
        session = self._sessions.get(session_id)
        if session:
            return SessionSummary(
                session_id=session["id"],
                subject=session["config"].subject,
                target_minutes=session["config"].target_duration_minutes,
                actual_seconds=session["actual_seconds"],
                distraction_count=len(session["distractions"]),
                total_distraction_seconds=sum(d["duration"] for d in session["distractions"]),
                state=session["state"]
            )
        return None

    def get_all(self) -> List[SessionSummary]:
        """Get all mock sessions."""
        return [self.get_by_id(sid) for sid in self._sessions.keys()]

    def update_state(self, session_id: int, state: SessionState) -> None:
        """Update mock state."""
        if session_id in self._sessions:
            self._sessions[session_id]["state"] = state
            print(f"[MOCK] Session {session_id} state: {state.value}")

    def update_duration(self, session_id: int, actual_seconds: int) -> None:
        """Update mock duration."""
        if session_id in self._sessions:
            self._sessions[session_id]["actual_seconds"] = actual_seconds
            print(f"[MOCK] Session {session_id} duration: {actual_seconds}s")
```

### Mock: `data_persistence/mocks/mock_distraction_repository.py`

```python
"""Mock DistractionRepository for testing without database."""
from shared.interfaces import IDistractionRepository, DistractionEvent
from typing import List


class MockDistractionRepository(IDistractionRepository):
    """In-memory distraction storage for testing."""

    def __init__(self):
        self._distractions: dict = {}  # session_id -> List[DistractionEvent]

    def save(self, event: DistractionEvent) -> None:
        """Save mock distraction."""
        if event.session_id not in self._distractions:
            self._distractions[event.session_id] = []
        self._distractions[event.session_id].append(event)
        print(f"[MOCK] Saved distraction: {event.app_name} ({event.duration_seconds}s)")

    def get_by_session(self, session_id: int) -> List[DistractionEvent]:
        """Get mock distractions."""
        return self._distractions.get(session_id, [])

    def get_stats(self, session_id: int) -> dict:
        """Get mock statistics."""
        events = self.get_by_session(session_id)
        return {
            "count": len(events),
            "total_seconds": sum(e.duration_seconds for e in events),
            "details": [{"app": e.app_name, "seconds": e.duration_seconds} for e in events]
        }
```

### Mock Usage Example: `ui_presentation/examples/test_ui_with_mocks.py`

```python
"""Example: Develop UI with mocks, no database or real tracking needed."""
import sys
from PyQt6.QtWidgets import QApplication
from ui_presentation.views.create_session_view import CreateSessionView
from data_persistence.mocks.mock_session_repository import MockSessionRepository
from data_persistence.mocks.mock_distraction_repository import MockDistractionRepository
from tracking_engine.mocks.mock_focus_tracker import MockFocusTracker
from shared.interfaces import SessionConfig


def test_ui_with_mocks():
    """Test UI completely isolated with mocks."""
    app = QApplication(sys.argv)

    # Create mock dependencies
    mock_session_repo = MockSessionRepository()
    mock_distraction_repo = MockDistractionRepository()
    mock_tracker = MockFocusTracker()

    # Create UI with mocks
    view = CreateSessionView(
        session_repository=mock_session_repo,
        tracker=mock_tracker
    )

    # Simulate user interaction
    config = SessionConfig(
        subject="Test Session",
        target_duration_minutes=25,
        allowed_keywords=["vscode", "chrome"]
    )

    # This works without real database or tracking!
    session_id = mock_session_repo.create(config)
    print(f"Created session: {session_id}")

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    test_ui_with_mocks()
```

---

## 5. Dependency Injection Container

### File: `application_services/di_container/container.py`

```python
"""Dependency Injection Container for wiring dependencies."""
from shared.interfaces import *
from tracking_engine.implementations.focus_tracker import FocusTracker
from tracking_engine.implementations.window_monitor import WindowMonitor
from tracking_engine.implementations.keyword_matcher import KeywordMatcher
from tracking_engine.implementations.browser_parser import BrowserParser
from data_persistence.repositories.session_repository import SessionRepository
from data_persistence.repositories.distraction_repository import DistractionRepository
from application_services.services.session_service import SessionService
from application_services.services.distraction_service import DistractionService
from application_services.services.statistics_service import StatisticsService


class DIContainer:
    """Central dependency wiring."""

    def __init__(self, use_mocks=False):
        self._use_mocks = use_mocks
        self._singletons = {}

    def get_session_repository(self) -> ISessionRepository:
        """Get session repository (real or mock)."""
        if "session_repo" not in self._singletons:
            if self._use_mocks:
                from data_persistence.mocks.mock_session_repository import MockSessionRepository
                self._singletons["session_repo"] = MockSessionRepository()
            else:
                self._singletons["session_repo"] = SessionRepository()
        return self._singletons["session_repo"]

    def get_distraction_repository(self) -> IDistractionRepository:
        """Get distraction repository (real or mock)."""
        if "distraction_repo" not in self._singletons:
            if self._use_mocks:
                from data_persistence.mocks.mock_distraction_repository import MockDistractionRepository
                self._singletons["distraction_repo"] = MockDistractionRepository()
            else:
                self._singletons["distraction_repo"] = DistractionRepository()
        return self._singletons["distraction_repo"]

    def get_window_monitor(self) -> IWindowMonitor:
        """Get window monitor (real or mock)."""
        if "window_monitor" not in self._singletons:
            if self._use_mocks:
                from tracking_engine.mocks.mock_window_monitor import MockWindowMonitor
                self._singletons["window_monitor"] = MockWindowMonitor()
            else:
                self._singletons["window_monitor"] = WindowMonitor()
        return self._singletons["window_monitor"]

    def get_keyword_matcher(self) -> IKeywordMatcher:
        """Get keyword matcher."""
        if "keyword_matcher" not in self._singletons:
            self._singletons["keyword_matcher"] = KeywordMatcher()
        return self._singletons["keyword_matcher"]

    def get_browser_parser(self) -> IBrowserParser:
        """Get browser parser."""
        if "browser_parser" not in self._singletons:
            self._singletons["browser_parser"] = BrowserParser()
        return self._singletons["browser_parser"]

    def get_focus_tracker(self) -> IFocusTracker:
        """Get focus tracker (wired with dependencies)."""
        if "focus_tracker" not in self._singletons:
            if self._use_mocks:
                from tracking_engine.mocks.mock_focus_tracker import MockFocusTracker
                self._singletons["focus_tracker"] = MockFocusTracker()
            else:
                self._singletons["focus_tracker"] = FocusTracker(
                    monitor=self.get_window_monitor(),
                    matcher=self.get_keyword_matcher(),
                    parser=self.get_browser_parser()
                )
        return self._singletons["focus_tracker"]

    def get_session_service(self) -> ISessionService:
        """Get session service (wired with dependencies)."""
        if "session_service" not in self._singletons:
            self._singletons["session_service"] = SessionService(
                session_repo=self.get_session_repository(),
                distraction_repo=self.get_distraction_repository(),
                tracker=self.get_focus_tracker()
            )
        return self._singletons["session_service"]

    def get_distraction_service(self) -> IDistractionService:
        """Get distraction service (wired with dependencies)."""
        if "distraction_service" not in self._singletons:
            self._singletons["distraction_service"] = DistractionService(
                repo=self.get_distraction_repository()
            )
        return self._singletons["distraction_service"]

    def get_statistics_service(self) -> IStatisticsService:
        """Get statistics service (wired with dependencies)."""
        if "statistics_service" not in self._singletons:
            self._singletons["statistics_service"] = StatisticsService(
                session_repo=self.get_session_repository(),
                distraction_repo=self.get_distraction_repository()
            )
        return self._singletons["statistics_service"]
```

---

## 6. Data Flow & Integration

### Flow: Creating a Session

```
[UI] → [ViewModel] → [SessionService] → [SessionRepository]
                          ↓
                    [FocusTracker]
                          ↓
                    [WindowMonitor]
```

**Step-by-step:**
1. User clicks "Start Session" in UI
2. CreateSessionViewModel validates input
3. ViewModel calls SessionService.create_session()
4. SessionService uses SessionRepository to save to DB
5. SessionService starts FocusTracker
6. FocusTracker polls WindowMonitor every second
7. Events are emitted via observer pattern
8. UI updates reactively via subscriptions

### Flow: Recording a Distraction

```
[WindowMonitor] → [FocusTracker] → [DistractionService] → [DistractionRepository]
                                ↓
                         [Event Bus]
                                ↓
                           [UI Update]
```

**Step-by-step:**
1. WindowMonitor detects window change
2. FocusTracker state machine processes
3. FocusTracker emits ON_DISTRACTION_DETECTED event
4. DistractionService listens and saves to repository
5. UI subscribed to event updates display

### Event Bus Implementation

```python
"""Simple event bus for module communication."""
from typing import Dict, List, Callable


class EventBus:
    """Central event dispatcher for loose coupling."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from event."""
        if event in self._subscribers:
            self._subscribers[event].remove(callback)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to all subscribers."""
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                callback(*args, **kwargs)


# Global event bus instance
event_bus = EventBus()
```

---

## 7. Parallel Development Strategy

### Team A: Core Domain & Business Logic
**Files to work on:**
- `core_domain/validators/*.py`
- `core_domain/state_machines/*.py`
- `shared/interfaces.py` (define contracts)

**Dependencies:** None (pure Python)

**Testing:** Use unit tests with mocks

### Team B: Tracking Engine
**Files to work on:**
- `tracking_engine/implementations/*.py`
- `tracking_engine/mocks/*.py`

**Dependencies:** `shared/interfaces.py`

**Testing:** Mock window monitor for testing

### Team C: Data Persistence
**Files to work on:**
- `data_persistence/models/*.py`
- `data_persistence/repositories/*.py`
- `data_persistence/mocks/*.py`

**Dependencies:** `shared/interfaces.py`

**Testing:** Use in-memory SQLite

### Team D: Application Services
**Files to work on:**
- `application_services/services/*.py`
- `application_services/di_container/*.py`

**Dependencies:** All other modules (via interfaces)

**Testing:** Wire with mock implementations

### Team E: UI Presentation
**Files to work on:**
- `ui_presentation/views/*.py`
- `ui_presentation/viewmodels/*.py`

**Dependencies:** `application_services` (via interfaces)

**Testing:** Use mock services for UI testing

---

## 8. Implementation Phases

### Phase 1: Foundation (Week 1)
1. Create `shared/` module with all interfaces
2. Set up project structure
3. Create mock implementations
4. Set up DI container

### Phase 2: Core Domain (Week 2)
1. Implement validators
2. Implement state machine
3. Unit test business rules

### Phase 3: Data Layer (Week 3)
1. Implement SQLAlchemy models
2. Implement repositories
3. Write migration scripts
4. Test with in-memory DB

### Phase 4: Tracking Engine (Week 4)
1. Implement window monitor
2. Implement keyword matcher
3. Implement browser parser
4. Integrate state machine

### Phase 5: Application Services (Week 5)
1. Implement session service
2. Implement distraction service
3. Implement statistics service
4. Wire dependencies in DI container

### Phase 6: UI Implementation (Week 6)
1. Implement view models
2. Implement views with PyQt6
3. Wire events to UI
4. Integration testing

### Phase 7: Integration & Testing (Week 7)
1. Replace mocks with real implementations
2. End-to-end testing
3. Performance optimization
4. Documentation

---

## 9. Success Criteria

- ✅ All modules can be developed in parallel
- ✅ UI can be tested without database
- ✅ Business logic can be tested without UI
- ✅ Tracking engine can be tested independently
- ✅ Zero circular dependencies
- ✅ All communication via interfaces
- ✅ Complete mock coverage
- ✅ 100% test coverage possible

---

## 10. Next Steps

1. **Review & Approval**: Review this architecture plan
2. **Setup**: Create directory structure
3. **Interfaces**: Implement `shared/interfaces.py`
4. **Mocks**: Create all mock implementations
5. **DI Container**: Set up dependency injection
6. **Parallel Development**: Teams start on their modules
7. **Integration**: Wire modules together
8. **Testing**: Comprehensive testing

---

**Status**: Ready for implementation
**Estimated Timeline**: 7 weeks
**Team Size**: 5 developers (1 per module + integration)
