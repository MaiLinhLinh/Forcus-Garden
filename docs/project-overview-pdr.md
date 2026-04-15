# Project Overview & Product Development Requirements (PDR) - Focus Garden

## Executive Summary

Focus Garden is a sophisticated real-time distraction tracking and productivity monitoring application designed to help users maintain focus and understand their digital habits. Built with a modular architecture in Python and PyQt6, the application combines advanced fuzzy matching technology with comprehensive analytics to provide actionable insights into user behavior.

**Current Status**: Phase 2 completed with 100% test success rate, ready for Phase 3 analytics development.

### Key Achievements (April 2026)
- ✅ RapidFuzzy integration with 85% accuracy threshold
- ✅ Complete Vietnamese language support with Unicode normalization
- ✅ Smart browser title parsing for accurate website tracking
- ✅ Comprehensive alias system for natural keyword matching
- ✅ Modular architecture (all files <200 lines)
- ✅ 100% test coverage (22/22 tests passed)

## Project Vision

Focus Garden aims to become the leading productivity application by combining cutting-edge technology with user-centered design. Our vision is to create a platform that not only tracks digital habits but actively helps users improve their focus, productivity, and overall digital wellbeing.

### Core Value Proposition
- **Accuracy**: Advanced fuzzy matching ensures reliable distraction detection
- **Usability**: Intuitive interface with minimal learning curve
- **Insight**: Comprehensive analytics provide actionable intelligence
- **Privacy**: Local data storage with full user control
- **Accessibility**: Multi-language support with Vietnamese-first approach

## Product Features

### Current Features (Phase 1-2 Completed)

#### 1. Real-time Distraction Tracking
- **Window Monitoring**: 1-second polling to detect active applications
- **Fuzzy Matching**: 85% threshold keyword detection using RapidFuzz
- **Smart Parsing**: Browser title parsing extracts actual site names
- **State Machine**: FOCUSING ↔ DISTRACTED transitions with 10-second buffer

#### 2. Multi-language Support
- **Vietnamese Unicode**: Full diacritic support with NFC normalization
- **English Compatibility**: Seamless bilingual operation
- **Text Normalization**: Consistent matching across character encodings
- **Cultural Adaptation**: Localized for Vietnamese user base

#### 3. Application Alias System
- **Comprehensive Dictionary**: Built-in mapping for common development tools
- **Natural Matching**: Users can type "vscode" to match "Visual Studio Code"
- **Reverse Lookup**: Bidirectional alias expansion
- **Case Insensitive**: Flexible input handling

#### 4. Browser Intelligence
- **Multi-browser Support**: Chrome, Firefox, Edge, Opera, Brave, Vivaldi
- **Site Extraction**: Intelligent parsing of browser window titles
- **Grouped Tab Detection**: Handles "Facebook and 3 other tabs" scenarios
- **Browser-specific Parsing**: Optimized patterns for each browser

#### 5. Data Management
- **SQLite Storage**: Local database for performance and privacy
- **Session Tracking**: Complete session history with timestamps
- **Statistics**: Distraction frequency, duration, and patterns
- **Export Capabilities**: Data export for external analysis

#### 6. User Interface
- **PyQt6 Framework**: Modern, responsive desktop interface
- **Session Creation**: Easy setup of focus sessions with custom keywords
- **History Viewer**: Session playback and filtering
- **Summary Reports**: Productivity insights and statistics

### Planned Features (Phase 3-6)

#### Phase 3: Enhanced Analytics (Q2 2026)
- **Dashboard Visualization**: Interactive charts and progress tracking
- **Goal Setting**: Personalized productivity targets
- **Pattern Recognition**: Identify distraction patterns and trends
- **Weekly/Monthly Reports**: Comprehensive productivity summaries
- **Focus Scoring**: Real-time productivity scoring system

#### Phase 4: Cloud Integration (Q3 2026)
- **Multi-device Sync**: Cross-platform data synchronization
- **Remote Backup**: Cloud backup with encryption
- **Collaborative Features**: Team focus sessions and sharing
- **API Access**: Third-party integrations
- **Offline Mode**: Full functionality without internet

#### Phase 5: Mobile Applications (Q4 2026)
- **iOS Application**: Native iOS app with feature parity
- **Android Application**: Native Android app with optimizations
- **Cross-platform Sync**: Real-time synchronization between devices
- **Mobile Notifications**: Focus reminders and alerts
- **Location-based Features**: Context-aware productivity tracking

#### Phase 6: AI-Powered Assistant (Q1 2027)
- **Machine Learning**: Predictive analytics for focus patterns
- **Intelligent Recommendations**: Personalized productivity suggestions
- **Automatic Optimization**: Self-improving focus algorithms
- **Natural Language Processing**: Voice commands and chat interface
- **Predictive Distraction Alerts**: Proactive distraction prevention

