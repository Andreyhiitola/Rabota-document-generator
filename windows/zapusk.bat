@echo off
title Generate Act
echo.
echo Starting script...
python generate_act.py --data "data.xlsx" --template "template.xlsx"
echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! New act created.
) else (
    echo ERROR! Check data.xlsx and template.xlsx files.
)
echo.
echo Press any key to exit...
pause >nul
