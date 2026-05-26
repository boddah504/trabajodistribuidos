"""
OPTIRUTA+ - Proyecto Integrador
Diseno de Algoritmos
"""

import math
import time

# ============================================================
# CLIENTES (coordenadas x, y)
# ============================================================
clientes = [
    ["A", 0, 0],  # Deposito
    ["B", 1, 3],
    ["C", 5, 0],
    ["D", 5, 4],
    ["E", 3, 5],
    ["F", 7, 2],
    ["G", 8, 5],
    ["H", 4, 1],
]

paquetes = [
    ["Paq1", 3, 50],
    ["Paq2", 2, 30],
    ["Paq3", 4, 70],
    ["Paq4", 1, 20],
    ["Paq5", 5, 80],
    ["Paq6", 2, 40],
]

def dist(a, b):
    return math.sqrt((clientes[a][1] - clientes[b][1]) ** 2 +
                     (clientes[a][2] - clientes[b][2]) ** 2)


# ============================================================
# 1) VORAZ - Vecino mas cercano (O(n^2))
# ============================================================
def voraz():
    n = len(clientes)
    visitados = [False] * n
    ruta = [0]
    visitados[0] = True
    total = 0
    actual = 0
    for _ in range(n - 1):
        mejor = -1
        mejor_dist = 999999
        for i in range(n):
            if not visitados[i]:
                d = dist(actual, i)
                if d < mejor_dist:
                    mejor_dist = d
                    mejor = i
        ruta.append(mejor)
        total += mejor_dist
        visitados[mejor] = True
        actual = mejor
    total += dist(actual, 0)  # Regreso al inicio
    return ruta, round(total, 2)


# ============================================================
# 2) DIVIDE Y VENCERAS - QuickSort (O(n log n))
# ============================================================
def distancia_origen(punto):
    return math.sqrt(punto[1]**2 + punto[2]**2)

def qs(lista):
    if len(lista) <= 1:
        return lista
    pivote = distancia_origen(lista[len(lista) // 2])
    izquierda = [c for c in lista if distancia_origen(c) < pivote]
    medio = [c for c in lista if distancia_origen(c) == pivote]
    derecha = [c for c in lista if distancia_origen(c) > pivote]
    return qs(izquierda) + medio + qs(derecha)


# ============================================================
# 3) MOCHILA - Programacion Dinamica (O(n * capacidad))
# ============================================================
def mochila():
    cap = 8
    n = len(paquetes)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        peso = paquetes[i - 1][1]
        valor = paquetes[i - 1][2]
        for w in range(cap + 1):
            if peso <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - peso] + valor)
            else:
                dp[i][w] = dp[i - 1][w]
    # Reconstruir
    selec = []
    w = cap
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selec.append(paquetes[i - 1][0])
            w -= paquetes[i - 1][1]
    return dp[n][cap], selec


# ============================================================
# 4) BACKTRACKING con PODA (O(n!)) - pero con poda es mucho menor
# ============================================================
def backtracking():
    n = len(clientes)
    mejor_dist = 999999
    mejor_ruta = None
    contador = [0]  # Para contar ramas exploradas
    # Precalcular matriz de distancias
    mat = [[dist(i, j) for j in range(n)] for i in range(n)]

    def bt(actual, visitados, dist_actual, ruta):
        nonlocal mejor_dist, mejor_ruta
        # PODA: si la distancia actual ya es mayor o igual a la mejor, salimos
        if dist_actual >= mejor_dist:
            return
        # Si ya visitamos todos, cerramos el ciclo
        if len(ruta) == n:
            dist_total = dist_actual + mat[actual][0]
            contador[0] += 1
            if dist_total < mejor_dist:
                mejor_dist = dist_total
                mejor_ruta = ruta[:]
            return
        # Explorar siguientes clientes
        for i in range(n):
            if not visitados[i]:
                visitados[i] = True
                ruta.append(i)
                bt(i, visitados, dist_actual + mat[actual][i], ruta)
                ruta.pop()  # Vuelta atras
                visitados[i] = False

    visitados = [False] * n
    visitados[0] = True
    bt(0, visitados, 0, [0])
    return mejor_ruta, round(mejor_dist, 2), contador[0]


