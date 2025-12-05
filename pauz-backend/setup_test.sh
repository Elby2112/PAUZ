#!/bin/bash

echo "🎵 ElevenLabs API Test Setup"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

echo "✅ Python3 found"

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements_elevenlabs.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages. Trying with pip..."
    pip install -r requirements_elevenlabs.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Package installation failed. You may need to install manually:"
        echo "   pip3 install requests pyaudio"
        echo "   Note: On macOS, you might need: brew install portaudio"
        echo "   On Ubuntu: sudo apt-get install python3-pyaudio"
        exit 1
    fi
fi

echo "✅ Packages installed successfully"

# Ask for API key
echo ""
echo "🔑 Please enter your ElevenLabs API key:"
read -s api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided"
    exit 1
fi

# Create environment file
echo "ELEVENLABS_API_KEY=$api_key" > .env
echo "✅ API key saved to .env file"

# Make the script executable
chmod +x test_elevenlabs.py

echo ""
echo "🎯 Setup complete! You can now run the test:"
echo "   source .env"
echo "   python3 test_elevenlabs.py"
echo ""
echo "Or simply run:"
echo "   ELEVENLABS_API_KEY='$api_key' python3 test_elevenlabs.py"