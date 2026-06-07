@echo off
REM Script para validar EERR de una sucursal
REM Uso: validar_sucursal.bat "ruta\al\excel.xlsx" NombreUnidad

setlocal

if "%~1"=="" (
    echo Error: Falta la ruta al archivo Excel
    echo.
    echo Uso: validar_sucursal.bat "ruta\al\excel.xlsx" NombreUnidad
    echo.
    echo Ejemplo: validar_sucursal.bat "C:\Desktop\EERR RODEO.xlsx" Rodeo
    exit /b 1
)

if "%~2"=="" (
    echo Error: Falta el nombre de la unidad
    echo.
    echo Uso: validar_sucursal.bat "ruta\al\excel.xlsx" NombreUnidad
    echo.
    echo Ejemplo: validar_sucursal.bat "C:\Desktop\EERR RODEO.xlsx" Rodeo
    exit /b 1
)

set EXCEL_FILE=%~1
set UNIT_NAME=%~2

echo ========================================
echo VALIDACION EERR - %UNIT_NAME%
echo ========================================
echo.
echo Excel: %EXCEL_FILE%
echo Unidad: %UNIT_NAME%
echo.

REM Verificar que el archivo existe
if not exist "%EXCEL_FILE%" (
    echo [ERROR] Archivo no encontrado: %EXCEL_FILE%
    exit /b 1
)

REM Ejecutar validación con verbose
python validar_eerr.py --excel "%EXCEL_FILE%" --unit "%UNIT_NAME%" --verbose

echo.
echo ========================================
echo VALIDACION COMPLETADA
echo ========================================

endlocal
