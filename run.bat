@echo off
REM =====================================================================
REM OCR CODE HUNTER v2.0 - BATCH RUNNER
REM =====================================================================
REM Purpose: Khởi động OCR bot với virtual environment
REM Requirements: Python 3.8+, venv_optimized
REM =====================================================================

setlocal enabledelayedexpansion

title OCR Code Hunter v2.0
color 0A
chcp 65001 >nul

REM =====================================================================
REM CONSTANTS
REM =====================================================================
set VENV_PATH=venv_optimized
set VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat
set MAIN_SCRIPT=main_fast.py
set LOG_FILE=logs\ocr_bee.log

REM =====================================================================
REM BANNER
REM =====================================================================
echo.
echo ========================================================
echo        DANG KHOI DONG HE THONG OCR BOT v2.0
echo ========================================================
echo.

REM =====================================================================
REM STEP 1: CHECK & ACTIVATE VIRTUAL ENVIRONMENT
REM =====================================================================
echo [STEP 1/4] Kiem tra moi truong ao...
echo.

if not exist "%VENV_ACTIVATE%" (
    echo [ERROR] Khong tim thay: %VENV_ACTIVATE%
    echo.
    echo === GIAI PHAP ===
    echo Chay cac lenh sau trong terminal:
    echo.
    echo   python -m venv %VENV_PATH%
    echo   %VENV_ACTIVATE%
    echo   pip install -r requirements.txt
    echo.
    echo Sau do chay lai: run.bat
    echo.
    pause
    exit /b 1
)

call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo [ERROR] Khong the kich hoat virtual environment!
    pause
    exit /b 1
)
echo [OK] Da kich hoat venv: %VENV_PATH%
echo.

REM =====================================================================
REM STEP 2: CHECK PYTHON VERSION
REM =====================================================================
echo [STEP 2/4] Kiem tra Python...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong co san hoac khong trong PATH!
    echo Vui long cai dat Python 3.8+ tu python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] Python version: %PYTHON_VER%
echo.

REM =====================================================================
REM STEP 3: CHECK DEPENDENCIES
REM =====================================================================
echo [STEP 3/4] Kiem tra dependencies...
echo.

python -c "import cv2, paddleocr, mss, keyboard, pyperclip" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Cac dependency chua duoc cai dat!
    echo.
    echo Dang cai dat... (Luc dau co the mat 1-2 phut)
    echo.
    call pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Khong the cai dat dependencies!
        echo Vui long kiem tra internet connection.
        echo.
        pause
        exit /b 1
    )
)
echo [OK] All dependencies OK
echo.

REM =====================================================================
REM STEP 4: RUN MAIN SCRIPT
REM =====================================================================
echo [STEP 4/4] Dang chay OCR Bot...
echo.
echo ========================================================
echo        BOT DANG CHAY
echo ========================================================
echo.
echo HOTKEY:
echo   [F8]  = Bat dau / Tam dung OCR
echo   [F9]  = Chon vung OCR lai
echo   [ESC] = Thoat
echo.
echo Nhat ky: %LOG_FILE%
echo.
echo ========================================================
echo.

cd /d "%~dp0"
python "%MAIN_SCRIPT%"

REM =====================================================================
REM CLEANUP & EXIT
REM =====================================================================
echo.
echo ========================================================
echo        BOT DA DUNG
echo ========================================================
echo.

if exist "%LOG_FILE%" (
    echo Nhat ky: %LOG_FILE%
    echo.
)

echo Nhan phim bat ky de thoat...
pause
exit /b 0