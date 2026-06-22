#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "📥 Installing ffmpeg via system package..."
apt-get update -qq && apt-get install -y -qq ffmpeg

echo "✅ Build completed."
