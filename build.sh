#!/bin/bash
set -e

echo "📦 Installing Python dependencies (minimal set)..."
pip install --no-cache-dir -r requirements.txt

echo "📥 Downloading static ffmpeg..."
wget -q -O ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg.tar.xz
mv ffmpeg-*-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg
export PATH=$(pwd):$PATH

echo "✅ ffmpeg version:"
./ffmpeg -version

echo "🚀 Build finished successfully."
