@echo off
echo Starting NJ IDE Copier Server...
echo.
python -m src.server.main
if %errorlevel% neq 0 (
    echo.
    echo Server exited with error code %errorlevel%
)
echo.
echo Server stopped. Press any key to exit.
pause >nul
