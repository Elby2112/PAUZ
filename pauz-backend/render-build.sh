#!/bin/bash

# Update package list and install PortAudio dev libraries
sudo apt-get update
sudo apt-get install -y portaudio19-dev

# Upgrade pip just in case
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
