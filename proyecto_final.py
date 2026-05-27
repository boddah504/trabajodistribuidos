"""
OPTIRUTA+ - Proyecto Integrador
Diseno de Algoritmos
Incluye: transportes (moto, carro, camion)
         paquetes con largo, peso, cantidad
         rutas terrestres (simuladas)
"""

import math
import time

# ============================================================
# TRANSPORTES
# ============================================================
TRANSPORTES = {
    "moto":   {"nombre": "Moto",   "peso_max": 50,  "largo_max": 100},
    "carro":  {"nombre": "Carro",  "peso_max": 300, "largo_max": 300},
    "camion": {"nombre": "Camion", "peso_max": 1000,"largo_max": 1000},
}

# ============================================================
# CLIENTES (coordenadas x, y)
# ============================================================
clientes = [
    ["A", 0, 0],
    ["B", 1, 3],
    ["C", 5, 0],
    ["D", 5, 4],
    ["E", 3, 5],
    ["F", 7, 2],
    ["G", 8, 5],
    ["H", 4, 1],
]

# ============================================================
# PAQUETES (nombre, largo_cm, peso_kg, cantidad, valor_unitario)
# ============================================================
paquetes = [
    ["Paq.A",  30, 2,  5, 50],
    ["Paq.B",  50, 5,  3, 80],
    ["Paq.C",  20, 1,  10, 20],
    ["Paq.D",  80, 10, 2, 120],
    ["Paq.E",  40, 3,  4, 60],
    ["Paq.F",  100, 15, 1, 200],
]

transporte_actual = "carro"

# ============================================================
# DISTANCIA TERRESTRE (simulada: aerea * 1.3)
# ============================================================
def dist(a, b):
    d = math.sqrt((clientes[a][1] - clientes[b][1]) ** 2 +
                  (clientes[a][2] - clientes[b][2]) ** 2)
    return d * 1.3  # Factor carretera


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
    total += dist(actual, 0)
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
# 3) MOCHILA - Programacion Dinamica (O(n * peso * largo))
# ============================================================
def mochila():
    t = TRANSPORTES[transporte_actual]
    peso_max = t["peso_max"]
    largo_max = t["largo_max"]

    # Generar todos los items (cada unidad)
    items = []
    for p in paquetes:
        nombre, largo, peso, cantidad, valor = p
        for _ in range(cantidad):
            items.append((nombre, largo, peso, valor))

    n = len(items)
    # DP 3D: [items+1][peso+1][largo+1]
    dp = [[[0] * (largo_max + 1) for _ in range(peso_max + 1)] for __ in range(n + 1)]

    for i in range(1, n + 1):
        nom, lar, pes, val = items[i - 1]
        for w in range(peso_max + 1):
            for l in range(largo_max + 1):
                if pes <= w and lar <= l:
                    dp[i][w][l] = max(dp[i - 1][w][l],
                                      dp[i - 1][w - pes][l - lar] + val)
                else:
                    dp[i][w][l] = dp[i - 1][w][l]

    # Reconstruir
    seleccionados = {}
    w, l = peso_max, largo_max
    for i in range(n, 0, -1):
        if dp[i][w][l] != dp[i - 1][w][l]:
            nom, lar, pes, val = items[i - 1]
            seleccionados[nom] = seleccionados.get(nom, 0) + 1
            w -= pes
            l -= lar

    return dp[n][peso_max][largo_max], seleccionados, peso_max - w, largo_max - l


# ============================================================
# 4) BACKTRACKING con PODA (O(n!))
# ============================================================
def backtracking():
    n = len(clientes)
    mejor_dist = 999999
    mejor_ruta = None
    contador = [0]
    mat = [[dist(i, j) for j in range(n)] for i in range(n)]

    def bt(actual, visitados, dist_actual, ruta):
        nonlocal mejor_dist, mejor_ruta
        if dist_actual >= mejor_dist:
            return
        if len(ruta) == n:
            dist_total = dist_actual + mat[actual][0]
            contador[0] += 1
            if dist_total < mejor_dist:
                mejor_dist = dist_total
                mejor_ruta = ruta[:]
            return
        for i in range(n):
            if not visitados[i]:
                visitados[i] = True
                ruta.append(i)
                bt(i, visitados, dist_actual + mat[actual][i], ruta)
                ruta.pop()
                visitados[i] = False

    visitados = [False] * n
    visitados[0] = True
    bt(0, visitados, 0, [0])
    return mejor_ruta, round(mejor_dist, 2), contador[0]


