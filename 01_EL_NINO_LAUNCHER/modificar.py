import os
base = "/run/media/urukais/PROYECTOS1/01_EL_NINO_LAUNCHER"
path = os.path.join(base, "index.html")
with open(path) as f: c = f.read()
c = c.replace("href=\"http://localhost:8080/02_EMULADORES_Y_ROMS/\"", "href=\"http://localhost:8080/launch/pcsx2\"")
c = c.replace("Emuladores y Retro", "PCSX2 (PS2) - Lanzar")
c = c.replace("<p>PS2, PSP, GameCube, Wii, GBA y Arcade MAME listos para jugar.</p>", "<p>Lanzar emulador de PlayStation 2</p>")
with open(path, "w") as f: f.write(c)
