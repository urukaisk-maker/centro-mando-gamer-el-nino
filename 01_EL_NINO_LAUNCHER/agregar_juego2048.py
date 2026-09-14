import os
base = "/run/media/urukais/PROYECTOS1/01_EL_NINO_LAUNCHER"
path = os.path.join(base, "index.html")
with open(path) as f: c = f.read()
nueva = """<a href="http://localhost:8080/01_EL_NINO_LAUNCHER/juego2048.html" class="card">\n<span class="badge">Juego</span>\n<h3>🎮 2048 (HTML)</h3>\n<p>Juega directamente en el navegador</p>\n</a>\n"""
if "juego2048.html" not in c:
    c = c.replace("<footer>", nueva + "\n<footer>", 1)
with open(path, "w") as f: f.write(c)
