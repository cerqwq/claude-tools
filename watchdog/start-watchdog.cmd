@echo off
title Claude Watchdog
echo Starting Claude Code Watchdog...
echo Close this window or create DISABLE_WATCHDOG to stop.
echo.
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0claude-watchdog.ps1"
