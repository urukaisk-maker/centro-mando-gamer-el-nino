import os
base = "/run/media/urukais/PROYECTOS1/01_EL_NINO_LAUNCHER"
path = os.path.join(base, "index.html")
with open(path) as f: c = f.read()
if "launch/ppsspp" not in c:
    nueva = """<a href="http://localhost:8080/launch/ppsspp" class="card">\n<span class="badge">Emulador</span>\n<h3>🕹️ PPSSPP (PSP)</h3>\n<p>Emulador de PlayStation Portable</p>\n</a>\n"""
    c = c.replace("<footer>", nueva + "\n<footer>", 1)
with open(path, "w") as f: f.write(c)
