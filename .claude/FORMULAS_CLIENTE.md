# Fórmulas Exactas del Cliente (2 EEFF ULTRAX COMPLETO 2026.xlsx)

Basado en el archivo maestro del cliente. El sistema DEBE replicar estos cálculos EXACTAMENTE.

## ESTADO DE RESULTADOS (EERR)

### Estructura de Ingresos
```
Total Ingresos = Subtotal Ing. Mercancía + Subtotal Ing. Servicios + Subtotal Ing. Eventos + Subtotal Ing. Taller

Subtotal Ingresos por Venta de Mercancía = Ingresos por venta de mercancía - Devoluciones - Descuentos

Subtotal Ingresos por Servicios = SUM(Ing. servicios café + Ing. zona FIT + Ing. fletes + otros servicios)

Subtotal Ingresos por Eventos = SUM(Ingresos por eventos)

Subtotal Ingresos por Taller = SUM(Ingresos por taller)
```

### Estructura de Costos
```
Total Costo de Ventas = Subtotal Costo Mercancía + Subtotal Costo Servicios + Subtotal Costo Eventos

Subtotal Costo de Ventas por Mercancía = SUM(Costo de venta por mercancía)

Subtotal Costo de Ventas por Servicios = SUM(Costo de venta por servicio del café)

Subtotal Costo de Ventas por Eventos = SUM(Costo de ventas por eventos)
```

### Utilidad Bruta (3 tipos)
```
Utilidad Bruta por Venta de Mercancía y Taller = Subtotal Ing. Mercancía + Subtotal Ing. Taller - Subtotal Costo Mercancía

Utilidad Bruta por Servicios = Subtotal Ing. Servicios - Subtotal Costo Servicios

Utilidad Bruta por Eventos = Subtotal Ing. Eventos - Subtotal Costo Eventos

Utilidad Bruta TOTAL = Total Ingresos - Total Costo de Ventas
```

### Gastos Operacionales
```
Total Gastos Operacionales = Subtotal Gastos Administración + Subtotal Gastos RRHH + Subtotal Gastos Comercialización + Subtotal Gastos Mercadeo + Subtotal Gastos TI

Categorías de gastos:
1. Administración: servicios públicos, telefonía, alquiler, condominio, outsourcing, oficina, limpieza, alimentos, honorarios, retenciones, mantenimiento, viáticos admin, seguro, impuesto, depreciación, deterioro, amortización, comisiones bancarias, IGTF, intereses
2. Recursos Humanos: sueldos, salarios, horas extras, complemento sueldos, bono alimentación, vacaciones, utilidades, prestaciones, aporte patronal, guardería, HCM, salud, uniformes, fiestas, capacitación, transporte personal
3. Comercialización y Logística: viáticos comerciales, fletes, almacenaje, importación, comisiones empleados, gasolina, garantías, suscripciones
4. Mercadeo: redes sociales, medios publicitarios, impresiones, decoración, muestras, campañas
5. TI+I: dominio, servidores, software tecnológico
```

### Utilidad Neta
```
Utilidad Neta = Utilidad Bruta - Total Gastos Operacionales + Otros Ingresos No Operacionales - Otros Gastos No Operacionales

Otros Ingresos No Operacionales: Sobrante en ventas, Sobrante de inventarios, Ganancia en venta de activos, Ganancia por tasa cambiaria, Ganancia por diferencias en pagos

Otros Gastos No Operacionales: Faltante en Ventas, Pérdida en venta de activos, Pérdida en siniestros, Pérdida en tasa cambiaria, Pérdida por diferencias en pagos, Multas, Faltante de inventarios, Deterioro de inventarios

Utilidad Neta después de ISLR = Utilidad Neta - ISLR
```

---

## INDICADORES FINANCIEROS (del archivo ESF ULTRAX)

### Márgenes
```
Margen Bruto % = Utilidad Bruta / Ingresos Brutos
   Meta: 30% a 50%
   Semáforo: Verde ≥30% | Ámbar 20-30% | Rojo <20%

Margen Neto % = Utilidad Neta después de ISLR / Ingresos Brutos
   Meta: 5% a 15%
   Semáforo: Verde ≥10% | Ámbar 0-10% | Rojo <0%
```

