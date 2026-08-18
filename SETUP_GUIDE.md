# ⚡ Rapid Message Sender (v1.3.0) - Setup & User Guide

Welcome to **Rapid Message Sender (v1.3.0)**! This detailed guide covers installation, environment setup, cross-platform compilation, operational usage, and safety controls.

---

## 📋 System Requirements & Dependencies

### Operating Systems
- **Windows**: Windows 10 / 11 (x64)
- **Linux**: Ubuntu / Debian / Fedora / Arch (x64)
- **macOS**: macOS 11.0+ (Intel & Apple Silicon)

### Dependencies
- **Go (Golang 1.20+)**: Required only if building or running from source code.
- **Web Browser**: Microsoft Edge or Google Chrome installed (used for App Mode GUI rendering).
- **Linux Tools (Linux build only)**: `xclip` and `xdotool` (`sudo apt install xclip xdotool`).

---

## ⚡ Quick Start Guide

### 1. Launching Pre-Built Executables
1. Navigate to `build/` directory (or workspace root).
2. Double-click `RapidMessageSender_Windows_amd64.exe` (or `RapidMessageSender_Go.exe`).
3. The app automatically binds an embedded HTTP server to a free dynamic port (`127.0.0.1:0`) and opens the native UI window in MS Edge App Mode.

### 2. Running from Source
Open terminal in the project root:
```bash
go run main.go
```

---

## 📖 Step-by-Step Usage Guide

1. **Select or Enter Message**:
   - Choose a preset template from the dropdown ("⚡ Rapid Ping Alert", "🔢 Counting Sequence Test", "🔥 Emoji Blast Alert", etc.), or type custom text into the **Message Content** box.
2. **Configure Parameters**:
   - **Repeat Count**: Number of times to send the message (default `10`).
   - **Interval (ms)**: Delay between messages (hard-locked to a minimum **200 ms** safety floor).
   - **Start Delay (s)**: Countdown timer (default `2` seconds) allowing you to switch focus to your target app window.
3. **Optional Counter Options**:
   - Check **Append Automated Counter**.
   - Select **Suffix (End)** or **Prefix (Start)**.
   - Choose a separator (`Space (" ")`, `Hash ("#")`, `Underscore ("_")`, `Hyphen ("-")`, `Colon (":")`).
4. **Trigger Key Selection**:
   - Select what key to send after pasting: `Enter Key (Default)`, `Ctrl + Enter`, `Shift + Enter`, or `None`.
5. **Start Dispatch**:
   - Click **🚀 Start Sending**.
   - Immediately switch focus to your target message input area (Discord, Telegram, WhatsApp Web, Slack, Notepad, etc.).
   - Observe the live dispatch progress, speed (`msg/s`), and timestamped logs on the dashboard.

---

## 🛡️ Emergency Abort & Safety Controls

Rapid Message Sender includes multiple fail-safe mechanisms to protect your system and accounts:

1. **Global Hotkey `Ctrl + Q`**:
   Pressing <kbd>Ctrl</kbd> + <kbd>Q</kbd> anywhere on your computer immediately stops the dispatch sequence from any window.
2. **Hardware Mouse Screen Corner `(0,0)` Fail-Safe**:
   Flicking your mouse pointer into the extreme top-left corner pixel of your screen `(0,0)` halts message dispatch instantly.
3. **200 ms Safety Floor**:
   Minimum message interval is locked to 200 ms to prevent chat rate-limiting and platform bans.
4. **Automated Window Close Shutdown**:
   Closing the application GUI window triggers an immediate shutdown beacon and background heartbeat monitor that terminates the backend Go process cleanly.

---

## 🔨 Building Cross-Platform Binaries

Run `build_cross_platform.bat` to compile all 4 desktop executables into `build/`:
```cmd
build_cross_platform.bat
```

### Generated Executables:
- `build/RapidMessageSender_Windows_amd64.exe` (Windows x64 GUI, console window suppressed via `-ldflags "-H=windowsgui"`)
- `build/RapidMessageSender_Windows_arm64.exe` (Windows ARM64 GUI, console window suppressed via `-ldflags "-H=windowsgui"`)
- `build/RapidMessageSender_Linux_amd64` (Linux x64 binary)
- `build/RapidMessageSender_macOS_amd64` (macOS Intel x64 binary)
- `build/RapidMessageSender_macOS_arm64` (macOS Apple Silicon ARM64 binary)

---

## 🔍 Troubleshooting & FAQs

- **Q: Edge/Chrome window doesn't open?**
  - Ensure Microsoft Edge or Google Chrome is installed. The backend will fall back to opening your default web browser if App Mode isn't found.
- **Q: Messages aren't pasting into the chat box?**
  - Make sure you focus the target input box during the **Start Delay** countdown (default 2 seconds).
- **Q: How do I stop an ongoing rapid dispatch sequence?**
  - Press <kbd>Ctrl</kbd> + <kbd>Q</kbd> globally or move your mouse to the top-left corner of your main screen `(0,0)`.
