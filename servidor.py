"""
OPTIRUTA+ - Servidor local con rutas terrestres
Ejecuta: python servidor.py
Luego abre: http://localhost:8000
Usa OSRM para distancias reales por carretera en Ibagué
"""

import math
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================
# TRANSPORTES
# ============================================================
TRANSPORTES = {
    "moto":   {"nombre": "Moto",   "peso_max": 50,  "largo_max": 100,  "velocidad": "40 km/h"},
    "carro":  {"nombre": "Carro",  "peso_max": 300, "largo_max": 300,  "velocidad": "30 km/h"},
    "camion": {"nombre": "Camion", "peso_max": 1000,"largo_max": 1000, "velocidad": "20 km/h"},
}

# ============================================================
# PAQUETES (nombre, largo_cm, peso_kg, cantidad, valor_unitario)
# ============================================================
PAQUETES = [
    ["Paq.A",  30, 2,  5, 50],
    ["Paq.B",  50, 5,  3, 80],
    ["Paq.C",  20, 1,  10, 20],
    ["Paq.D",  80, 10, 2, 120],
    ["Paq.E",  40, 3,  4, 60],
    ["Paq.F",  100, 15, 1, 200],
]

# ============================================================
# DISTANCIA POR CARRETERA (OSRM)
# ============================================================
_cache_distancias = {}

def distancia_terrestre(coord1, coord2):
    """Distancia real en km por carretera usando OSRM"""
    key = (round(coord1[0], 5), round(coord1[1], 5), round(coord2[0], 5), round(coord2[1], 5))
    if key in _cache_distancias:
        return _cache_distancias[key]

    # OSRM necesita formato: lng,lat
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}?overview=false")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OPTIRUTA+"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        dist_km = data["routes"][0]["distance"] / 1000
        _cache_distancias[key] = dist_km
        return dist_km
    except:
        d = _distancia_aerea(coord1, coord2) * 1.4
        _cache_distancias[key] = d
        return d


def geometria_ruta_osrm(clientes, orden):
    """Obtiene la polilinea de calles reales desde OSRM para una secuencia ordenada de puntos"""
    if len(orden) < 2:
        return []
    # Cerrar el ciclo: A → B → ... → A
    coords = ";".join([f"{clientes[i][1]},{clientes[i][0]}" for i in orden + [orden[0]]])
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=false"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OPTIRUTA+"})
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read())
        pts = data["routes"][0]["geometry"]["coordinates"]
        return [[p[1], p[0]] for p in pts]  # [lat, lng] para Leaflet
    except:
        return []  # fallback a linea recta en el frontend

def _distancia_aerea(coord1, coord2):
    R = 6371
    dLat = (coord2[0] - coord1[0]) * math.pi / 180
    dLng = (coord2[1] - coord1[1]) * math.pi / 180
    a = (math.sin(dLat/2)**2 +
         math.cos(coord1[0]*math.pi/180) * math.cos(coord2[0]*math.pi/180) * math.sin(dLng/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ============================================================
# ALGORITMOS
# ============================================================
def voraz(clientes):
    n = len(clientes)
    visitados = [False] * n
    ruta = [0]
    visitados[0] = True
    total = 0
    actual = 0
    for _ in range(n - 1):
        mejor = -1
        mejor_d = float('inf')
        for i in range(n):
            if not visitados[i]:
                d = distancia_terrestre(clientes[actual], clientes[i])
                if d < mejor_d:
                    mejor_d = d
                    mejor = i
        ruta.append(mejor)
        total += mejor_d
        visitados[mejor] = True
        actual = mejor
    total += distancia_terrestre(clientes[actual], clientes[0])
    return ruta, round(total, 2)


def backtracking(clientes):
    n = len(clientes)
    mat = [[distancia_terrestre(clientes[i], clientes[j]) for j in range(n)] for i in range(n)]
    mejor_dist = float('inf')
    mejor_ruta = None
    ramas = 0
    def bt(actual, vis, d_act, ruta):
        nonlocal mejor_dist, mejor_ruta, ramas
        if d_act >= mejor_dist:
            return
        if len(ruta) == n:
            d_total = d_act + mat[actual][0]
            ramas += 1
            if d_total < mejor_dist:
                mejor_dist = d_total
                mejor_ruta = ruta[:]
            return
        for i in range(n):
            if not vis[i]:
                vis[i] = True
                ruta.append(i)
                bt(i, vis, d_act + mat[actual][i], ruta)
                ruta.pop()
                vis[i] = False
    vis = [False] * n
    vis[0] = True
    bt(0, vis, 0, [0])
    total_posible = math.factorial(n - 1) if n > 1 else 1
    return mejor_ruta or [], round(mejor_dist, 2) if mejor_ruta else 0, ramas, total_posible


def mochila(transporte):
    """MOCHILA 2D: maximiza valor segun peso max y largo max del transporte"""
    info = TRANSPORTES[transporte]
    peso_max = info["peso_max"]
    largo_max = info["largo_max"]

    # Generar todos los items posibles (cada unidad de cada paquete)
    items = []
    for p in PAQUETES:
        nombre, largo, peso, cantidad, valor = p
        for _ in range(cantidad):
            items.append((nombre, largo, peso, valor))

    n = len(items)
    # DP 2D: [n+1][peso+1][largo+1]
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

    return {
        "valor_maximo": dp[n][peso_max][largo_max],
        "seleccionados": seleccionados,
        "peso_usado": peso_max - w,
        "largo_usado": largo_max - l,
    }


# ============================================================
# SERVIDOR HTTP
# ============================================================
class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/mapa_ibague.html"
        try:
            with open("mapa_ibague.html", "rb") as f:
                self.send_response(200)
                if self.path.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f.read())
        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404")

    def do_POST(self):
        if self.path == "/api/ejecutar":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            clientes = body["clientes"]
            transporte = body.get("transporte", "carro")

            resultado = {
                "clientes": clientes,
                "transporte": TRANSPORTES[transporte],
                "transporte_id": transporte,
                "paquetes": [{"nombre": p[0], "largo": p[1], "peso": p[2],
                              "cantidad": p[3], "valor": p[4]} for p in PAQUETES],
            }

            # Mochila
            resultado["mochila"] = mochila(transporte)

            # Voraz
            ruta_v, dist_v = voraz(clientes)
            resultado["voraz"] = {
                "ruta": ruta_v, "distancia": dist_v,
                "geometria": geometria_ruta_osrm(clientes, ruta_v)
            }

            # Backtracking (max 10)
            if len(clientes) <= 10:
                ruta_bt, dist_bt, ramas, total = backtracking(clientes)
                mejora = round(((dist_v - dist_bt) / dist_v) * 100, 1) if dist_v else 0
                ahorro = round((1 - ramas / total) * 100, 1)
                resultado["backtracking"] = {
                    "ruta": ruta_bt, "distancia": dist_bt,
                    "ramas": ramas, "total": total, "ahorro": ahorro,
                    "geometria": geometria_ruta_osrm(clientes, ruta_bt)
                }
                if dist_v:
                    resultado["mejora"] = mejora
            else:
                resultado["backtracking"] = None
                resultado["mejora"] = 0

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resultado, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"  [{args[0]}] {args[1]} {args[2]}")


print("=" * 55)
print(" OPTIRUTA+ - Servidor de Rutas Terrestres")
print("=" * 55)
print(" Abre: http://localhost:8000")
print(" Usa OSRM para distancias reales por carretera")
print(" Transportes: Moto, Carro, Camion")
print("-" * 55)
print(" Ctrl+C para detener")
print("=" * 55)
HTTPServer(("", 8000), Servidor).serve_forever()
