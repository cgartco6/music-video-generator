#!/bin/bash
set -e

# Install Python packages (Vercel does this, but we add extra)
pip install -r requirements.txt

# Download static ffmpeg and add to PATH
FFMPEG_VERSION="7.1"
FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
wget -O ffmpeg.tar.xz $FFMPEG_URL
tar -xf ffmpeg.tar.xz
mv ffmpeg-*-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg
export PATH=$(pwd):$PATH

# Verify ffmpeg is available
./ffmpeg -version

# Set environment variable for librosa
export LIBROSA_BACKEND=soundfile
