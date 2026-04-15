# Focus Garden - Setup Guide

## Prerequisites

- Python 3.10 or higher
- Windows 10/11 (currently Windows-only due to pygetwindow)
- Git (optional, for cloning)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd Forcus-Garden
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

The database will be created automatically on first run.

```bash
python main.py
```

## Running the Application

### Start the Application

```bash
python main.py
```

### First Time Setup

1. **Create Study Session**: Enter subject, duration, and study zone keywords
2. **Keywords Examples**: `vscode`, `chrome`, `word`, `github` (one per line)
3. **Start Learning**: Click "BẮT ĐẦU TRỒNG CÂY" to begin tracking

## New Features (Bug Fix Implementation)

### ✅ Fuzzy Matching
- Type "vscode" → Matches "Visual Studio Code"
- Type "chrome" → Matches "Google Chrome"
- 90% accuracy threshold for optimal matching

### ✅ Smart Browser Detection
- Extracts site names from browser titles
- Handles "Facebook and 3 other tabs" correctly
- Works with Chrome, Firefox, Edge, Opera

### ✅ Vietnamese Language Support
- Full Unicode normalization
- Handles Vietnamese diacritics correctly
- Case-insensitive matching

### ✅ Alias System
- "vscode" matches "Visual Studio Code", "VS Code", etc.
- "idea" matches "IntelliJ IDEA", "JetBrains IDEA"
- Comprehensive app variation support

## Project Structure

```
Forcus-Garden/
├── core/                    # Core tracking logic
│   ├── matcher.py          # Fuzzy matching (NEW)
│   ├── normalizer.py       # Text normalization (NEW)
│   ├── alias-manager.py    # App aliases (NEW)
│   ├── browser-parser.py   # Browser title parsing (NEW)
│   └── tracker.py          # Main tracking thread
├── ui/                      # User interface
│   ├── main_window.py      # Main application window
│   ├── create_session_widget.py
│   ├── history_widget.py   # Session history
│   └── tree_widget.py      # Focus tree display
├── database/                # Database layer
│   ├── db_config.py        # Database configuration
│   ├── models.py           # SQLAlchemy models
│   └── session_repo.py     # Session repository
├── docs/                    # Documentation
├── plans/                   # Implementation plans
├── main.py                  # Application entry point
└── requirements.txt         # Python dependencies
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

All modules follow YAGNI/KISS/DRY principles:
- Files under 200 lines
- Modular architecture
- Comprehensive testing
- Vietnamese language support

## Troubleshooting

### Common Issues

**Issue**: "No module named 'PyQt6'"
- **Solution**: `pip install -r requirements.txt`

**Issue**: Window detection not working
- **Solution**: Run as administrator on Windows

**Issue**: Vietnamese characters not displaying
- **Solution**: Ensure terminal/console supports UTF-8 encoding

## Performance Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **CPU**: Any modern processor
- **Storage**: <100MB for application + database

## License

See LICENSE file for details.

## Support

For issues or questions, please refer to documentation in `docs/` directory.
