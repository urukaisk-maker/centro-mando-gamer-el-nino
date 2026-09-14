import os
base = "/run/media/urukais/PROYECTOS1/01_EL_NINO_LAUNCHER"
path = os.path.join(base, "index.html")
with open(path) as f: c = f.read()
if "launch/retroarch" not in c:
    nueva = """<a href="http://localhost:8080/launch/retroarch" class="card">\n<span class="badge">Emulador</span>\n<h3>🕹️ RetroArch</h3>\n<p>Multi-emulador y cores</p>\n</a>\n"""
    # Insertar antes de la tarjeta del Diario (que tiene 07_DIARIO)
    marcador = "<a href=\"http://localhost:8080/07_DIARIO_MARIO/index.html\""
    if marcador in c:
        c = c.replace(marcador, nueva + marcador, 1)
    else:
        # Si no hay marcador, insertar antes del footer
        c = c.replace("<footer>", nueva + "\n<footer>", 1)
with open(path, "w") as f: f.write(c)
