#!/usr/bin/env python3
import http.server, socketserver, subprocess, os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/launch/"):
            emulator = self.path.split("/launch/")[1].strip("/")
            base = os.path.join(DIRECTORY, "02_EMULADORES_Y_ROMS", "EJECUTABLES_PORTABLES")
            sh = os.path.join(base, f"{emulator}.sh")
            bat = os.path.join(base, f"{emulator}.bat")
            if os.path.exists(sh):
                subprocess.Popen(["bash", sh])
                self.redirect(emulator)
            elif os.path.exists(bat):
                subprocess.Popen(["cmd", "/c", bat])
                self.redirect(emulator)
            else:
                self.not_found("Emulador no encontrado")
        elif self.path.startswith("/juego/"):
            juego = self.path.split("/juego/")[1].strip("/")
            base = os.path.join(DIRECTORY, "08_JUEGOS_EXTRA")
            sh = os.path.join(base, f"{juego}.sh")
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

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Servidor en http://localhost:{PORT}")
        httpd.serve_forever()
