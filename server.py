#!/usr/bin/env python3
import http.server, socketserver, subprocess, os, glob, json, socket, time, threading, urllib.parse

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# ===== CARGAR CONFIGURACION =====
CONFIG_PATH = os.path.join(DIRECTORY, "config.json")
CONFIG = {
    "servidor": {"puerto": 8080, "host": "0.0.0.0", "modo_debug": False,
                 "timeout_backup": 60, "timeout_escaner": 120, "timeout_mandos": 60},
    "rutas": {
        "launcher": "01_EL_NINO_LAUNCHER",
        "emuladores_portables": "02_EMULADORES_Y_ROMS/EJECUTABLES_PORTABLES",
        "juegos_extra": "08_JUEGOS_EXTRA",
        "catalogo_roms": "01_EL_NINO_LAUNCHER/juegos.json"
    },
    "scripts": {
        "backup": "Backup_Partidas.sh",
        "limpiar": "limpiar_cache.sh",
        "escanear": "escanear_roms.py",
        "instalar_mandos": "05_HERRAMIENTAS_GAMER/instalar_mandos.sh"
    }
}
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cargado = json.load(f)
            # Fusionar (sin sobreescribir claves no presentes)
            for seccion, valores in cargado.items():
                if seccion in CONFIG and isinstance(valores, dict):
                    CONFIG[seccion].update(valores)
                else:
                    CONFIG[seccion] = valores
    except Exception as e:
        print("AVISO: no se pudo leer config.json: " + str(e))

PORT = CONFIG["servidor"]["puerto"]
HOST = CONFIG["servidor"]["host"]
DEBUG = CONFIG["servidor"]["modo_debug"]
TIMEOUT_BACKUP = CONFIG["servidor"]["timeout_backup"]
TIMEOUT_ESCANER = CONFIG["servidor"]["timeout_escaner"]
TIMEOUT_MANDOS = CONFIG["servidor"]["timeout_mandos"]

RUTA_LAUNCHER = CONFIG["rutas"]["launcher"]
RUTA_EMU_PORTABLES = CONFIG["rutas"]["emuladores_portables"]
RUTA_JUEGOS_EXTRA = CONFIG["rutas"]["juegos_extra"]
RUTA_CATALOGO = CONFIG["rutas"]["catalogo_roms"]

SCRIPT_BACKUP = CONFIG["scripts"]["backup"]
SCRIPT_LIMPIAR = CONFIG["scripts"]["limpiar"]
SCRIPT_ESCANEAR = CONFIG["scripts"]["escanear"]
SCRIPT_MANDOS = CONFIG["scripts"]["instalar_mandos"]

# ===== REGISTRO DE PROCESOS ACTIVOS =====
procesos_activos = {}
lock = threading.Lock()


MAPEO_EMULADOR = {
    "ps2": {"core": None, "emu": "pcsx2"},
    "psp": {"core": None, "emu": "ppsspp"},
    "gamecube_wii": {"core": None, "emu": "dolphin"},
    "gba_snes": {"core": "mgba", "emu": "retroarch"},
    "arcade": {"core": "fceumm", "emu": "retroarch"}
}

REQUISITOS = {
    "pcsx2": {
        "bios": "02_EMULADORES_Y_ROMS/01_PS2/BIOS",
        "roms": "02_EMULADORES_Y_ROMS/01_PS2",
        "ext_roms": [".iso", ".bin", ".chd", ".elf"],
        "nombre": "PCSX2 (PlayStation 2)"
    },
    "dolphin": {
        "bios": "02_EMULADORES_Y_ROMS/03_GAMECUBE_WII",
        "roms": "02_EMULADORES_Y_ROMS/03_GAMECUBE_WII",
        "ext_roms": [".iso", ".gcm", ".wbfs", ".rvz"],
        "nombre": "Dolphin (GameCube/Wii)"
    },
    "ppsspp": {
        "roms": "02_EMULADORES_Y_ROMS/02_PSP",
        "ext_roms": [".iso", ".cso", ".pbp"],
        "nombre": "PPSSPP (PlayStation Portable)"
    },
    "retroarch": {
        "roms": "02_EMULADORES_Y_ROMS",
        "ext_roms": [".nes", ".snes", ".sfc", ".gba", ".gb", ".gbc", ".md", ".zip"],
        "nombre": "RetroArch"
    }
}

