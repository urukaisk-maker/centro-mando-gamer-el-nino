#!/usr/bin/env python3
import signal
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
def validar_config(config):
    """Valida el config y devuelve lista de errores."""
    errores = []
    if "servidor" not in config:
        errores.append("falta seccion 'servidor'")
        return errores
    srv = config["servidor"]
    if not isinstance(srv.get("puerto"), int):
        errores.append("puerto debe ser un numero")
    elif srv["puerto"] < 1024 or srv["puerto"] > 65535:
        errores.append("puerto debe estar entre 1024 y 65535")
    if not isinstance(srv.get("host"), str):
        errores.append("host debe ser texto")
    for seccion in ["rutas", "scripts"]:
        if seccion not in config:
            errores.append("falta seccion '" + seccion + "'")
    return errores

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
        # Validar
        errores = validar_config(CONFIG)
        if errores:
            print("AVISO: config.json tiene problemas, usando valores por defecto:")
            for e in errores:
                print("  - " + e)
            # Resetear a valores por defecto
            CONFIG["servidor"]["puerto"] = 8080
            CONFIG["servidor"]["host"] = "0.0.0.0"
    except Exception as e:
        print("AVISO: no se pudo leer config.json: " + str(e))
        print("  Usando configuracion por defecto.")

def encontrar_puerto_libre(puerto_inicial, max_intentos=10):
    """Busca un puerto libre empezando por puerto_inicial."""
    import socket
    for offset in range(max_intentos):
        puerto = puerto_inicial + offset
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((CONFIG["servidor"]["host"], puerto))
            s.close()
            return puerto
        except OSError:
            continue
    return puerto_inicial  # Fallback

