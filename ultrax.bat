@echo off
title ULTRAX — Financial Intelligence
cd /d "%~dp0"

echo.
echo  ==========================================
echo   ULTRAX Financial Intelligence
echo   Iniciando servidor...
echo  ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (echo  [ERROR] Python no encontrado. & pause & exit /b 1)

python -c "import flask" >nul 2>&1
if errorlevel 1 (echo  Instalando dependencias... & pip install flask openpyxl pandas xlrd --quiet)

:: Abrir browser tras 2 segundos
start "" /B cmd /C "timeout /t 2 /nobreak >nul && start http://localhost:5000"

echo  Servidor en http://localhost:5000
echo  Cierra el navegador para detener el servidor.
echo.

:: Arrancar Flask — cuando el navegador llama /api/shutdown, el proceso termina
python app.py

:: Cerrar esta ventana de PowerShell/CMD automaticamente
exit
