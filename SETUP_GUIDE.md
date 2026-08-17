# 🛠️ Setup & Compilation Guide - Rapid Message Sender

This guide provides step-by-step instructions for configuring the C++ development environment, compiling the native binary using CMake and Qt 6, embedding Windows manifests & resources, code signing, and packaging the standalone executable on Windows.

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
4. **Ninja Build Tool** (Recommended for fast parallel compilation)
   - Install via MSYS2: `pacman -S mingw-w64-x86_64-ninja` or via `pip install ninja`

---

## 🚀 Automated 1-Click Build & Deploy (`build.bat`)

The fastest way to build and sign the project is running `build.bat` from the project root:

```cmd
build.bat
```

### What `build.bat` does automatically:
1. Creates the `build/` directory if missing.
2. Configures CMake with Ninja generator in Release mode (`-DCMAKE_BUILD_TYPE=Release`).
3. Compiles all C++ source files, Qt MOC/UIC files, and Windows resource scripts (`version.rc`).
4. Deploys required Qt 6 runtime DLLs (`Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Widgets.dll`, `Qt6Network.dll`, plugins) via `windeployqt6`.

---

## 🔧 Building via Command Line (MSYS2 / MinGW)

1. Open **MSYS2 MinGW64 Terminal** or **PowerShell** with GCC/CMake in PATH.
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
5. Deploy Qt 6 runtime libraries:
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

## 🛡️ Windows Manifest & Embedded Resources

### 1. Embedded Application Manifest (`resources/app.manifest`)
Contains Windows execution privileges (`asInvoker`), Windows 10 & 11 compatibility GUIDs, and PerMonitorV2 high-DPI scaling configuration.

### 2. Embedded Resource Script (`resources/version.rc`)
Embeds application icon (`app_icon.ico`), company details (`ShowayebDev`), product name, file description, copyright, and version info directly into the binary PE header.

---

## 🔢 Version Management

Application version is centrally controlled in [`CMakeLists.txt`](file:///c:/Users/Showayeb/Desktop/Rapid_Message_Sender/CMakeLists.txt):

```cmake
set(APP_VERSION_MAJOR 0)
set(APP_VERSION_MINOR 2)
set(APP_VERSION_PATCH 0)
set(APP_VERSION_STRING "${APP_VERSION_MAJOR}.${APP_VERSION_MINOR}.${APP_VERSION_PATCH}")
```

Updating these values automatically injects `APP_VERSION_STRING` into C++ compilation, UI title bar, Windows resource properties, and the GitHub release auto-updater.

---

## 📦 Run Standalone Executable

Launch the compiled executable directly from the `build` directory:
```powershell
build\RapidMessageSender.exe
```
