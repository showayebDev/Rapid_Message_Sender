@echo off
setlocal enabledelayedexpansion

echo =========================================================================
echo   ⚡ Rapid Message Sender - Automated C++ (Qt 6 + CMake) Build Script
echo =========================================================================
echo.

if not exist build (
    echo [INFO] Creating build directory...
    mkdir build
)

cd build

echo [INFO] Running CMake configuration...
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] CMake configuration failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [INFO] Compiling C++ executable...
cmake --build . --config Release
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =========================================================================
echo   Compilation Successful! Deploying Qt 6 Runtime DLLs...
echo =========================================================================

where windeployqt6 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    windeployqt6 RapidMessageSender.exe
) else (
    where windeployqt >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        windeployqt RapidMessageSender.exe
    ) else (
        echo [WARNING] windeployqt tool not found in PATH.
    )
)

echo.
echo =========================================================================
echo   [SUCCESS] Build completed!
echo   Executable location: build\RapidMessageSender.exe
echo =========================================================================
echo.
pause
