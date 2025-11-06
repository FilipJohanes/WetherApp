# Project Structure

This document provides an overview of the Daily Brief Service project structure and files.

## 📁 Directory Structure

```
daily-brief-service/
├── 📄 app.py                    # Main application file
├── 📄 setup.py                  # Automated setup script
├── 📄 requirements.txt          # Production dependencies
├── 📄 requirements-dev.txt      # Development dependencies
├── 📄 weather_messages.txt      # Weather personality messages
├── 📄 .env.example             # Environment configuration template
├── 📄 .gitignore               # Git ignore rules
├── 📄 LICENSE                  # MIT License
├── 📄 README.md                # Main documentation
├── 📄 CONTRIBUTING.md          # Contribution guidelines
├── 📁 .github/                 # GitHub templates and workflows
│   ├── 📄 pull_request_template.md
│   └── 📁 ISSUE_TEMPLATE/
│       ├── 📄 bug_report.md
│       ├── 📄 feature_request.md
│       └── 📄 configuration_help.md
├── 📁 examples/                # Development examples
│   └── 📄 development_examples.py
└── 📁 tests/                   # Unit tests
    └── 📄 test_daily_brief.py
```

## 📋 File Descriptions

### Core Application Files

- **`app.py`** - Main application with all service logic
  - Email handling (IMAP/SMTP)
  - Weather API integration  
  - Calendar reminder system
  - Personality-based responses
  - Database management
  - CLI commands

- **`weather_messages.txt`** - Personality messages configuration
  - 21 weather conditions
  - 3 personality modes each (neutral, cute, brutal)
  - Easy to customize and extend

### Configuration Files

- **`.env.example`** - Environment template with:
  - Email provider examples (Gmail, Outlook, Yahoo)
  - Required and optional settings
  - Development configuration options

- **`requirements.txt`** - Production dependencies:
  - `requests` - HTTP client for weather API
  - `APScheduler` - Job scheduling
  - `dateparser` - Flexible date parsing
  - `python-dateutil` - Date utilities

- **`requirements-dev.txt`** - Development tools:
  - `pytest` - Testing framework
  - `black` - Code formatting
  - `flake8` - Code linting
  - `mypy` - Type checking

### Development & Testing

- **`setup.py`** - Automated setup and verification script
- **`examples/development_examples.py`** - Interactive examples and utilities
- **`tests/test_daily_brief.py`** - Comprehensive unit tests

### Documentation

- **`README.md`** - Complete user guide with:
  - Installation instructions
  - Usage examples
  - Configuration guide
  - Troubleshooting

- **`CONTRIBUTING.md`** - Developer guide with:
  - Development workflow
  - Coding standards
  - Testing guidelines
  - Contribution ideas

### GitHub Integration

- **`.github/ISSUE_TEMPLATE/`** - Issue templates for:
  - Bug reports
  - Feature requests  
  - Configuration help

- **`.github/pull_request_template.md`** - PR template with:
  - Change description
  - Testing checklist
  - Documentation requirements

## 🚀 Quick Start Commands

```bash
# Setup everything
python setup.py

# Run development examples
python examples/development_examples.py

# Test configuration
python app.py --send-test your@email.com

# Run in dry mode (no emails sent)
python app.py --dry-run

# Start service
python app.py
```

## 🔧 Development Workflow

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/yourusername/daily-brief-service.git
   cd daily-brief-service
   python setup.py
   ```

2. **Configure Environment**:
   ```bash
   # Edit .env with your email credentials
   cp .env.example .env
   nano .env
   ```

3. **Test and Develop**:
   ```bash
   # Run tests
   python -m pytest tests/

   # Test changes
   python app.py --dry-run

   # Development examples
   python examples/development_examples.py
   ```

4. **Contribute**:
   ```bash
   # Create feature branch
   git checkout -b feature/amazing-feature
   
   # Make changes and test
   # Commit and push
   # Create pull request
   ```

## 📊 Key Features by File

### Email Processing (`app.py`)
- IMAP email fetching with deduplication
- Intelligent command parsing
- Personality mode detection
- Error handling and user feedback

### Weather System (`app.py` + `weather_messages.txt`)
- Open-Meteo API integration
- Condition detection (21 scenarios)
- Personality-based responses (3 modes)
- Clothing recommendations

### Calendar System (`app.py`)
- Flexible date/time parsing
- Repeating reminders (10-minute intervals)
- Timezone-aware scheduling
- Database persistence

### Development Tools
- **Setup automation** - One command setup
- **Testing framework** - Comprehensive test suite
- **Examples** - Interactive development utilities
- **Documentation** - Complete guides and templates

## 🔒 Security & Privacy

- **No API keys required** - Uses free Open-Meteo service
- **Local data storage** - SQLite database only
- **Secure connections** - SSL/TLS for all email
- **Git safety** - Sensitive files in `.gitignore`
- **Development friendly** - Safe examples and tests

This structure ensures the project is:
- ✅ **Easy to set up** - Automated setup script
- ✅ **Developer friendly** - Examples and tests
- ✅ **Well documented** - Comprehensive guides  
- ✅ **GitHub ready** - Templates and workflows
- ✅ **Cross-platform** - Works on Windows/Linux/macOS