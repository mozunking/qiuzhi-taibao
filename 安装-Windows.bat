@echo off
chcp 65001 >nul 2>nul
setlocal
cd /d "%~dp0"
echo ============================================
echo   JobDesk (qiuzhi-taibao) Installer
echo   target: Qoder  ( ^~/.qoder  or  ^~/.qoder-cn )
echo ============================================
echo.

set PY=
where python >nul 2>nul && set PY=python
if "%PY%"=="" (where py >nul 2>nul && set PY=py)
if "%PY%"=="" (
  echo [ERROR] Python not found.
  echo         Install Python 3.8+ from https://www.python.org/downloads/
  echo         Remember to check "Add python.exe to PATH".
  echo.
  pause
  exit /b 1
)

echo Using %PY%
%PY% --version
echo.
%PY% scripts\install.py %*
echo.
if errorlevel 1 (
  echo [FAILED] see messages above.
) else (
  echo [DONE] Now RESTART Qoder, then type / in the chat box.
)
echo.
pause