## Technical Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────┐ │
│  │ Main Window │ │ Session Cre│ │ History     │ │ Summ│ │
│  │             │ │ ation       │ │ Viewer      │ │ ary │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │ Dia │ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Core Engine Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────┐ │
│  │ Keyword     │ │ Browser     │ │ Normalizer  │ │ Sta │ │
│  │ Matcher     │ │ Parser      │ │             │ │ te  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │ Mach │ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ ine │ │
│  │ Alias       │ │ State       │ │ Tracker     │ │     │ │
│  │ Manager     │ │ Machine     │ │             │ │     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────┐ │
│  │ SQLite      │ │ Models      │ │ Repository  │ │ Migr│ │
│  │ Database    │ │             │ │             │ │ atio│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │ ns  │ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python 3.12+, PyQt6, SQLite3
- **Matching**: RapidFuzz, Unicode NFC
- **Testing**: unittest framework, 100% coverage
- **Architecture**: Modular design (<200 lines per module)
- **Languages**: Python, Vietnamese, English

### Key Technologies
1. **RapidFuzz**: Advanced fuzzy string matching library
2. **PyQt6**: Modern GUI framework for desktop applications
3. **SQLite**: Lightweight local database
4. **Unicode NFC**: Text normalization for internationalization
5. **Regex**: Pattern matching for browser parsing

## Product Development Requirements

### Functional Requirements

#### FR1: Real-time Distraction Detection
- **FR1.1**: Monitor active window titles every 1 second
- **FR1.2**: Match window titles against user-defined keywords with 85% accuracy
- **FR1.3**: Support Vietnamese and English text matching
- **FR1.4**: Maintain FOCUSING ↔ DISTRACTED state transitions
- **FR1.5**: Record distraction events with timestamps

#### FR2: Keyword Matching System
- **FR2.1**: Implement fuzzy matching using RapidFuzz library
- **FR2.2**: Support exact substring matching for performance
- **FR2.3**: Provide configurable threshold (default 85%)
- **FR2.4**: Handle special character normalization
- **FR2.5**: Support alias expansion for keyword variations

#### FR3: Browser Integration
- **FR3.1**: Parse browser window titles to extract site names
- **FR3.2**: Support major browsers (Chrome, Firefox, Edge, etc.)
- **FR3.3**: Handle grouped tab scenarios ("Facebook and 3 other tabs")
- **FR3.4**: Distinguish between browser and non-browser windows
- **FR3.5**: Maintain browser-specific parsing accuracy

#### FR4: Data Management
- **FR4.1**: Store sessions, distractions, and app usage in SQLite
- **FR4.2**: Support automatic schema migrations
- **FR4.3**: Provide data export functionality
- **FR4.4**: Maintain data integrity and relationships
- **FR4.5**: Support large datasets with performance optimization

#### FR5: User Interface
- **FR5.1**: Provide intuitive desktop interface with PyQt6
- **FR5.2**: Support session creation and management
- **FR5.3**: Display session history with filtering
- **FR5.4**: Show productivity summaries and statistics
- **FR5.5**: Ensure responsive and accessible design

### Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: Window title processing <1ms per title (fast path)
- **NFR1.2**: Application startup <3 seconds
- **NFR1.3**: Database queries <100ms for typical operations
- **NFR1.4**: Memory usage <100MB for typical workloads
- **NFR1.5**: CPU usage <5% for continuous monitoring

#### NFR2: Reliability
- **NFR2.1**: 99.9% uptime for continuous monitoring
- **NFR2.2**: Graceful degradation on system errors
- **NFR2.3**: Automatic recovery from temporary failures
- **NFR2.4**: Comprehensive error handling and logging
- **NFR2.5**: Data integrity protection

#### NFR3: Security
- **NFR3.1**: Local data storage with encryption option
- **NFR3.2**: No external data transmission without user consent
- **NFR3.3**: Secure password handling for cloud features
- **NFR3.4**: Protection against injection attacks
- **NFR3.5**: Regular security audits and updates

#### NFR4: Usability
- **NFR4.1**: Intuitive interface with minimal learning curve
- **NFR4.2**: Vietnamese language interface with full Unicode support
- **NFR4.3**: Context-sensitive help and documentation
- **NFR4.4**: Responsive design for various screen sizes
- **NFR4.5**: Keyboard navigation support

#### NFR5: Maintainability
- **NFR5.1**: Modular architecture with single responsibility
- **NFR5.2**: All core modules <200 lines of code
- **NFR5.3**: 100% test coverage for critical components
- **NFR5.4**: Comprehensive documentation and code comments
- **NFR5.5**: Clear separation of concerns between layers

### Technical Requirements

#### TR1: Code Quality
- **TR1.1**: Follow PEP 8 Python coding standards
- **TR1.2**: Maintain 100% test coverage for core functionality
- **TR1.3**: Use type hints for all public interfaces
- **TR1.4**: Implement comprehensive error handling
- **TR1.5**: Follow modular design principles

