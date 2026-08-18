@echo off
IF NOT EXIST "build" mkdir build

echo [0/5] Compiling Windows Icon Resource...
where windres >nul 2>nul
if %errorlevel% equ 0 (
    windres -I resources -i resources/app.rc -O coff -o rsrc_windows_amd64.syso
)

echo [1/5] Building Windows x64 GUI Executable...
set GOOS=windows
set GOARCH=amd64
go build -ldflags "-H=windowsgui" -o build/RapidMessageSender_Windows_amd64.exe .
if exist build\RapidMessageSender_Windows_amd64.exe copy /Y build\RapidMessageSender_Windows_amd64.exe RapidMessageSender_Go.exe >nul

echo [2/5] Building Windows ARM64 GUI Executable...
set GOOS=windows
set GOARCH=arm64
go build -ldflags "-H=windowsgui" -o build/RapidMessageSender_Windows_arm64.exe .

echo [3/5] Building Linux x64 Executable...
set GOOS=linux
set GOARCH=amd64
go build -o build/RapidMessageSender_Linux_amd64 .

echo [4/5] Building macOS Intel x64 Executable...
set GOOS=darwin
set GOARCH=amd64
go build -o build/RapidMessageSender_macOS_amd64 .

echo [5/5] Building macOS Apple Silicon ARM64 Executable...
set GOOS=darwin
set GOARCH=arm64
go build -o build/RapidMessageSender_macOS_arm64 .

set GOOS=windows
set GOARCH=amd64
dir build
pause
