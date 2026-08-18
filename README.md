# ⚡ Rapid Message Sender (Multi-OS Edition)

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
- 📦 **1-Click Multi-OS Cross-Compilation**: Build scripts for all platforms — `build_cross_platform.bat` (Windows) and `build_cross_platform.sh` (macOS / Linux) — compile executables for Windows, Linux, and macOS.

---

## 🛠️ Build & Execution Instructions

### 1. Build All Cross-Platform Binaries

**Windows** — run the batch script:
```cmd
build_cross_platform.bat
```

**macOS / Linux** — run the shell script:
```bash
chmod +x build_cross_platform.sh
./build_cross_platform.sh
```

Output binaries in `build/`:
| File | Platform |
|------|----------|
| `RapidMessageSender_Windows_amd64.exe` | Windows x64 GUI |
| `RapidMessageSender_Windows_arm64.exe` | Windows ARM64 GUI |
| `RapidMessageSender_Linux_amd64` | Linux x64 |
| `RapidMessageSender_macOS_amd64` | macOS Intel x64 |
| `RapidMessageSender_macOS_arm64` | macOS Apple Silicon ARM64 |

> **Note**: The Windows icon resource (`windres`) step is Windows-only and is skipped automatically on macOS/Linux.

### 2. Build for Your Own System Only
To build a single binary for your **current OS and architecture** (no cross-compilation):
```bash
go build -o build/RapidMessageSender .
```
On Windows, add `-ldflags "-H=windowsgui"` to suppress the console window:
```cmd
go build -ldflags "-H=windowsgui" -o build/RapidMessageSender.exe .
```

### 3. Run Directly from Source
```bash
go run main.go
```

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Serves embedded `frontend/index.html` with dynamic `{{VERSION}}` template replacement |
| `/api/version` | `GET` | Returns `{"version": "v*.*.*"}` |
| `/api/start` | `POST` | Initiates automation worker loop with specified configuration JSON |
| `/api/stop` | `POST` | Triggers instant worker abort |
| `/api/events` | `GET` | Server-Sent Events (SSE) log and live stats stream |
| `/api/heartbeat` | `POST` | Frontend window pulse (auto-shuts backend if disconnected) |
| `/api/shutdown` | `POST` | Triggers clean backend process termination |
| `/api/update` | `GET` | Asynchronously checks GitHub REST API for release updates |

---

## 📜 License & Author

- **Author**: Showayeb
- **License**: MIT License
