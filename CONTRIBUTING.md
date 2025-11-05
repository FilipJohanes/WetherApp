# Contributing to Daily Brief Service

Thank you for your interest in contributing to the Daily Brief Service! 🎉

This document provides guidelines and information about contributing to this project.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/daily-brief-service.git
   cd daily-brief-service
   ```
3. **Set up development environment**:
   ```bash
   python setup.py  # Run setup script
   # OR manually:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

## 🛠️ Development Workflow

### Setting Up Your Development Environment

1. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials for testing
   ```

2. **Run Development Examples**:
   ```bash
   python examples/development_examples.py
   ```

3. **Run Tests**:
   ```bash
   python -m pytest tests/ -v
   ```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Run unit tests
   python -m pytest tests/

   # Test with dry-run mode
   python app.py --dry-run

   # Test specific functionality
   python app.py --list-subs
   python app.py --send-test your@email.com
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code style
- **Use type hints** where appropriate
- **Add docstrings** to all functions and classes
- **Keep functions focused** and single-purpose
- **Use descriptive variable names**

### Example Function:
```python
def parse_weather_data(data: Dict[str, Any]) -> WeatherInfo:
    """
    Parse raw weather API response into structured weather information.
    
    Args:
        data: Raw weather data from Open-Meteo API
        
    Returns:
        WeatherInfo object with parsed weather details
        
    Raises:
        ValueError: If required weather fields are missing
    """
    # Implementation here
    pass
```

### Commit Messages

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `test:` - Adding/updating tests
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

Examples:
```
feat: add brutal personality mode for weather reports
fix: handle missing geocoding results gracefully
docs: update README with personality mode examples
test: add unit tests for email parsing
```

## 🧪 Testing Guidelines

### Writing Tests

- **Add tests** for all new features
- **Test edge cases** and error conditions
- **Use descriptive test names**
- **Keep tests focused** on single functionality

### Test Structure:
```python
class TestNewFeature:
    """Test the new feature functionality."""
    
    def test_normal_case(self):
        """Test normal operation."""
        # Test implementation
        
    def test_edge_case(self):
        """Test edge case handling."""
        # Test implementation
        
    def test_error_handling(self):
        """Test error conditions."""
        # Test implementation
```

### Running Tests:
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app

# Run specific test file
python -m pytest tests/test_daily_brief.py -v

# Run specific test
python -m pytest tests/test_daily_brief.py::TestEmailParsing::test_delete_command -v
```

## 🌟 Types of Contributions

### 🐛 Bug Reports
- **Use the issue template** when reporting bugs
- **Provide detailed reproduction steps**
- **Include environment information** (Python version, OS, etc.)
- **Include relevant log outputs**

### ✨ Feature Requests  
- **Describe the use case** clearly
- **Explain the expected behavior**
- **Consider alternative solutions**
- **Check if similar features exist**

### 📖 Documentation
- **Improve README clarity**
- **Add code examples**
- **Fix typos and grammar**
- **Translate documentation**

### 🔧 Code Contributions
- **New personality modes** for weather reports
- **Additional weather conditions**
- **Email provider configurations**
- **CLI improvements**
- **Performance optimizations**
- **Security enhancements**

## 🎯 Contribution Ideas

Looking for something to work on? Here are some ideas:

### Easy (Good for beginners)
- Add more weather conditions to `weather_messages.txt`
- Improve error messages
- Add more email provider examples
- Fix typos in documentation
- Add more unit tests

### Medium
- Add new personality modes (e.g., "professional", "funny")
- Implement weather alerts (temperature thresholds)
- Add support for multiple timezones per user
- Improve email parsing robustness
- Add more CLI commands

### Advanced
- Add web dashboard for managing subscriptions
- Implement weather charts/graphs in emails
- Add support for different email formats (HTML)
- Implement backup/restore functionality
- Add clustering support for multiple instances

## 🔍 Code Review Process

All contributions go through code review:

1. **Automated checks** run on pull requests
2. **Manual review** by maintainers
3. **Discussion** of changes if needed
4. **Approval and merge** once ready

### What We Look For:
- **Code quality** and style compliance
- **Test coverage** for new features
- **Documentation** updates
- **Backward compatibility**
- **Security considerations**

## 🏷️ Release Process

- **Semantic versioning** (MAJOR.MINOR.PATCH)
- **Regular releases** with new features and fixes
- **Release notes** documenting changes
- **Migration guides** for breaking changes

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Email** - For security issues (see SECURITY.md)

## 🙏 Recognition

Contributors are recognized in:
- **README.md** acknowledgments section
- **CONTRIBUTORS.md** file
- **Release notes** for their contributions

Thank you for contributing to Daily Brief Service! 🚀