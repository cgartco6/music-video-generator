@echo off
echo ========================================
echo   Music Video Generator Setup (Windows)
echo ========================================

echo Installing dependencies...
call npm install

echo Starting the app...
echo.
echo Open your browser and go to: http://localhost:3000
echo.

node backend/server.js
pause
