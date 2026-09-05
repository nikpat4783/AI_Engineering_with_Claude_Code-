@echo off
REM ALOCA+ QA System - Cleanup Script (Windows)
REM Removes build artifacts, logs, and temporary files

echo.
echo ====================================
echo   ALOCA+ QA System Cleanup
echo ====================================
echo.

setlocal enabledelayedexpansion
set "cleaned=0"

REM Clean dist and build directories
if exist "dist" (
    echo Removing dist directory...
    rmdir /s /q dist 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned dist directory
)

if exist "frontend\build" (
    echo Removing frontend build directory...
    rmdir /s /q frontend\build 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned frontend build directory
)

if exist "frontend\.cache" (
    echo Removing frontend cache...
    rmdir /s /q frontend\.cache 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned frontend cache
)

REM Clean log files
if exist "backend\*.log" (
    echo Removing backend logs...
    del /q backend\*.log 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned backend logs
)

if exist "frontend\*.log" (
    echo Removing frontend logs...
    del /q frontend\*.log 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned frontend logs
)

REM Clean Python cache
if exist "backend\__pycache__" (
    echo Removing Python cache...
    rmdir /s /q backend\__pycache__ 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned Python cache
)

if exist "backend\.pytest_cache" (
    echo Removing pytest cache...
    rmdir /s /q backend\.pytest_cache 2>nul
    set /a cleaned+=1
    echo [OK] Cleaned pytest cache
)

echo.
echo ====================================
echo   Cleanup Completed!
echo ====================================
echo.
echo Cleaned: !cleaned! item(s)
echo.
pause
