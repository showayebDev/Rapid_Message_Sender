# ⚡ Rapid Message Sender

A modern, high-speed desktop automation tool built with **Python**, **PySide6**, **PyAutoGUI**, and **Pyperclip**.

Designed for ultra-fast, reliable message sending across messaging platforms (WhatsApp, Discord, Telegram, Messenger, Web Chat, etc.) using **clipboard copy & paste** instead of slow character-by-character typing.

---

## ✨ Features

- 💬 **Multi-line Message Template**: Type or paste any single/multi-line message or choose from preset templates.
- 🔢 **Customizable Repeat Count**: Send from 1 to 100,000+ messages seamlessly.
- ⏱️ **Fast Interval Control**: Set wait time between messages (default **100 ms**).
- 🔢 **Counter Suffix/Prefix**: Optional check box to append counters to messages (`message 1`, `message 2`, etc.).
- ⏳ **Start Countdown Delay**: Configurable start delay (default **5 seconds**) giving you time to switch focus to your target chat box.
- 🛑 **Emergency Stop (Ctrl + Q)**: Press **`Ctrl + Q`** anytime from *any window* to instantly abort the message sending process.
- 🚀 **Clipboard Paste Engine**: Uses PyAutoGUI `Ctrl + V` for ultra-fast pasting with full unicode & emoji support.
- 🎨 **Modern Dark UI**: Sleek PySide6 user interface with live stats dashboard, progress bar, and real-time activity logs.
- 📋 **Auto-Restore Clipboard**: Automatically restores your original clipboard text after automation completes.

---

## 🚀 How to Run with `uv`

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run Application
```bash
uv run rapid-message-sender
```

Or run directly with Python:
```bash
uv run python -m rapid_message_sender.main
```

---

## 📦 How to Build `.exe` Executable

You can compile the application into a standalone Windows executable (`.exe`) using **PyInstaller** and `main.spec` via `uv`:

### Step 1: Add PyInstaller Dependency (if not already added)
```bash
uv add --dev pyinstaller
```

### Step 2: Build Executable with `main.spec`
```bash
uv run pyinstaller main.spec --noconfirm
```

### Step 3: Run the Built Executable
Your compiled standalone `.exe` will be saved in the `dist/` directory:
```bash
.\dist\RapidMessageSender.exe
```

---

## 🎮 How to Use

1. Enter your **Message** in the text area (or select a preset template).
2. Set **How many times send** (e.g., `10`).
3. Adjust **Wait between each message** in milliseconds (default `100 ms`).
4. Toggle **Show counter after the message** if you want `Message 1`, `Message 2` format.
5. Set **Start countdown delay** (default `5 seconds`).
6. Click **`🚀 Start Sending`**.
7. Switch immediately to your target application (WhatsApp, Messenger, Discord, Telegram, Notepad, etc.) and click inside the text input box.
8. The app will count down and start rapidly sending messages!
9. Press **`Ctrl + Q`** at any moment to emergency stop!
