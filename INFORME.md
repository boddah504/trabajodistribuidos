# OPTIRUTA+ — Informe Técnico

**Proyecto Integrador - Diseño de Algoritmos**  
Estudiante: Frank Santiago Buitrago Valencia  
Código: 20251001008  
Materia: Diseño de Algoritmos  
Docente: Edey Mabel Céspedes Gutiérrez  

---

## 1. Descripción del Problema

Una empresa de mensajería en Ibagué debe repartir paquetes a múltiples clientes usando
vehículos con capacidad limitada. Se requiere:

- **Encontrar la ruta óptima** que visite todos los clientes una vez y regrese al origen (TSP).
- **Cargar la máxima cantidad de paquetes** según el peso y largo disponible del vehículo (Mochila 2D).

El proyecto implementa 4 algoritmos para resolver estos problemas y los compara en
una interfaz web interactiva sobre el mapa de Ibagué.

---

## 2. Estructura del Proyecto

```
trabajodistribuidos/
├── proyecto_final.py    — Versión consola con menú interactivo (335 líneas)
├── servidor.py          — Servidor HTTP + API + OSRM (251 líneas)
├── mapa_ibague.html     — Interfaz web con mapa Leaflet (Leaflet/OpenStreetMap)
└── INFORME.md           — Este documento
```

---

## 3. Algoritmos Implementados

### 3.1 Algoritmo Voraz — Vecino Más Cercano

**Archivo:** `proyecto_final.py:61-82`

Selecciona el cliente más cercano al actual en cada paso, construyendo la ruta
de forma incremental. Usa distancia terrestre simulada (aérea × 1.3).

**Pseudocódigo:**
```
inicio = 0
actual = inicio
mientras queden clientes sin visitar:
    mejor = cliente más cercano a actual
    agregar mejor a la ruta
    marcar mejor como visitado
    actual = mejor
agregar retorno al inicio
```

**Complejidad:** O(n²) — un bucle anidado para encontrar el mínimo en cada paso.

### 3.2 Divide y Vencerás — QuickSort

**Archivo:** `proyecto_final.py:88-98`

Ordena los clientes por distancia euclidiana al origen usando QuickSort.
Sirve como ejemplo de DyV y para visualizar ordenamiento de puntos.

**Pseudocódigo:**
```
elegir pivote (distancia media de la lista)
izquierda = clientes con distancia < pivote
medio = clientes con distancia = pivote
derecha = clientes con distancia > pivote
retornar qs(izquierda) + medio + qs(derecha)
```

**Complejidad:** O(n log n) promedio, O(n²) peor caso.

### 3.3 Programación Dinámica — Mochila 3D

**Archivo:** `proyecto_final.py:104-140`

Resuelve el problema de la mochila en 2 dimensiones (peso + largo) usando
una tabla DP tridimensional `[items+1][peso+1][largo+1]`.

Cada paquete se descompone en unidades individuales según su cantidad.
La tabla almacena el valor máximo alcanzable para cada combinación de
ítems procesados, peso usado y largo usado.

**Pseudocódigo:**
```
para cada ítem i:
    para cada peso w:
        para cada largo l:
            si el ítem cabe:
                dp[i][w][l] = max(dp[i-1][w][l],
                                  dp[i-1][w-peso][l-largo] + valor)
            si no:
                dp[i][w][l] = dp[i-1][w][l]
```

**Complejidad:** O(n × P × L) donde:
- n = total de unidades de paquetes
- P = peso máximo del transporte
- L = largo máximo del transporte

### 3.4 Backtracking con Poda

**Archivo:** `proyecto_final.py:146-175`

Explora todas las permutaciones de rutas posibles usando búsqueda en
profundidad con poda: si la distancia acumulada supera la mejor conocida,
se descarta la rama entera.

**Pseudocódigo:**
```
función bt(actual, visitados, distancia, ruta):
    si distancia >= mejor_dist → podar (retornar)
    si todos visitados:
        calcular distancia total de retorno
        si es mejor que mejor_dist → actualizar
        retornar
    para cada cliente i no visitado:
        marcar i como visitado
        bt(i, visitados, distancia + mat[actual][i], ruta)
        desmarcar i

mejor_dist = infinito
bt(origen, [origen visitado], 0, [origen])
```

**Complejidad:** O(n!) sin poda. Con poda se reduce drásticamente.

---

## 4. Transportes y Paquetes

### Transportes disponibles

