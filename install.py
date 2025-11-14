#!/usr/bin/env python3
"""
Daily Brief Service - Installation Script
Sets up the environment for Raspberry Pi Zero W2
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description=""):
    """Run a shell command with error handling"""
    if description:
        print(f"📦 {description}...")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_system_dependencies():
    """Install system dependencies for Pi Zero W2"""
    if platform.system() != "Linux":
        print("⚠️  System dependencies skip (not Linux)")
        return True
    
    commands = [
        ("sudo apt update", "Updating package list"),
        ("sudo apt install -y python3-pip python3-venv", "Installing Python tools"),
        ("sudo apt install -y git curl", "Installing utilities"),
        ("sudo apt install -y libssl-dev", "Installing SSL support"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment exists at {venv_path}")
        return True
    
    if not run_command(f"{sys.executable} -m venv {venv_path}", "Creating virtual environment"):
        return False
    
    print(f"✅ Virtual environment created at {venv_path}")
    return True

def install_python_dependencies():
    """Install Python packages"""
    venv_python = "venv/bin/python" if platform.system() != "Windows" else "venv\\Scripts\\python.exe"
    venv_pip = "venv/bin/pip" if platform.system() != "Windows" else "venv\\Scripts\\pip.exe"
    
    # Create requirements.txt if it doesn't exist
    requirements = [
        "flask>=2.0.0",
        "requests>=2.25.0", 
        "python-dotenv>=0.19.0",
        "APScheduler>=3.8.0",
        "psutil>=5.8.0",
    ]
    
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        print("📄 Created requirements.txt")
    
    # Install packages
    commands = [
        (f"{venv_pip} install --upgrade pip", "Upgrading pip"),
        (f"{venv_pip} install -r requirements.txt", "Installing Python packages"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def create_env_template():
    """Create .env template if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file exists")
        return True
    
    env_content = """# Daily Brief Service Configuration

# === Email Configuration ===
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_POLL_INTERVAL=60

# === WhatsApp Business API Configuration ===
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_custom_verify_token_here

# === Service Configuration ===
PORT=5000
HOST=0.0.0.0
DEBUG=false

# === Weather API (Optional) ===
WEATHER_API_KEY=your_openweather_api_key

# === Database ===
DATABASE_URL=daily_brief.db
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📄 Created .env template - please configure your credentials")
    return True

def setup_git_hooks():
    """Setup git hooks for development"""
    if not os.path.exists(".git"):
        print("⚠️  Not a git repository, skipping hooks")
        return True
    
    # Simple pre-commit hook to check .env isn't committed
    hook_content = """#!/bin/sh
# Check if .env is being committed
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "❌ Error: .env file should not be committed!"
    echo "   Add .env to .gitignore"
    exit 1
fi
"""
    
    hook_path = ".git/hooks/pre-commit"
    with open(hook_path, "w") as f:
        f.write(hook_content)
    
    os.chmod(hook_path, 0o755)
    print("✅ Git pre-commit hook installed")
    return True

def check_port_availability():
    """Check if default port is available"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 5000))
        print("✅ Port 5000 is available")
        return True
    except OSError:
        print("⚠️  Port 5000 is in use, will try another port")
        return True

def main():
    print("🚀 Daily Brief Service - Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ Failed to install system dependencies")
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        return False
    
    # Create configuration template
    if not create_env_template():
        print("❌ Failed to create configuration template")
        return False
    
    # Setup development tools
    setup_git_hooks()
    check_port_availability()
    
    print("\n🎉 Installation Complete!")
    print("=" * 25)
    print("Next steps:")
    print("1. 📝 Configure .env file with your credentials")
    print("2. 📱 For WhatsApp: Follow WHATSAPP_SETUP_GUIDE.md")
    print("3. 🚀 Run: python deploy.py --status")
    print("4. 🚀 Run: python deploy.py --email (or --whatsapp)")
    print("\n💡 For Pi Zero W2: Use --whatsapp mode for best performance!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)