PUERTO_CONFIG = CONFIG["servidor"]["puerto"]
PORT = encontrar_puerto_libre(PUERTO_CONFIG)
if PORT != PUERTO_CONFIG:
    print("AVISO: puerto " + str(PUERTO_CONFIG) + " ocupado, usando " + str(PORT))
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
    def lanzar_appimage(self, rom):
        """Lanza un AppImage (emulador o juego)."""
        ruta = rom["ruta"]
        if not os.path.exists(ruta):
            self.not_found("AppImage no encontrado: " + ruta)
            return
        try:
            os.chmod(ruta, 0o755)
        except Exception:
            pass
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        try:
            proc = subprocess.Popen(
                [ruta],
                cwd=os.path.dirname(ruta),
                env=env,
                stdout=open("/tmp/elnino_lanzar.log","ab"),
                stderr=open("/tmp/elnino_lanzar.log","ab"),
                start_new_session=True
            )
        except Exception as e:
            self.not_found("Error al lanzar: " + str(e))
            return
        with lock:
            procesos_activos["app_" + rom["nombre"]] = {
                "pid": proc.pid, "proceso": proc,
                "hora": time.time(), "tipo": rom.get("tipo", "juego")
            }
        self.redirect("app_" + rom["nombre"])

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

        elif self.path.startswith("/juego-win/"):
            juego = self.path.split("/juego-win/")[1].strip("/")
            # Buscar en la carpeta windows/ el .bat correspondiente
            base_win = os.path.join(DIRECTORY, "08_JUEGOS_EXTRA", "windows")
            bat = os.path.join(base_win, juego + ".bat")
            if os.path.exists(bat):
                # En Windows usar cmd, en otros SO no funciona
                try:
                    subprocess.Popen(["cmd", "/c", bat], cwd=base_win)
                    self.redirect(juego)
                except FileNotFoundError:
                    # Si no hay cmd (Linux), devolver aviso
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    html = "<html><body style='background:#0a0a0f;color:#ff00ff;font-family:sans-serif;padding:3rem;text-align:center'><h1>Requiere Windows</h1><p>Este juego solo esta disponible en Windows.</p><a href='/01_EL_NINO_LAUNCHER/index.html' style='color:#00f0ff'>Volver</a></body></html>"
                    self.wfile.write(html.encode())
            else:
                self.not_found("Lanzador Windows no encontrado")

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
                self.lanzar_appimage(rom)

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

        elif self.path.startswith("/modo-fiesta"):
            script = os.path.join(DIRECTORY, "modo_fiesta.sh")
            if os.path.exists(script):
                try:
                    # No esperamos la salida porque cierra el navegador
                    subprocess.Popen(["bash", script])
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Modo fiesta activado")
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script no encontrado")

        elif self.path.startswith("/modo-cine"):
            script = os.path.join(DIRECTORY, "modo_cine.sh")
            if os.path.exists(script):
                try:
                    subprocess.Popen(["bash", script])
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Modo cine activado")
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.not_found("Script no encontrado")

        elif self.path.startswith("/espacio"):
            try:
                import subprocess as sp
                # Ejecutar du para saber el tamaño de cada carpeta
                base = DIRECTORY
                carpetas = {
                    "Juegos PC": "08_JUEGOS_EXTRA",
                    "Emuladores y ROMs": "02_EMULADORES_Y_ROMS",
                    "Streaming": "03_STREAMING_Y_CLIPS",
                    "Mods": "04_MODS_Y_SHADERS",
                    "Herramientas": "05_HERRAMIENTAS_GAMER",
                    "Media y Wallpapers": "06_MEDIA_Y_WALLPAPERS",
                    "Diario": "07_DIARIO_MARIO",
                    "Launcher": "01_EL_NINO_LAUNCHER",
                    "Python portable": "python_portable",
                }
                resultado = []
                for nombre, carpeta in carpetas.items():
                    ruta = os.path.join(base, carpeta)
                    if os.path.isdir(ruta):
                        try:
                            r = sp.run(["du", "-sm", ruta], capture_output=True, text=True, timeout=30)
                            if r.stdout:
                                mb = int(r.stdout.split()[0])
                                resultado.append({"nombre": nombre, "mb": mb})
                        except Exception:
                            pass
                # Tamano total del disco
                try:
                    r = sp.run(["df", "-m", base], capture_output=True, text=True)
                    lineas = r.stdout.strip().split("\n")
                    if len(lineas) >= 2:
                        partes = lineas[1].split()
                        total_mb = int(partes[1])
                        usado_mb = int(partes[2])
                        libre_mb = int(partes[3])
                    else:
                        total_mb = usado_mb = libre_mb = 0
                except Exception:
                    total_mb = usado_mb = libre_mb = 0

                datos = {
                    "carpetas": resultado,
                    "total_mb": total_mb,
                    "usado_mb": usado_mb,
                    "libre_mb": libre_mb,
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(datos).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path.startswith("/plataforma"):
            import platform as plat
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "so": plat.system(),
                "es_windows": plat.system() == "Windows",
                "es_linux": plat.system() == "Linux",
                "es_mac": plat.system() == "Darwin"
            }).encode())

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
                        # CPU del propio servidor Python
                        try:
                            proceso_actual = psutil.Process()
                            datos["cpu_server"] = round(proceso_actual.cpu_percent(interval=None), 1)
                            datos["ram_server_mb"] = round(proceso_actual.memory_info().rss / 1024 / 1024, 1)
                        except:
                            datos["cpu_server"] = 0
                            datos["ram_server_mb"] = 0
                    payload = "data: " + json.dumps(datos) + chr(10) + chr(10)

                    self.wfile.write(payload.encode())
                    self.wfile.flush()
                    time.sleep(3)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception:
                pass

        elif self.path.startswith("/timeline-escanear"):
            script = os.path.join(DIRECTORY, "timeline_saves.py")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["python3", script], capture_output=True, text=True, timeout=60)
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
                self.not_found("Script de timeline no encontrado")

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

    def do_POST(self):
        if self.path.startswith("/trailers-guardar"):
            try:
                longitud = int(self.headers.get('Content-Length', 0))
                cuerpo = self.rfile.read(longitud).decode('utf-8')
                datos = json.loads(cuerpo)
                destino = os.path.join(DIRECTORY, "01_EL_NINO_LAUNCHER", "trailers.json")
                with open(destino, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

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

# ===== DETECCION AUTOMATICA DE ENTORNO GRAFICO =====
def detectar_entorno_grafico():
    """Detecta si estamos en X11 o Wayland y configura las variables."""
    import subprocess as sp
    # Si ya hay WAYLAND_DISPLAY, estamos en Wayland
    if os.environ.get("WAYLAND_DISPLAY"):
        return
    # Si hay DISPLAY, X11
    if os.environ.get("DISPLAY"):
        return
    # Auto-detectar
    try:
        # Buscar el display de X11
        r = sp.run(["bash", "-c", "ls /tmp/.X11-unix/ 2>/dev/null"], capture_output=True, text=True)
        if r.stdout.strip():
            display = ":" + r.stdout.strip()[0]
            os.environ["DISPLAY"] = display
            print("DISPLAY auto-detectado: " + display)
    except:
        pass
    try:
        # Buscar WAYLAND_DISPLAY del usuario
        uid = os.getuid()
        r = sp.run(["bash", "-c", "ls /run/user/" + str(uid) + "/wayland-* 2>/dev/null | head -1"], capture_output=True, text=True)
        if r.stdout.strip():
            wayland = os.path.basename(r.stdout.strip())
            os.environ["WAYLAND_DISPLAY"] = wayland
            os.environ["XDG_RUNTIME_DIR"] = "/run/user/" + str(uid)
            print("WAYLAND_DISPLAY auto-detectado: " + wayland)
    except:
        pass

detectar_entorno_grafico()

import signal

def cierre_limpio(signum, frame):
    """Cierra el servidor de forma limpia."""
    print("")
    print("Cerrando servidor El Nino...")
    # Matar procesos hijos (juegos/emuladores abiertos)
    with lock:
        for nombre, info in list(procesos_activos.items()):
            try:
                info["proceso"].terminate()
                print("  Cerrado: " + nombre)
            except:
                pass
    print("Servidor cerrado correctamente.")
    import sys
    sys.exit(0)

signal.signal(signal.SIGTERM, cierre_limpio)
signal.signal(signal.SIGINT, cierre_limpio)

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
