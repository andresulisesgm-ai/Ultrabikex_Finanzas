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

:: Cerrar cualquier proceso zombie que ya este escuchando en el puerto 5000, antes
:: de arrancar uno nuevo -- evita que un servidor viejo (de un cierre incompleto)
:: siga respondiendo mientras este arranca, sirviendo codigo desactualizado.
echo  Verificando puerto 5000...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo  Cerrando proceso zombie en puerto 5000 ^(PID %%p^)...
    taskkill /F /PID %%p >nul 2>&1
)
:: Arrancar Flask — cuando el navegador llama /api/shutdown, el proceso termina
python app.py

:: Cerrar esta ventana de PowerShell/CMD automaticamente
exit