### Rentabilidad
```
ROE (Return on Equity) = Utilidad Neta / Patrimonio
   Meta: 10% a 20%
   Fórmula en Excel: =IFERROR(Utilidad_Neta / Total_Patrimonio, "")

ROA (Return on Assets) = Utilidad Neta / Total Activos
   Meta: 5% a 15%
   Fórmula en Excel: =IFERROR(Utilidad_Neta / Total_Activos, "")
```

### Rotación
```
Rotación de Inventarios (en meses) = (Inventario * 3) / Costo de Ventas
   Meta: 2 a 3 meses
   Fórmula en Excel: =IFERROR(Inventario * 3 / Costo_Ventas_Trimestral, "")

Rotación de Activos (veces al año) = Ingresos Brutos / Total Activos
   Meta: 1.5 a 2 veces al año
   Fórmula en Excel: =IFERROR(Ingresos_Trimestral / Total_Activos, "")

Período de Cobro (días) = (Cuentas por Cobrar / Ingresos Brutos) * 90
   Meta: 30 a 60 días máximo
   Fórmula en Excel: =IFERROR(CxC / Ingresos_Trimestral * 90, "")
```

### Liquidez
```
Ratio Corriente = Activos Corrientes / Pasivos Corrientes
   Meta: 1.5 a 2
   Fórmula en Excel: =IFERROR(Activos_Corrientes / Pasivos_Corrientes, "")

Prueba Ácida = (Activos Corrientes - Inventarios) / Pasivos Corrientes
   Meta: 0.8 a 1
   Fórmula en Excel: =IFERROR((Activos_Corrientes - Inventarios) / Pasivos_Corrientes, "")

Prueba Defensiva = Efectivo y Equivalentes / Pasivos Corrientes
   Meta: 0.5 a 0.7
   Fórmula en Excel: =IFERROR(Efectivo / Pasivos_Corrientes, "")
```

### Endeudamiento
```
Ratio Endeudamiento = Total Pasivos / Total Patrimonio
   Meta: 0.4 a 0.6
   Fórmula en Excel: =IFERROR(Total_Pasivos / Total_Patrimonio, "")
```

### Eficiencia (usados en dashboard actual)
```
% Costo/Venta = Costo de Ventas / Ingresos Brutos
   Meta: ≤50%
   Semáforo: Verde ≤50% | Ámbar 50-70% | Rojo >70%

% Gasto/Venta = Gastos Operacionales / Ingresos Brutos
   Meta: ≤30%
   Semáforo: Verde ≤30% | Ámbar 30-45% | Rojo >45%
```

---

## PUNTO DE EQUILIBRIO (solo por unidad individual)

```
Margen de Contribución = Ingresos - Costos de Ventas
Margen de Contribución % = (Ingresos - Costos) / Ingresos

Punto de Equilibrio en Ingresos = Gastos Operacionales / Margen_Contribución_%

Cobertura del P.E. % = Ingresos Actuales / P.E._Ingresos
   Meta: ≥100%
   Semáforo: Verde ≥100% | Ámbar 80-100% | Rojo <80%
```

---

## DIVIDENDOS (del archivo ESF ULTRAX)

Fórmula por accionista:
```
Dividendo = Porcentaje_Participación * Ingresos_Brutos_Trimestral * 2%

Ejemplo (Camilo Gonzalez Parra):
= (% en col D) * Ingresos_Q1 * 2%

Total Dividendos = SUM(todos los accionistas)

Utilidades Reinvertidas = Utilidad Neta antes de ISLR - Total Dividendos
```

---

## ESTRUCTURA DEL BALANCE (ESF)

### ACTIVOS CORRIENTES
- Efectivo y Equivalentes (Cajas + Bancos en Bs y $ + en tránsito)
- Cuentas por Cobrar (Clientes + Empleados + Socios + Empresas relacionadas + Otras)
- Préstamos por Cobrar
- Anticipos (Proveedores + Socios + Empleados)
- Inventarios (Mercancía + Suministros + En tránsito + Consignación)
- Prepagados (Impuestos + Gastos pagados por anticipado)

