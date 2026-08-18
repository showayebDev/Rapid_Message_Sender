#!/usr/bin/env bash
set -e

mkdir -p build

echo "[0/5] Skipping Windows Icon Resource (windres not applicable on this platform)..."

echo "[1/5] Building Windows x64 GUI Executable..."
GOOS=windows GOARCH=amd64 go build -ldflags "-H=windowsgui" -o build/RapidMessageSender_Windows_amd64.exe .

echo "[2/5] Building Windows ARM64 GUI Executable..."
GOOS=windows GOARCH=arm64 go build -ldflags "-H=windowsgui" -o build/RapidMessageSender_Windows_arm64.exe .

echo "[3/5] Building Linux x64 Executable..."
GOOS=linux GOARCH=amd64 go build -o build/RapidMessageSender_Linux_amd64 .

echo "[4/5] Building macOS Intel x64 Executable..."
GOOS=darwin GOARCH=amd64 go build -o build/RapidMessageSender_macOS_amd64 .

echo "[5/5] Building macOS Apple Silicon ARM64 Executable..."
GOOS=darwin GOARCH=arm64 go build -o build/RapidMessageSender_macOS_arm64 .

echo ""
echo "Build complete. Output files:"
ls -lh build/
