#!/bin/bash
# Pi Zero 2 W Optimized Setup Script for Daily Brief Service

echo "🥧 Daily Brief Service - Pi Zero 2 W Setup"
echo "========================================"
echo

# Check if running on Pi Zero 2 W
if grep -q "Pi Zero 2" /proc/device-tree/model 2>/dev/null; then
    echo "✅ Pi Zero 2 W detected - Perfect for this service!"
else
    echo "ℹ️  Running setup (not confirmed Pi Zero 2 W, but should work)"
fi

echo "🔧 Optimizing Pi Zero 2 W for Daily Brief Service..."

# Reduce GPU memory to give more RAM to our service
echo "📝 Optimizing memory allocation..."
sudo raspi-config nonint do_memory_split 16
echo "✅ GPU memory set to 16MB (more RAM for our service)"

# Update system
echo "📦 Updating system packages..."
sudo apt update -qq
sudo apt upgrade -y -qq

# Install required packages
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git htop nano

# Create project directory
echo "📁 Setting up project..."
cd /home/pi
if [ ! -d "reminderAPP" ]; then
    git clone https://github.com/FilipJohanes/reminderAPP.git
fi
cd reminderAPP

# Create virtual environment
echo "🏠 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup configuration
echo "⚙️ Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env file - you'll need to edit it with your email settings"
else
    echo "✅ .env file already exists"
fi

# Create systemd service
echo "🔧 Creating system service..."
sudo tee /etc/systemd/system/daily-brief.service > /dev/null << 'EOF'
[Unit]
Description=Daily Brief Email Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/reminderAPP
Environment=PATH=/home/pi/reminderAPP/venv/bin
ExecStart=/home/pi/reminderAPP/venv/bin/python app.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set up log rotation to prevent SD card filling
echo "📊 Setting up log rotation..."
sudo tee /etc/logrotate.d/daily-brief > /dev/null << 'EOF'
/home/pi/reminderAPP/app.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    su pi pi
}
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable daily-brief

echo
echo "✅ Pi Zero 2 W setup complete!"
echo
echo "📝 Next steps:"
echo "1. Edit /home/pi/reminderAPP/.env with your email settings:"
echo "   nano /home/pi/reminderAPP/.env"
echo
echo "2. Test the configuration:"
echo "   cd /home/pi/reminderAPP"
echo "   source venv/bin/activate"
echo "   python app.py --send-test your-email@example.com"
echo
echo "3. Start the service:"
echo "   sudo systemctl start daily-brief"
echo
echo "4. Check service status:"
echo "   sudo systemctl status daily-brief"
echo
echo "5. View logs:"
echo "   sudo journalctl -u daily-brief -f"
echo
echo "🎉 Your Pi Zero 2 W is ready to run Daily Brief Service 24/7!"
echo "💡 Power consumption: ~2W (less than a night light!)"