#!/bin/bash
# Script para validar todas las sucursales
# Uso: ./validar_todas_sucursales.sh

echo "========================================"
echo "VALIDACIÓN MASIVA - TODAS LAS SUCURSALES"
echo "========================================"
echo ""

# Directorio de reportes
REPORTES_DIR="reportes_validacion"
mkdir -p "$REPORTES_DIR"

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Función para validar una sucursal
validar_sucursal() {
    local excel=$1
    local unit=$2
    local output_file="$REPORTES_DIR/${unit}_${TIMESTAMP}.json"

    echo ""
    echo "----------------------------------------"
    echo "Validando: $unit"
    echo "----------------------------------------"

    if [ ! -f "$excel" ]; then
        echo "[ERROR] Archivo no encontrado: $excel"
        return 1
    fi

    python validar_eerr.py \
        --excel "$excel" \
        --unit "$unit" \
        --save "$output_file"

    if [ $? -eq 0 ]; then
        echo "[OK] $unit validado correctamente"
        return 0
    else
        echo "[ERROR] Falló la validación de $unit"
        return 1
    fi
}

# Contador
total=0
exitosos=0
fallidos=0

# CONFIGURACIÓN: Ajustar estas rutas según tus archivos
# Formato: validar_sucursal "ruta/al/excel.xlsx" "NombreUnidad"

# Rodeo
if validar_sucursal "C:/Users/andre/Desktop/EERR RODEO ENERO.xlsx" "Rodeo"; then
    ((exitosos++))
else
    ((fallidos++))
fi
((total++))

# Terracota (descomentar cuando tengas el archivo)
# if validar_sucursal "C:/Users/andre/Desktop/EERR TERRACOTA ENERO.xlsx" "Terracota"; then
#     ((exitosos++))
# else
#     ((fallidos++))
# fi
# ((total++))

# Altamira (descomentar cuando tengas el archivo)
# if validar_sucursal "C:/Users/andre/Desktop/EERR ALTAMIRA ENERO.xlsx" "Altamira"; then
#     ((exitosos++))
# else
#     ((fallidos++))
# fi
# ((total++))

# Resumen final
echo ""
echo "========================================"
echo "RESUMEN DE VALIDACIONES"
echo "========================================"
echo "Total:     $total"
echo "Exitosos:  $exitosos"
echo "Fallidos:  $fallidos"
echo ""
echo "Reportes guardados en: $REPORTES_DIR"
echo "========================================"

# Exit code
if [ $fallidos -eq 0 ]; then
    exit 0
else
    exit 1
fi
