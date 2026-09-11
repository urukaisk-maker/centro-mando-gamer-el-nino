import os
base = "/run/media/urukais/PROYECTOS1/01_EL_NINO_LAUNCHER"
path = os.path.join(base, "index.html")
with open(path) as f: c = f.read()
if "launch/dolphin" not in c:
    nueva = """<a href="http://localhost:8080/launch/dolphin" class="card">\n<span class="badge">Emulador</span>\n<h3>🏰 Dolphin (GC/Wii)</h3>\n<p>Emulador de GameCube y Wii</p>\n</a>\n"""
    c = c.replace("<footer>", nueva + "\n<footer>", 1)
with open(path, "w") as f: f.write(c)