# ============================================================
# MENU PRINCIPAL
# ============================================================
def menu():
    global transporte_actual

    while True:
        t = TRANSPORTES[transporte_actual]
        print("\n" + "=" * 50)
        print(" OPTIRUTA+ - MENU PRINCIPAL")
        print("=" * 50)
        print(f" Transporte: {t['nombre']} ({t['peso_max']}kg / {t['largo_max']}cm)")
        print("-" * 50)
        print(" 1. ALGORITMO VORAZ (O(n^2))")
        print(" 2. DIVIDE Y VENCERAS - QuickSort (O(n log n))")
        print(" 3. MOCHILA - Programacion Dinamica")
        print(" 4. BACKTRACKING con PODA (O(n!))")
        print(" 5. COMPARATIVA COMPLETA")
        print(" 6. Cambiar transporte")
        print(" 7. Ver datos actuales")
        print(" 0. SALIR")
        print("-" * 50)
        op = input("Elija una opcion: ").strip()

        if op == "1":
            print("\n--- VORAZ (Vecino mas cercano) ---")
            print("Complejidad: O(n^2)")
            print("Ruta por carretera (distancia terrestre simulada).\n")
            inicio = time.time()
            ruta, distancia = voraz()
            tiempo = time.time() - inicio
            print("Ruta:")
            for i in ruta:
                print(f"  {clientes[i][0]}", end="")
            print()
            print(f"Distancia total: {distancia} km (terrestre)")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "2":
            print("\n--- DIVIDE Y VENCERAS (QuickSort) ---")
            print("Complejidad: O(n log n)\n")
            inicio = time.time()
            ordenados = qs(clientes[:])
            tiempo = time.time() - inicio
            print("Clientes ordenados por cercania al origen:")
            for c in ordenados:
                d = math.sqrt(c[1]**2 + c[2]**2)
                print(f"  {c[0]} - distancia: {d:.2f}")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "3":
            print("\n--- MOCHILA (Programacion Dinamica) ---")
            print(f"Complejidad: O(n * peso_max * largo_max)")
            print(f"Transporte: {t['nombre']} ({t['peso_max']}kg / {t['largo_max']}cm)\n")
            inicio = time.time()
            valor, selec, peso_u, largo_u = mochila()
            tiempo = time.time() - inicio
            print(f"Valor maximo cargado: ${valor}")
            print(f"Peso usado: {peso_u}/{t['peso_max']}kg")
            print(f"Largo usado: {largo_u}/{t['largo_max']}cm")
            print("Paquetes seleccionados:")
            for nom, cant in selec.items():
                print(f"  {nom} x{cant}")
            print(f"Tiempo: {tiempo:.6f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "4":
            print("\n--- BACKTRACKING con PODA ---")
            print("Complejidad: O(n!) - poda reduce drasticamente\n")
            inicio = time.time()
            ruta, distancia, ramas = backtracking()
            tiempo = time.time() - inicio
            n = len(clientes)
            print("Ruta optima (terrestre):")
            for i in ruta:
                print(f"  {clientes[i][0]}", end="")
            print()
            print(f"Distancia total: {distancia} km")
            print(f"Ramas exploradas: {ramas} de {math.factorial(n - 1)} posibles")
            print(f"Ahorro por poda: {(1 - ramas / math.factorial(n - 1)) * 100:.1f}%")
            print(f"Tiempo: {tiempo:.4f} segundos")
            input("\nPresione Enter para continuar...")

        elif op == "5":
            print("\n--- COMPARATIVA COMPLETA ---\n")
            print("[1/3] Voraz...")
            inicio = time.time()
            ruta_v, dist_v = voraz()
            tiempo_v = time.time() - inicio
            print("[2/3] Mochila...")
            inicio = time.time()
            valor_m, sel_m, pu, lu = mochila()
            tiempo_m = time.time() - inicio
            print("[3/3] Backtracking...")
            inicio = time.time()
            ruta_bt, dist_bt, ramas = backtracking()
            tiempo_bt = time.time() - inicio
            mejora = ((dist_v - dist_bt) / dist_v) * 100

            print("\n" + "=" * 55)
            print(f" TABLA COMPARATIVA ({t['nombre']})")
            print("=" * 55)
            print(f" {'Algoritmo':<25} {'Distancia':<12} {'Tiempo (s)':<15}")
            print("-" * 55)
            print(f" {'Voraz (O(n^2))':<25} {dist_v:<12} {tiempo_v:<15.6f}")
            print(f" {'Backtracking (O(n!))':<25} {dist_bt:<12} {tiempo_bt:<15.4f}")
            print(f" {'Mochila DP':<25} {'---':<12} {tiempo_m:<15.6f}")
            print()
            print(f" MEJORA del Backtracking vs Voraz: {mejora:.1f}%")
            print(f" Poda evito explorar {(1 - ramas / math.factorial(len(clientes) - 1)) * 100:.1f}% de rutas")
            print(f" Mochila: ${valor_m} | Peso: {pu}/{t['peso_max']}kg | Largo: {lu}/{t['largo_max']}cm")
            print("\n COMPLEJIDAD (Big O):")
            print(" - Voraz: O(n^2)")
            print(" - QuickSort: O(n log n)")
            print(" - Mochila DP: O(n * peso_max * largo_max)")
            print(" - Backtracking: O(n!) con poda")
            input("\nPresione Enter para continuar...")

        elif op == "6":
            print("\n--- CAMBIAR TRANSPORTE ---")
            print(" 1. Moto   (50kg / 100cm)")
            print(" 2. Carro  (300kg / 300cm)")
            print(" 3. Camion (1000kg / 1000cm)")
            op_t = input("Elija: ").strip()
            if op_t == "1":
                transporte_actual = "moto"
                print("Transporte cambiado a Moto")
            elif op_t == "2":
                transporte_actual = "carro"
                print("Transporte cambiado a Carro")
            elif op_t == "3":
                transporte_actual = "camion"
                print("Transporte cambiado a Camion")
            else:
                print("Opcion invalida")
            input("\nPresione Enter para continuar...")

        elif op == "7":
            print("\n--- DATOS ACTUALES ---")
            t = TRANSPORTES[transporte_actual]
            print(f"Transporte: {t['nombre']} ({t['peso_max']}kg / {t['largo_max']}cm)")
            print("\nClientes:")
            for c in clientes:
                print(f"  {c[0]}: ({c[1]}, {c[2]})")
            print("\nPaquetes (nombre, largo, peso, cantidad, valor):")
            for p in paquetes:
                print(f"  {p[0]}: {p[1]}cm, {p[2]}kg, x{p[3]}, ${p[4]}/u")
            input("\nPresione Enter para continuar...")

        elif op == "0":
            print("\nGracias por usar OPTIRUTA+")
            break
        else:
            print("Opcion invalida")

menu()
