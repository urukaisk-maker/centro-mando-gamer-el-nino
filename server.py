#!/usr/bin/env python3
import http.server, socketserver, subprocess, os, glob

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

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
            base = os.path.join(DIRECTORY, "02_EMULADORES_Y_ROMS", "EJECUTABLES_PORTABLES")
            sh = os.path.join(base, emulador + ".sh")
            bat = os.path.join(base, emulador + ".bat")
            if os.path.exists(sh):
                subprocess.Popen(["bash", sh])
                self.redirect(emulador)
            elif os.path.exists(bat):
                subprocess.Popen(["cmd", "/c", bat])
                self.redirect(emulador)
            else:
                self.not_found("Emulador no encontrado")

        elif self.path.startswith("/backup"):
            script = os.path.join(DIRECTORY, "Backup_Partidas.sh")
            if os.path.exists(script):
                try:
                    resultado = subprocess.run(["bash", script], capture_output=True, text=True, timeout=60, input="\n")
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

        elif self.path.startswith("/juego/"):
            juego = self.path.split("/juego/")[1].strip("/")
            base = os.path.join(DIRECTORY, "08_JUEGOS_EXTRA")
            sh = os.path.join(base, juego + ".sh")
            if os.path.exists(sh):
                subprocess.Popen(["bash", sh])
                self.redirect(juego)
            else:
                self.not_found("Juego no encontrado")
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
    with ServidorConcurrente(("", PORT), Handler) as httpd:
        print("Servidor en http://localhost:" + str(PORT))
        httpd.serve_forever()