#### TR2: Architecture
- **TR2.1**: Maintain loose coupling between components
- **TR2.2**: Implement clear interfaces between modules
- **TR2.3**: Use appropriate design patterns
- **TR2.4**: Ensure scalability for future features
- **TR2.5**: Support multiple operating systems

#### TR3: Performance Optimization
- **TR3.1**: Implement fast path optimization for common operations
- **TR3.2**: Use efficient data structures (sets, dictionaries)
- **TR3.3**: Cache frequently accessed data
- **TR3.4**: Profile and optimize critical paths
- **TR3.5**: Monitor memory usage and prevent leaks

## Quality Assurance Requirements

### Testing Strategy

#### Unit Testing
- **Coverage**: 100% line coverage for core modules
- **Framework**: unittest with comprehensive test suites
- **Categories**: Unit, integration, performance, edge case
- **Automation**: Automated test execution on commits
- **Performance**: Speed and memory validation tests

#### Integration Testing
- **Module Interaction**: Test data flow between components
- **Interface Validation**: Verify API contracts between modules
- **Database Testing**: Test data persistence and relationships
- **UI Testing**: Test user interface functionality and responsiveness
- **End-to-end Testing**: Test complete user workflows

#### Performance Testing
- **Benchmarking**: Measure matching speed and accuracy
- **Load Testing**: Test under typical and peak workloads
- **Memory Testing**: Monitor memory usage patterns
- **Response Time**: Ensure real-time performance targets
- **Stress Testing**: Test system limits and failure modes

### Quality Metrics

#### Code Quality Metrics
- **Test Coverage**: 100% for core functionality
- **Code Complexity**: Maintain cyclomatic complexity <10
- **Documentation**: Complete docstrings and comments
- **Standards**: 100% adherence to coding standards
- **Dependencies**: Minimal external dependencies

#### Performance Metrics
- **Response Time**: <1ms for window processing
- **Memory Usage**: <100MB for typical workloads
- **CPU Usage**: <5% for continuous monitoring
- **Database Performance**: <100ms for typical queries
- **Startup Time**: <3 seconds for application launch

#### User Experience Metrics
- **Interface Responsiveness**: <100ms UI updates
- **Task Completion**: Intuitive workflows for common tasks
- **Error Handling**: Clear error messages and recovery options
- **Accessibility**: Support for assistive technologies
- **Internationalization**: Full Vietnamese language support

## Project Timeline

### Completed Phases
- **Phase 1** (Q4 2025): Core functionality ✅
- **Phase 2** (Q1 2026): Advanced matching & parser ✅

### Current Phase
- **Phase 3** (Q2 2026): Enhanced analytics & reporting 🟡 IN PROGRESS

### Future Phases
- **Phase 4** (Q3 2026): Cloud integration 🟡 PLANNED
- **Phase 5** (Q4 2026): Mobile applications 🟡 PLANNED
- **Phase 6** (Q1 2027): AI-powered assistant 🟡 PLANNED

### Milestones
- **Q2 2026**: Complete Phase 3 analytics
- **Q3 2026**: Launch cloud sync features
- **Q4 2026**: Release mobile applications
- **Q1 2027**: Introduce AI assistant features
- **Q2 2027**: Enterprise version release

## Success Criteria

### Technical Success Criteria
- **Test Coverage**: 100% line coverage maintained
- **Performance**: All performance targets met
- **Reliability**: 99.9% uptime achieved
- **Code Quality**: Modular architecture maintained
- **Scalability**: System handles 100K+ users

### Business Success Criteria
- **User Adoption**: 10K+ monthly active users
- **User Satisfaction**: >90% satisfaction score
- **Feature Adoption**: >80% of users adopt new features
- **Market Position**: Leading productivity app in target market
- **Revenue Generation**: Self-sustaining by Q1 2027

### Innovation Success Criteria
- **Technology Leadership**: Industry recognition for innovation
- **Patent Opportunities**: Unique technologies patented
- **Research Output**: Published research and case studies
- **Community Engagement**: Active developer community
- **Integration Ecosystem**: 50+ third-party integrations

## Conclusion

Focus Garden represents a significant advancement in productivity applications through its sophisticated matching technology, modular architecture, and user-centered design. The successful completion of Phase 2 demonstrates our technical capability and sets a strong foundation for future growth.

The project's commitment to quality is evidenced by:
- 100% test coverage (22/22 tests passed)
- Modular architecture with all files <200 lines
- Comprehensive Vietnamese language support
- Advanced fuzzy matching with 85% accuracy threshold
- Smart browser parsing for accurate tracking

With Phase 3 in progress and a clear roadmap for future development, Focus Garden is positioned to become the leading productivity application, combining technical excellence with genuine user value.

---

*Last Updated: April 15, 2026*
*Version: 2.0.0*
*Status: Phase 2 completed, Phase 3 in progress*
*Next Milestone: Enhanced analytics completion (Q2 2026)*