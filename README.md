# ⚡ Rapid Message Sender

A modern, high-speed desktop automation application built with **Python**, **PySide6**, **PyAutoGUI**, **Pyperclip**, and **pynput**.

Designed for ultra-fast, reliable message dispatch across messaging platforms (WhatsApp, Discord, Telegram, Messenger, Web Chat, Notepad, etc.) supporting both **Direct Character Typing (Hardware Keyboard Simulation)** and **Clipboard Copy & Paste**.

---

## ✨ Key Features

- 💬 **Multi-line Text & Presets**: Type/paste multi-line text or select built-in template presets.
- ⌨️ **Dual Input Engines**:
  - **Direct Character Typing**: Simulates hardware keyboard keystrokes directly into active text boxes without touching system clipboard memory.
  - **Clipboard Copy & Paste**: Ultra-fast `Ctrl+V` pasting with strict read-back verification and Win32 fallback.
- 🔄 **GitHub Release Auto-Updater**: Asynchronously checks `showayebDev/Rapid_Message_Sender` for new GitHub Releases, prompts user with changelogs, downloads latest binary, replaces old EXE, and deletes old files automatically upon restart.
- 🔢 **Customizable Repeat Count**: Dispatch anywhere from 1 to 100,000+ messages seamlessly.
- ⏱️ **Zero Dropped Messages**: Built-in 5ms buffer flush & 12ms target render sync micro-pauses ensure every message (1, 2, 3...) is delivered sequentially.
- 🔢 **Counter Suffix & Prefix**: Add customizable message numbering (`Message 1`, `Message 2`...) with custom separators (`Space`, `Semicolon`, `Dash`, `Hash`).
- ⏳ **Countdown Start Delay**: Configurable delay (default **5 seconds**) giving you time to switch focus to your target text box.
- 🛑 **Dual Emergency Abort**: Press **`Ctrl + Q`** globally from *any active window* or flick your mouse to the top-left screen corner (PyAutoGUI Fail-Safe) to abort instantly.
- 🔒 **Mouse Scroll Lock**: Input fields (`QSpinBox` & `QComboBox`) ignore hover mouse-wheel scrolling so you can scroll the settings page without changing values.
- 📖 **Built-in Documentation Page**: Includes an interactive **User Guide** page built directly into the UI.
- 🔄 **Reset All Button**: Restore all defaults, reset progress bars, clear logs, and wipe clipboard memory with a single click.
- 🧹 **Automatic Clipboard Security**: Wipes automated clipboard memory using Windows Win32 API when finished or stopped.
- 🎨 **Modern Dark Theme**: Dark slate UI design with live stats dashboard, progress bar, real-time activity logs, and vector checkmark (✔️) indicators.
- 🖼️ **Asset & Icon Suite**: Multi-resolution `app_icon.png`, Windows native `app_icon.ico`, and `512x512` square thumbnail.

---

## 🚀 Getting Started with `uv`

### 1. Install Project Dependencies
```bash
uv sync
```

### 2. Launch Application
```bash
uv run rapid-message-sender
```

Or execute directly via Python module:
```bash
uv run python -m rapid_message_sender.main
```

### 3. Rebuild UI & Icon Assets
Re-generate all vector icons, checkmarks, up/down arrows, `.png`, and `.ico` assets anytime:
```bash
uv run build-assets
```

---

## 📦 Building Standalone `.exe` Executable

You can compile the application into a single standalone Windows `.exe` using **PyInstaller** and [`main.spec`](file:///c:/Users/Showayeb/Desktop/Rapid_Message_Sender/main.spec):

### Step 1: Install PyInstaller (Dev Group)
```bash
uv add --dev pyinstaller
```

### Step 2: Build Executable
```bash
uv run pyinstaller main.spec --noconfirm
```

### Step 3: Run Executable
Your compiled executable will be output to the `dist/` directory:
```bash
.\dist\RapidMessageSender.exe
```

---

## 🎮 Step-by-Step Usage Guide

1. **Enter Message**: Type your message in the text editor or select a template from the preset dropdown.
2. **Select Input Method**: Choose **⌨️ Direct Character Typing** (recommended) or **⚡ Clipboard Copy & Paste**.
3. **Configure Count & Delay**: Set **How many times send** (e.g. `10`), **Wait between each message** (default `100 ms`), and **Start countdown delay** (default `5 sec`).
4. **Set Counter Options**: Check **Show counter after message** if you want automated numbering (`Message 1`, `Message 2`...). Select your separator and position.
5. **Trigger Key**: Choose your send key (`Enter`, `Ctrl + Enter`, `Shift + Enter`, or `None`).
6. **Start Automation**: Click **`🚀 Start Sending`**.
7. **Focus Target Window**: During the 5-second countdown, switch focus immediately to your target chat box (WhatsApp, Telegram, Discord, Messenger, Notepad, etc.).
8. **Check Updates**: Click **`🔄 Check Updates`** at any time to query GitHub Releases for new updates.
9. **Emergency Stop**: Press **`Ctrl + Q`** from any active window to halt the process at any time!

---

## ⌨️ Shortcuts & Hotkey Reference

| Hotkey / Trigger | Action | Scope |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | **Emergency Stop** (Instantly aborts message dispatch) | **Global** (Works from any active app/window) |
| **Top-Left Screen Corner `(0,0)`** | **PyAutoGUI Hardware Fail-Safe** (Aborts automation instantly) | **System Mouse** |
| **`Enter`** | Standard message send trigger key after typing/pasting | Target Text Box |
| **`Ctrl + Enter`** | Alternative send trigger (ideal for Slack / Discord multi-line modes) | Target Text Box |
| **`Shift + Enter`** | Insert newline without triggering instant send | Target Text Box |
| **`None`** | Type or paste message into input field without pressing any trigger key | Target Text Box |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
