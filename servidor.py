"""
OPTIRUTA+ - Servidor local
Ejecuta: python servidor.py
Luego abre: http://localhost:8000
"""

import math
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================
# ALGORITMOS
# ============================================================
def distancia(coord1, coord2):
    R = 6371
    dLat = (coord2[0] - coord1[0]) * math.pi / 180
    dLng = (coord2[1] - coord1[1]) * math.pi / 180
    a = math.sin(dLat/2)**2 + math.cos(coord1[0]*math.pi/180) * math.cos(coord2[0]*math.pi/180) * math.sin(dLng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

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
                d = distancia(clientes[actual], clientes[i])
                if d < mejor_d:
                    mejor_d = d
                    mejor = i
        ruta.append(mejor)
        total += mejor_d
        visitados[mejor] = True
        actual = mejor
    total += distancia(clientes[actual], clientes[0])
    return ruta, round(total, 2)

def backtracking(clientes):
    n = len(clientes)
    mat = [[distancia(clientes[i], clientes[j]) for j in range(n)] for i in range(n)]
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
            self.wfile.write(b"404 - Archivo no encontrado")

    def do_POST(self):
        if self.path == "/api/ejecutar":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            clientes = body["clientes"]

            resultado = {"clientes": clientes}

            # Voraz
            ruta_v, dist_v = voraz(clientes)
            resultado["voraz"] = {"ruta": ruta_v, "distancia": dist_v}

            # Backtracking (solo si <= 10)
            if len(clientes) <= 10:
                ruta_bt, dist_bt, ramas, total = backtracking(clientes)
                mejora = round(((dist_v - dist_bt) / dist_v) * 100, 1) if dist_v else 0
                ahorro = round((1 - ramas / total) * 100, 1)
                resultado["backtracking"] = {
                    "ruta": ruta_bt,
                    "distancia": dist_bt,
                    "ramas": ramas,
                    "total": total,
                    "ahorro": ahorro
                }
                if dist_v:
                    resultado["mejora"] = mejora
            else:
                resultado["backtracking"] = None
                resultado["mejora"] = 0

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resultado, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"  [{args[0]}] {args[1]} {args[2]}")


print("=" * 50)
print(" OPTIRUTA+ - Servidor iniciado")
print("=" * 50)
print(" Abre tu navegador en:")
print("   http://localhost:8000")
print("-" * 50)
print(" Presiona Ctrl+C para detener")
print("=" * 50)
HTTPServer(("", 8000), Servidor).serve_forever()
