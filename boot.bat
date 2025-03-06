@echo off
start cmd /k "cd /d %~dp0AI && call ..\Sample_Venv\Scripts\activate && python -m uvicorn api:app --port 8030"
start cmd /k "cd /d %~dp0site && call ..\Sample_Venv\Scripts\activate && python app.py"