# ============================================================
# MENU PRINCIPAL
# ============================================================
def menu():
    while True:
        print("\n" + "=" * 50)
        print(" OPTIRUTA+ - MENU PRINCIPAL")
        print("=" * 50)
        print(" 1. ALGORITMO VORAZ (O(n^2))")
        print(" 2. DIVIDE Y VENCERAS - QuickSort (O(n log n))")
        print(" 3. MOCHILA - Programacion Dinamica")
        print(" 4. BACKTRACKING con PODA (O(n!))")
        print(" 5. COMPARATIVA COMPLETA")
        print(" 6. Ver clientes actuales")
        print(" 0. SALIR")
        print("-" * 50)
        op = input("Elija una opcion: ").strip()

        if op == "1":
            print("\n--- VORAZ (Vecino mas cercano) ---")
            print("Complejidad: O(n^2)")
            print("Idea: En cada paso elige el cliente mas cercano no visitado.\n")
            inicio = time.time()
            ruta, distancia = voraz()
            tiempo = time.time() - inicio
            print("Ruta encontrada:")
            for i in ruta:
                print(f"  {clientes[i][0]}", end="")
            print()
            print(f"Distancia total: {distancia}")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "2":
            print("\n--- DIVIDE Y VENCERAS (QuickSort) ---")
            print("Complejidad: O(n log n)")
            print("Idea: Ordena los clientes por cercania al origen.\n")
            inicio = time.time()
            ordenados = qs(clientes[:])
            tiempo = time.time() - inicio
            print("Clientes ordenados (mas cercanos primero):")
            for c in ordenados:
                d = math.sqrt(c[1]**2 + c[2]**2)
                print(f"  {c[0]} - distancia al origen: {d:.2f}")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "3":
            print("\n--- MOCHILA (Programacion Dinamica) ---")
            print("Complejidad: O(n * capacidad)")
            print("Idea: Maximizar el valor de los paquetes dentro de la capacidad.\n")
            inicio = time.time()
            valor, seleccion = mochila()
            tiempo = time.time() - inicio
            print(f"Capacidad del vehiculo: 8")
            print(f"Valor maximo cargado: ${valor}")
            print(f"Paquetes seleccionados: {', '.join(seleccion)}")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "4":
            print("\n--- BACKTRACKING con PODA ---")
            print("Complejidad: O(n!) sin poda, pero la poda reduce mucho")
            print("Idea: Prueba todas las rutas posibles pero retrocede")
            print("       cuando la distancia parcial supera la mejor actual.\n")
            inicio = time.time()
            ruta, distancia, ramas = backtracking()
            tiempo = time.time() - inicio
            n = len(clientes)
            print("Ruta optima encontrada:")
            for i in ruta:
                print(f"  {clientes[i][0]}", end="")
            print()
            print(f"Distancia total: {distancia}")
            print(f"Ramas exploradas: {ramas} de {math.factorial(n - 1)} posibles")
            print(f"Ahorro por poda: {(1 - ramas / math.factorial(n - 1)) * 100:.1f}%")
            print(f"Tiempo: {tiempo:.4f} segundos")
            print(f"(Sin poda habria explorado las {math.factorial(n - 1)} rutas completas)")
            input("\nPresione Enter para continuar...")

        elif op == "5":
            print("\n--- COMPARATIVA COMPLETA ---\n")

            print("[1/3] Ejecutando Voraz...")
            inicio = time.time()
            ruta_v, dist_v = voraz()
            tiempo_v = time.time() - inicio

            print("[2/3] Ejecutando Mochila...")
            inicio = time.time()
            valor_m, _ = mochila()
            tiempo_m = time.time() - inicio

            print("[3/3] Ejecutando Backtracking...")
            inicio = time.time()
            ruta_bt, dist_bt, ramas = backtracking()
            tiempo_bt = time.time() - inicio

            mejora = ((dist_v - dist_bt) / dist_v) * 100

            print("\n" + "=" * 55)
            print(" TABLA COMPARATIVA")
            print("=" * 55)
            print(f" {'Algoritmo':<25} {'Distancia':<12} {'Tiempo (s)':<15}")
            print("-" * 55)
            print(f" {'Voraz (O(n^2))':<25} {dist_v:<12} {tiempo_v:<15.6f}")
            print(f" {'Backtracking (O(n!))':<25} {dist_bt:<12} {tiempo_bt:<15.4f}")
            print(f" {'Mochila (O(n*cap))':<25} {'---':<12} {tiempo_m:<15.6f}")
            print()
            print(f" MEJORA del Backtracking vs Voraz: {mejora:.1f}%")
            print(f" Poda evito explorar {(1 - ramas / math.factorial(len(clientes) - 1)) * 100:.1f}% de rutas")
            print()
            print(" ANALISIS DE COMPLEJIDAD (Big O):")
            print(" - Voraz: O(n^2) - por cada cliente busca entre los demas")
            print(" - QuickSort: O(n log n) - divide la lista en mitades")
            print(" - Mochila DP: O(n * capacidad) - llena una tabla n x cap")
            print(" - Backtracking: O(n!) - explora permutaciones (la poda lo reduce)")
            input("\nPresione Enter para continuar...")

        elif op == "6":
            print("\n--- CLIENTES ACTUALES ---")
            for c in clientes:
                print(f"  {c[0]}: ({c[1]}, {c[2]})")
            input("\nPresione Enter para continuar...")

        elif op == "0":
            print("\nGracias por usar OPTIRUTA+")
            break

        else:
            print("Opcion invalida")

# Iniciar
menu()