def verificar_emulador(nombre):
    if nombre not in REQUISITOS:
        return True, None
    regla = REQUISITOS[nombre]
    faltas = []
    if "bios" in regla:
        ruta_bios = os.path.join(DIRECTORY, regla["bios"])
        if not os.path.isdir(ruta_bios) or not os.listdir(ruta_bios):
            faltas.append("Falta la BIOS en: <code>" + regla["bios"] + "/</code>")
    if "roms" in regla and "ext_roms" in regla:
        ruta_roms = os.path.join(DIRECTORY, regla["roms"])
        encontrados = []
        if os.path.isdir(ruta_roms):
            for ext in regla["ext_roms"]:
                encontrados += glob.glob(os.path.join(ruta_roms, "**/*" + ext), recursive=True)
        if not encontrados:
            faltas.append("No hay juegos (ROMs/ISOs) en: <code>" + regla["roms"] + "/</code>")
    if faltas:
        return False, faltas
    return True, None

def pagina_aviso(nombre, faltas):
    items = "".join("<li>" + f + "</li>" for f in faltas)
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>Aviso - """ + nombre + """</title>
<style>
body{font-family:'Segoe UI',sans-serif;background:#0a0a0f;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:2rem}
.box{max-width:600px;background:#1a1a24;border:2px solid #ff00ff;border-radius:20px;padding:2.5rem;box-shadow:0 0 40px rgba(255,0,255,0.4);text-align:center}
h1{color:#ff00ff;margin:0 0 1rem;text-shadow:0 0 20px #ff00ff}
p{color:#d0d0e0;line-height:1.7;text-align:left}
ul{color:#00f0ff;text-align:left;line-height:1.8;padding-left:1.5rem}
code{background:#0a0a0f;padding:0.2rem 0.5rem;border-radius:4px;color:#00f0ff;font-size:0.9rem}
a{display:inline-block;margin-top:2rem;padding:0.8rem 2rem;background:linear-gradient(45deg,#00f0ff,#ff00ff);color:#000;text-decoration:none;border-radius:30px;font-weight:bold}
a:hover{transform:scale(1.05)}
</style></head><body>
<div class="box">
<h1>Falta contenido</h1>
<p>Para lanzar <strong>""" + nombre + """</strong> necesitas anadir lo siguiente:</p>
<ul>""" + items + """</ul>
<p style="margin-top:1.5rem;font-size:0.9rem;color:#8899aa">
Cuando lo tengas, vuelve al launcher y prueba de nuevo.
</p>
<a href="/01_EL_NINO_LAUNCHER/index.html">Volver al Centro de Mando</a>
</div>
</body></html>"""

def get_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def limpiar_procesos():
    with lock:
        terminados = []
        for n, d in list(procesos_activos.items()):
            if d["proceso"].poll() is not None:
                terminados.append(n)
        for n in terminados:
            del procesos_activos[n]

def lanzar_proceso(nombre, script_path, tipo):
    proc = subprocess.Popen(["bash", script_path])
    with lock:
        procesos_activos[nombre] = {
            "pid": proc.pid,
            "proceso": proc,
            "hora": time.time(),
            "tipo": tipo
        }
    return proc

def matar_proceso(nombre):
    with lock:
        if nombre not in procesos_activos:
            return False, "No esta corriendo"
        info = procesos_activos[nombre]
        try:
            info["proceso"].terminate()
            try:
                info["proceso"].wait(timeout=3)
            except subprocess.TimeoutExpired:
                info["proceso"].kill()
            del procesos_activos[nombre]
            return True, "Cerrado correctamente"
        except Exception as e:
            return False, str(e)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/launch/"):
            emulador = self.path.split("/launch/")[1].strip("/")
            ok, faltas = verificar_emulador(emulador)
            if not ok:
                nombre = REQUISITOS[emulador]["nombre"]
                html = pagina_aviso(nombre, faltas)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode())
                return
            base = os.path.join(DIRECTORY, RUTA_EMU_PORTABLES)
            sh = os.path.join(base, emulador + ".sh")
            bat = os.path.join(base, emulador + ".bat")
            if os.path.exists(sh):
                lanzar_proceso(emulador, sh, "emulador")
                self.redirect(emulador)
            elif os.path.exists(bat):
                lanzar_proceso(emulador, bat, "emulador")
                self.redirect(emulador)
            else:
                self.not_found("Emulador no encontrado")

        elif self.path.startswith("/juego/"):
            juego = self.path.split("/juego/")[1].strip("/")
            base = os.path.join(DIRECTORY, RUTA_JUEGOS_EXTRA)
            sh = os.path.join(base, juego + ".sh")
            if os.path.exists(sh):
                lanzar_proceso(juego, sh, "juego")
                self.redirect(juego)
            else:
                self.not_found("Juego no encontrado")

        elif self.path.startswith("/kill/"):
            nombre = self.path.split("/kill/")[1].strip("/")
            ok, msg = matar_proceso(nombre)
            self.send_response(200 if ok else 404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": ok, "mensaje": msg}).encode())

        elif self.path.startswith("/estado"):
            limpiar_procesos()
            with lock:
                activos = []
                ahora = time.time()
                for n, d in procesos_activos.items():
                    activos.append({
                        "nombre": n,
                        "pid": d["pid"],
                        "tipo": d["tipo"],
                        "segundos": int(ahora - d["hora"])
                    })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"activos": activos}).encode())

        elif self.path.startswith("/rom/"):
            partes = self.path.split("/rom/")[1].strip("/").split("/", 1)
            if len(partes) < 2:
                self.not_found("Falta el archivo")
                return
            sistema = urllib.parse.unquote(partes[0])
            archivo = urllib.parse.unquote(partes[1])
            # Buscar la ROM en el JSON
            json_path = os.path.join(DIRECTORY, RUTA_CATALOGO)
            if not os.path.exists(json_path):
                self.not_found("No hay catalogo de ROMs")
                return
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            rom = None
            for j in data["juegos"]:
                if j["sistema"] == sistema and j["archivo"] == archivo:
                    rom = j
                    break
            if not rom:
                self.not_found("ROM no encontrada")
                return
            # Lanzar con RetroArch y el core adecuado
            if rom["emulador"] == "retroarch":
                core_nombre = MAPEO_EMULADOR.get(sistema, {}).get("core", "mgba")
                core_path = os.path.expanduser("~/.config/retroarch/cores/" + core_nombre + "_libretro.so")
                if not os.path.exists(core_path):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    html = "<html><body style='background:#0a0a0f;color:#ff00ff;font-family:sans-serif;padding:3rem;text-align:center'><h1>Falta el core</h1><p>Necesitas el core <code>" + core_nombre + "_libretro.so</code></p><p>Descargalo con:</p><pre style='background:#1a1a24;padding:1rem;border-radius:8px;color:#00f0ff'>cd ~/.config/retroarch/cores/<br>wget https://buildbot.libretro.com/nightly/linux/x86_64/latest/" + core_nombre + "_libretro.so.zip<br>unzip " + core_nombre + "_libretro.so.zip</pre><a href='/01_EL_NINO_LAUNCHER/index.html' style='color:#00f0ff'>Volver</a></body></html>"
                    self.wfile.write(html.encode())
                    return
                proc = subprocess.Popen(["retroarch", "-L", core_path, rom["ruta"]])
                with lock:
                    procesos_activos["rom_" + rom["nombre"]] = {
                        "pid": proc.pid, "proceso": proc,
                        "hora": time.time(), "tipo": "juego"
                    }
                self.redirect("rom_" + rom["nombre"])
            else:
                # Para emuladores pesados, sin core especifico (por ahora)
                self.not_found("Este sistema necesita configuracion manual")

        elif self.path.startswith("/tecla/"):
            # Enviar una tecla al PC (press + release)
            tecla = urllib.parse.unquote(self.path.split("/tecla/")[1].strip("/"))
            try:
                subprocess.Popen(["xdotool", "key", tecla])
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path.startswith("/tecla-down/"):
            tecla = urllib.parse.unquote(self.path.split("/tecla-down/")[1].strip("/"))
            try:
                subprocess.Popen(["xdotool", "keydown", tecla])
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path.startswith("/tecla-up/"):
            tecla = urllib.parse.unquote(self.path.split("/tecla-up/")[1].strip("/"))
            try:
                subprocess.Popen(["xdotool", "keyup", tecla])
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path.startswith("/eventos"):
            # Server-Sent Events: stream continuo de estado
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                import psutil
                TIENE_PSUTIL = True
            except ImportError:
                TIENE_PSUTIL = False
            try:
                while True:
                    limpiar_procesos()
                    with lock:
                        activos = []
                        ahora = time.time()
                        for n, d in procesos_activos.items():
                            activos.append({
                                "nombre": n,
                                "pid": d["pid"],
                                "tipo": d["tipo"],
                                "segundos": int(ahora - d["hora"])
                            })
                    datos = {"activos": activos, "tiempo": int(time.time())}
                    if TIENE_PSUTIL:
                        datos["cpu"] = psutil.cpu_percent(interval=None)
                        datos["ram"] = psutil.virtual_memory().percent
                        datos["ram_libre_gb"] = round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 1)
                    payload = "data: " + json.dumps(datos) + chr(10) + chr(10)

                    self.wfile.write(payload.encode())
                    self.wfile.flush()
                    time.sleep(3)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception:
                pass

        elif self.path.startswith("/comprimir-roms"):
            script = os.path.join(DIRECTORY, "comprimir_roms.sh")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=600, input="")
                    salida = resultado.stdout or "Compresion completada"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script no encontrado")

        elif self.path.startswith("/benchmark"):
            script = os.path.join(DIRECTORY, "benchmark.py")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["python3", script], capture_output=True, text=True, timeout=30)
                    salida = resultado.stdout or "Benchmark completado"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script de benchmark no encontrado")

        elif self.path.startswith("/guardar-configs"):
            script = os.path.join(DIRECTORY, "guardar_configs.sh")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=60, input="")
                    salida = resultado.stdout or "Configs guardadas"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script no encontrado")

        elif self.path.startswith("/restaurar-configs"):
            script = os.path.join(DIRECTORY, "restaurar_configs.sh")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=60, input="")
                    salida = resultado.stdout or "Configs restauradas"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script no encontrado")

        elif self.path.startswith("/escanear-roms"):
            script = os.path.join(DIRECTORY, SCRIPT_ESCANEAR)
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["python3", script], capture_output=True, text=True, timeout=TIMEOUT_MANDOS)
                    salida = resultado.stdout or "Escaneo completado"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script de escaneo no encontrado")
        elif self.path.startswith("/instalar-mandos"):
            script = os.path.join(DIRECTORY, SCRIPT_MANDOS)
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=60, input="")
                    salida = resultado.stdout or "Mandos instalados"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script de instalacion no encontrado")
        elif self.path.startswith("/limpiar"):
            script = os.path.join(DIRECTORY, SCRIPT_LIMPIAR)
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=TIMEOUT_ESCANER, input="")
                    salida = resultado.stdout or "Limpieza completada"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(salida.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script de limpieza no encontrado")
        elif self.path.startswith("/backup"):
            script = os.path.join(DIRECTORY, SCRIPT_BACKUP)
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=TIMEOUT_BACKUP, input="\n")
                    salida = resultado.stdout or "Backup completado"
                    lineas = [l for l in salida.split("\n") if "Pulsa Enter" not in l]
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("\n".join(lineas).encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script de backup no encontrado")

        else:
            super().do_GET()

    def redirect(self, name):
        self.send_response(302)
        self.send_header("Location", "/01_EL_NINO_LAUNCHER/index.html?launched=" + name)
        self.end_headers()

    def not_found(self, msg):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(msg.encode())

    def log_message(self, fmt, *args):
        pass

class ServidorConcurrente(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    ip = get_ip_local()
    with ServidorConcurrente((HOST, PORT), Handler) as httpd:
        print("=" * 50)
        print("  Servidor El Nino iniciado")
        print("=" * 50)
        print("  Local:   http://localhost:" + str(PORT))
        print("  Red:     http://" + ip + ":" + str(PORT))
        print("           (para movil/tablet en la misma WiFi)")
        print("=" * 50)
        httpd.serve_forever()