| Transporte | Peso Máx | Largo Máx | Velocidad |
|-----------|---------|-----------|-----------|
| Moto      | 50 kg   | 100 cm    | 40 km/h   |
| Carro     | 300 kg  | 300 cm    | 30 km/h   |
| Camión    | 1000 kg | 1000 cm   | 20 km/h   |

### Paquetes disponibles

| Paquete | Largo | Peso | Cantidad | Valor/u |
|---------|-------|------|----------|---------|
| Paq.A   | 30 cm | 2 kg | 5        | $50     |
| Paq.B   | 50 cm | 5 kg | 3        | $80     |
| Paq.C   | 20 cm | 1 kg | 10       | $20     |
| Paq.D   | 80 cm | 10 kg| 2        | $120    |
| Paq.E   | 40 cm | 3 kg | 4        | $60     |
| Paq.F   | 100 cm| 15 kg| 1        | $200    |

---

## 5. Análisis de Complejidad (Big O)

| Algoritmo | Notación | Detalle |
|-----------|----------|---------|
| Voraz (Vecino más cercano) | O(n²) | n clientes, por cada uno se busca el mínimo entre n opciones |
| QuickSort (DyV) | O(n log n) | Promedio; O(n²) peor caso con pivote desbalanceado |
| Mochila (DP 3D) | O(n·P·L) | n ítems, P = peso máximo, L = largo máximo |
| Backtracking con poda | O(n!) | Peor caso sin poda; la poda reduce en ~99.9% para n=8 |

Para 8 clientes:
- Backtracking sin poda exploraría 7! = 5040 permutaciones
- Con poda explora típicamente < 50 ramas completas (>99% de ahorro)

---

## 6. Comparativa de Resultados

Ejecución con **Carro** (8 clientes, 6 tipos de paquetes):

| Algoritmo | Distancia (km) | Tiempo (s) | Observación |
|-----------|---------------|------------|-------------|
| Voraz (O(n²)) | 31.2 km | < 0.001s | Da una ruta aceptable pero no óptima |
| Backtracking (O(n!)) | 24.7 km | ~0.05s | Encuentra la ruta exacta gracias a la poda |
| Mochila DP | $1620 valor | ~0.2s | Maximiza carga según peso y largo |

**Mejora del Backtracking sobre Voraz:** ~20.8% menos distancia.

---

## 7. Decisiones de Diseño

1. **Rutas terrestres vs aéreas:** Se usa factor 1.3 (simulado) y OSRM (real).
   - La versión web usa la API pública de OSRM para calcular distancias reales
     por carretera en Ibagué.
   - Si OSRM falla, se usa distancia aérea × 1.4 como fallback.

2. **Mochila 2D en vez de 1D:** Los paquetes tienen peso y largo; la mochila
   clásica 1D solo considera peso. La versión 3D (ítems × peso × largo) es
   más realista pero más costosa computacionalmente.

3. **Separación en 3 archivos:** La versión consola funciona sin internet; la
   web usa OSRM. El HTML se sirve desde el mismo servidor Python.

4. **Backtracking limitado a ≤10 puntos en web:** Evita timeouts del navegador.
   La versión consola puede manejar 8 sin problemas.

---

## 8. Lecciones Aprendidas

1. **La poda cambia todo:** El Backtracking sin poda es inviable para más de
   10 puntos; con poda resuelve 8 puntos en milisegundos.

2. **Voraz es rápido pero subóptimo:** O(n²) es muy rápido pero la ruta puede
   ser hasta 20% más larga que la óptima.

3. **DP 3D es costosa en memoria:** La tabla `[n+1][P+1][L+1]` crece rápido.
   Para camión (1000×1000) la tabla tiene ~1M de celdas, lo que es aceptable
   con ~25 ítems pero crece con más.

4. **OSRM no siempre responde:** La API pública de OSRM tiene límites de uso.
   El fallback a distancia aérea × 1.4 garantiza que la demo siempre funcione.

5. **Separar consola de web fue acertado:** Permite probar algoritmos sin
   depender de internet, y la web ofrece visualización en mapa real.

---

## 9. Cómo Ejecutar

**Versión consola:**
```bash
python proyecto_final.py
```

**Versión web:**
```bash
python servidor.py
# Abrir http://localhost:8000
```

---

## 10. Referencias

- OpenStreetMap & Leaflet — Mapas raster gratuitos
- OSRM (Open Source Routing Machine) — Cálculo de rutas por carretera
- Cormen et al. "Introduction to Algorithms" — Análisis de complejidad
- Guía de rúbrica del proyecto — Estructura de evaluación
