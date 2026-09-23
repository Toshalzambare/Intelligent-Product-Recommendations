@echo off
echo =======================================================
echo Starting Intelligent Product Recommendation System...
echo =======================================================

echo.
echo [1/2] Starting FastAPI Backend on Port 8000...
start "FastAPI Backend" cmd /c "call venv\Scripts\activate.bat && uvicorn backend.app:app --host 127.0.0.1 --port 8000"

echo Waiting for the backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo [2/2] Starting Streamlit Frontend on Port 8501...
start "Streamlit Frontend" cmd /c "call venv\Scripts\activate.bat && streamlit run frontend\streamlit_app.py --server.port 8501"

echo.
echo =======================================================
echo Both servers have been launched in separate windows!
echo Streamlit will automatically open in your default browser.
echo You can now close this command window.
echo =======================================================
pause
