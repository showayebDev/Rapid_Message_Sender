# 🛠️ Setup & Compilation Guide - Rapid Message Sender

This guide provides step-by-step instructions for configuring the development environment, compiling the C++ binary using CMake and Qt 6, and packaging the standalone executable on Windows.

---

## 📋 Prerequisites

To build **Rapid Message Sender**, ensure you have the following tools installed on your Windows machine:

1. **CMake** (version 3.16 or higher)
   - Download from: [cmake.org](https://cmake.org/download/)
2. **C++ Compiler** (supporting C++17)
   - **MSYS2 MinGW64** (`g++` / `gcc` 10+): Install via `pacman -S mingw-w64-x86_64-toolchain`
   - **OR Visual Studio 2019/2022** (MSVC C++ Desktop Development workload)
3. **Qt 6 Framework** (`Qt6Widgets`, `Qt6Network`, `Qt6Core`)
   - **Via MSYS2**: `pacman -S mingw-w64-x86_64-qt6-base mingw-w64-x86_64-qt6-tools`
   - **OR Official Qt Installer**: Select Qt 6.x.x for MSVC/MinGW
4. **Ninja Build Tool** (Optional but recommended for fast parallel builds)
   - Install via MSYS2: `pacman -S mingw-w64-x86_64-ninja` or via `pip install ninja`

---

## 🔧 Building via Command Line (MSYS2 / MinGW)

1. Open **MSYS2 MinGW64 Terminal** or **PowerShell** with GCC in PATH.
2. Navigate to project root directory:
   ```powershell
   cd C:\path\to\Rapid_Message_Sender
   ```
3. Create build directory and run CMake configuration:
   ```bash
   mkdir build
   cd build
   cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release
   ```
4. Compile executable:
   ```bash
   cmake --build .
   ```
5. Deploy Qt runtime DLLs for standalone execution:
   ```bash
   windeployqt6 RapidMessageSender.exe
   ```

---

## 💻 Building via Visual Studio (MSVC)

1. Launch **Developer Command Prompt for VS 2022**.
2. Navigate to project directory:
   ```cmd
   cd C:\path\to\Rapid_Message_Sender
   ```
3. Run CMake configuration specifying Qt 6 prefix path:
   ```cmd
   mkdir build
   cd build
   cmake .. -DCMAKE_PREFIX_PATH="C:/Qt/6.x.x/msvc2019_64"
   cmake --build . --config Release
   ```
4. Deploy Qt runtime libraries:
   ```cmd
   windeployqt6 --release RapidMessageSender.exe
   ```

---

## 🎨 Visual Layout Editing (Qt Designer)

You can visually open and modify the UI layout (`resources/mainwindow.ui`) using Qt Designer:

```bash
# Using uv (Python PySide6 Designer)
uv run pyside6-designer resources/mainwindow.ui

# OR using native Qt Creator / Qt Designer
designer resources/mainwindow.ui
```

---

## 📦 Run Standalone Executable

Once compiled and deployed, launch the executable directly:
```powershell
build\RapidMessageSender.exe
```
