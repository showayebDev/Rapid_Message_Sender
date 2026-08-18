# ⚡ Rapid Message Sender (v1.3.0 - Multi-OS Edition)

A high-performance, modern cross-platform desktop automation application built with **Go (Golang 1.20+)** and an embedded dynamic **HTML5/CSS3/JS Web UI** running in Microsoft Edge / Google Chrome App Mode.

Designed for ultra-fast, reliable message dispatch across desktop applications and web messaging platforms (Discord, Telegram, WhatsApp Web, Slack, Messenger, Web Chat, Notepad, etc.).

---

## 🌟 Key Features

- 🚀 **Cross-Platform Go Engine**: Zero CGO external dependencies. Compiled native binaries for Windows (`.exe` with console window suppressed), Linux, and macOS (Intel & Apple Silicon).
- 🎨 **Modern Dark Slate Web UI**: Embedded web interface using HTML5, Vanilla CSS3 (Modern Dark Slate theme with Inter & JetBrains Mono fonts), and ES6+ JavaScript.
- 💬 **Multi-line Text & Presets**: Select built-in template presets or type custom multi-line messages with emoji support (`⚡🚀🔥`).
- ⚡ **High-Speed Clipboard Copy & Paste Engine**: Native OS clipboard dispatch (`Win32 OpenClipboard` / `xclip` / `pbcopy`) with `Ctrl+V` pasting and memory read-back verification.
- ⏱️ **200 ms Safety Floor**: Hard-locked minimum interval floor to prevent chat rate-limiting across platforms.
- 🔢 **Automated Counter Suffix & Prefix**: Append message numbering (`1 Message`, `Message # 1`, etc.) with customizable separators (` `, `#`, `_`, `-`, `:`).
- ⏳ **Countdown Start Delay**: Configurable start delay giving you time to switch focus to your target input field.
- 🛡️ **Emergency Abort Controls**:
  - **Global Hotkey `Ctrl+Q`**: Registered via Win32 `RegisterHotKey` on a locked OS thread (`runtime.LockOSThread()`) to instantly abort from any active desktop application.
  - **Hardware Mouse Corner `(0,0)` Fail-Safe**: Instantly halts dispatch if mouse cursor touches top-left screen pixel `(0,0)`.
- 🔄 **Real-Time Activity Log & Stats**: Real-time log streaming over Server-Sent Events (SSE `/api/events`) with timestamped level badges (`INFO`, `SUCCESS`, `WARNING`, `ERROR`).
- ⚡ **Auto-Shutdown on Window Close**: Automatically terminates the backend Go process when the application desktop window is closed via heartbeat monitoring and unload beacons.
- 📦 **1-Click Multi-OS Cross-Compilation**: Batch compilation script `build_cross_platform.bat` builds executables for Windows, Linux, and macOS.

---

## 📂 Repository Directory Structure

```
.
├── main.go                       # App entry point, embedded FS, dynamic port server & desktop launcher
├── go.mod                        # Go module declaration (rapid-message-sender, go 1.20)
├── build_cross_platform.bat      # 1-click batch script compiling Windows, Linux, & macOS binaries
├── pkg/
│   ├── version/
│   │   └── version.go            # Single source of truth version file (AppVersion = "v1.3.0")
│   ├── automation/
│   │   ├── automation.go         # Unified Driver interface definition & registry
│   │   ├── input_windows.go      # Win32 SendInput, Clipboard, RegisterHotKey (Ctrl+Q), GetCursorPos
│   │   ├── input_linux.go        # Linux X11 / xclip / xdotool driver
│   │   └── input_darwin.go       # macOS CoreGraphics / pbcopy / osascript driver
│   ├── engine/
│   │   └── worker.go             # Automation loop thread, countdown, rate calculations, & abort checks
│   ├── net/
│   │   └── updater.go            # Async GitHub REST API release checker
│   └── api/
│       └── server.go             # HTTP router, dynamic template injector, SSE stream & heartbeat
└── frontend/
    ├── index.html                # Responsive dark UI layout with {{VERSION}} placeholders
    ├── style.css                 # Dark Slate CSS theme, fixed 320px console terminal with scrollbars
    └── app.js                    # Dynamic version fetcher, EventSource listener, & UI manager
```

---

## 🛠️ Build & Execution Instructions

### 1. Build All Cross-Platform Binaries
Run the included batch script:
```cmd
build_cross_platform.bat
```
Output binaries in `build/`:
- `RapidMessageSender_Windows_amd64.exe` (Windows x64 GUI)
- `RapidMessageSender_Windows_arm64.exe` (Windows ARM64 GUI)
- `RapidMessageSender_Linux_amd64` (Linux x64)
- `RapidMessageSender_macOS_amd64` (macOS Intel x64)
- `RapidMessageSender_macOS_arm64` (macOS Apple Silicon ARM64)

### 2. Run Directly from Source
```bash
go run main.go
```

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Serves embedded `frontend/index.html` with dynamic `{{VERSION}}` template replacement |
| `/api/version` | `GET` | Returns `{"version": "v1.3.0"}` |
| `/api/start` | `POST` | Initiates automation worker loop with specified configuration JSON |
| `/api/stop` | `POST` | Triggers instant worker abort |
| `/api/events` | `GET` | Server-Sent Events (SSE) log and live stats stream |
| `/api/heartbeat` | `POST` | Frontend window pulse (auto-shuts backend if disconnected) |
| `/api/shutdown` | `POST` | Triggers clean backend process termination |
| `/api/update` | `GET` | Asynchronously checks GitHub REST API for release updates |

---

## 📜 License & Author

- **Author**: Showayeb
- **Version**: `v1.3.0`
- **License**: MIT License
