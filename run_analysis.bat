@echo off
echo Running Flight Test Data Analysis...
echo.

REM Change to project directory
cd /d "c:\Users\joao.bosco\OneDrive\Documentos\vscode_01\flight_test_data"

REM Run the main analysis
"C:/Users/joao.bosco/OneDrive/Documentos/vscode_01/flight_test_data/.venv/Scripts/python.exe" plot_data.py

echo.
echo Analysis complete! Check the plots/ and processed_data/ folders for results.
echo.
pause
