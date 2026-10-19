@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   Website Safety Checker - Android APK Builder
echo =======================================================
echo.

where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Flutter was not found on your system PATH.
    echo.
    echo To install Flutter automatically on Windows:
    echo   1. Run in PowerShell (Admin):
    echo        winget install Google.Flutter
    echo.
    echo   2. Alternatively, download Flutter SDK from:
    echo        https://docs.flutter.dev/get-started/install/windows/mobile
    echo.
    echo Once installed and added to PATH, re-run this script to build the APK!
    echo.
    echo (Tip: You can also push to GitHub and GitHub Actions will build
    echo  the APK for you in ~3 minutes using .github/workflows/build-apk.yml)
    echo.
    pause
    exit /b 1
)

echo [*] Flutter found! Checking dependencies...
cd /d "%~dp0mobile"

echo [*] Running flutter pub get...
call flutter pub get
if %errorlevel% neq 0 (
    echo [!] Failed to fetch packages.
    pause
    exit /b 1
)

echo [*] Building Android Release APK...
call flutter build apk --release
if %errorlevel% neq 0 (
    echo [!] Build failed. Please check Flutter and Android SDK setup.
    pause
    exit /b 1
)

set "APK_PATH=%~dp0mobile\build\app\outputs\flutter-apk\app-release.apk"
echo.
echo =======================================================
echo [SUCCESS] APK built successfully!
echo APK Location:
echo   %APK_PATH%
echo =======================================================
echo.

rem Open the folder with the APK highlighted
explorer /select,"%APK_PATH%"

pause