### ACTIVOS NO CORRIENTES
- Otros activos no corrientes (Deudores LP + Otras CxC + Préstamos LP + Anticipos LP)
- Propiedades de inversión
- Propiedades, Plantas y Equipos (Terrenos + Mobiliario + Maquinaria + Vehículos + Edificios + Materiales eventos + Herramientas + Utensilios + Equipamiento deportivo + Mejoras arrendadas + Software)

### PASIVOS CORRIENTES
- Cuentas por Pagar (Proveedores + Empresas relacionadas + Socios + TDC + Consignación + Otras)
- Sueldos y Salarios por pagar
- Retenciones laborales + Aportes patronales
- Intereses por pagar
- Impuestos por pagar
- Dividendos por pagar
- Préstamos por Pagar (Empresas + Socios + Empleados + Bancarios)
- Anticipos de clientes
- Provisiones para empleados

### PASIVOS NO CORRIENTES
- Otras cuentas por pagar LP
- Intereses por pagar LP
- Préstamos por pagar LP
- Provisiones LP

### PATRIMONIO
- Capital social
- Reservas legales y estatutarias
- Superávit por revaluación
- Resultados acumulados
- Resultados del ejercicio

---

## NOTAS IMPORTANTES

1. **Ingresos No Operacionales NO suman al Total Ingresos principal** (línea 4 EERR) — solo se usan para calcular Utilidad Neta final.

2. **La Utilidad Neta tiene 2 versiones**:
   - Antes de ISLR (la que se usa para ROE/ROA)
   - Después de ISLR (la que va al Patrimonio)

3. **Los indicadores usan IFERROR** para evitar divisiones por cero — retornan cadena vacía "" si hay error.

4. **Período de cobro usa 90 días** (trimestre), no 30 días (mes).

5. **Rotación de Inventarios se expresa en MESES**, multiplicando inventario por 3 (trimestres/año) y dividiendo por costo trimestral.

6. **El archivo tiene 2 hojas de EERR**:
   - " EERR ULTRAX" (con espacio inicial) — usa estructura agrupada con subtotales
   - "N EERR ULTRAX" — estructura más plana, suma por unidades

7. **Consolidado** = suma de las 6 unidades (Rodeo, PiedeMonte, Terracota, Ucafe, Barinas, Los Naranjos)

---

## ACCIONES PARA EL SISTEMA

### ✅ Ya implementado correctamente
- Margen Bruto % (Utilidad Bruta / Ingresos)
- Margen Neto % (Utilidad Neta / Ingresos)
- % Costo/Venta
- % Gasto/Venta
- Punto de Equilibrio básico (solo por unidad)
- Estructura de gastos por categorías (alineada con las 6 del cliente)

### ❌ Falta implementar / validar
1. **Dividir Utilidad Bruta en 3 tipos** (Mercancía+Taller, Servicios, Eventos) en el EERR Detallado
2. **Añadir ROE** (Utilidad Neta / Patrimonio) — requiere datos de Patrimonio desde ESF
3. **Añadir ROA** (Utilidad Neta / Total Activos) — requiere datos de Activos desde ESF
4. **Añadir Ratio Corriente** (Activos Corrientes / Pasivos Corrientes)
5. **Añadir Prueba Ácida** ((Activos Corrientes - Inventarios) / Pasivos Corrientes)
6. **Añadir Prueba Defensiva** (Efectivo / Pasivos Corrientes)
7. **Añadir Ratio Endeudamiento** (Total Pasivos / Patrimonio)
8. **Añadir Rotación de Inventarios** (en meses)
9. **Añadir Rotación de Activos** (veces al año)
10. **Añadir Período de Cobro** (en días)
11. **Validar que Ingresos No Operacionales NO sumen al Total Ingresos** (revisar parser)
12. **Añadir módulo de Dividendos** (cálculo por accionista con % participación)
13. **Completar todas las partidas del ESF** según la estructura del cliente
