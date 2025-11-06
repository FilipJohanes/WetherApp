#!/usr/bin/env python3
"""
Setup script for Daily Brief Service

This script helps set up the development environment and
verifies that everything is configured correctly.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}")


def print_step(step, text):
    """Print a formatted step."""
    print(f"\n{step}. {text}")
    print("-" * 40)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version}")
        print("Please upgrade Python and try again.")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")
        return True


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            print(f"💡 Activate with: {activate_script}")
        else:  # Unix-like
            activate_script = venv_path / "bin" / "activate"
            print(f"💡 Activate with: source {activate_script}")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def install_dependencies():
    """Install required dependencies."""
    try:
        print("📥 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def setup_environment_file():
    """Set up environment configuration file.""" 
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env from template")
        print("⚠️  Please edit .env with your email credentials")
        print("💡 Use app-specific passwords for Gmail")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env: {e}")
        return False


def verify_files():
    """Verify all required files exist."""
    required_files = [
        "app.py",
        "requirements.txt",
        "weather_messages.txt",
        ".env.example",
        ".gitignore",
        "LICENSE",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0


def run_tests():
    """Run development tests."""
    try:
        print("🧪 Running development examples...")
        subprocess.run([sys.executable, "examples/development_examples.py"], check=True)
        print("✅ Development examples completed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Development examples failed")
        return False
    except FileNotFoundError:
        print("⚠️  Development examples not found, skipping...")
        return True


def main():
    """Main setup function."""
    print_header("Daily Brief Service Setup")
    
    success = True
    
    print_step(1, "Checking Python Version")
    if not check_python_version():
        success = False
    
    print_step(2, "Verifying Required Files")
    if not verify_files():
        success = False
        
    print_step(3, "Setting Up Virtual Environment")
    if not setup_virtual_environment():
        success = False
    
    print_step(4, "Installing Dependencies")
    if not install_dependencies():
        success = False
    
    print_step(5, "Setting Up Environment Configuration")
    if not setup_environment_file():
        success = False
        
    print_step(6, "Running Development Tests")
    if not run_tests():
        success = False
    
    # Final status
    if success:
        print_header("Setup Complete! 🎉")
        print("✅ All setup steps completed successfully")
        print("\n📋 Next Steps:")
        print("   1. Edit .env with your email credentials")
        print("   2. Test configuration: python app.py --send-test your@email.com")
        print("   3. Run dry mode: python app.py --dry-run")
        print("   4. Start service: python app.py")
        
        print("\n🔧 Development Commands:")
        print("   - List subscribers: python app.py --list-subs")
        print("   - List reminders: python app.py --list-reminders") 
        print("   - Run tests: python -m pytest tests/")
        
        print("\n📚 Documentation:")
        print("   - README.md - Complete usage guide")
        print("   - examples/ - Development examples")
        print("   - tests/ - Unit tests")
        
    else:
        print_header("Setup Incomplete ❌")
        print("Some setup steps failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()