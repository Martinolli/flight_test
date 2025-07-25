@echo off
echo Running Advanced Statistical Analysis...
echo.

REM Change to project directory
cd /d "c:\Users\joao.bosco\OneDrive\Documentos\vscode_01\flight_test_data"

REM Run the advanced analysis
"C:/Users/joao.bosco/OneDrive/Documentos/vscode_01/flight_test_data/.venv/Scripts/python.exe" advanced_analysis.py

echo.
echo Advanced analysis complete! Check the plots/ folder for statistical plots.
echo.
pause
