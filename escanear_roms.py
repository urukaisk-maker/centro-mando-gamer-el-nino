#!/usr/bin/env python3
# ==========================================
#  ESCANER DE ROMS Y JUEGOS - EL NINO (v3)
# ==========================================
import os, json, time

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ROMS_DIR   = os.path.join(DIRECTORIO, "02_EMULADORES_Y_ROMS")
JUEGOS_DIR = os.path.join(DIRECTORIO, "08_JUEGOS_EXTRA")
EMUS_DIR   = os.path.join(ROMS_DIR, "EJECUTABLES_PORTABLES")
SALIDA     = os.path.join(DIRECTORIO, "01_EL_NINO_LAUNCHER", "juegos.json")

CARPETAS_IGNORADAS = [
    "assets", "docs", "doc", "BIOS", "bios",
    "cores", "config", "configs", "shaders", "overlays",
    "thumbnails", "playlists", "saves", "states", "screenshots",
    "system", "info", "database", "cheats", "filters", "autoconfig",
    "input", "menu", "menu_drivers", "libretro", "dolphin-emu",
    "PCSX2", "PPSSPP", "wine", "squashfs-root", "python_portable",
    "windows",  # dentro de 08_JUEGOS_EXTRA, evita duplicar (contiene .exe)
    ".git", "node_modules", "__pycache__", "src", "source",
]

EXTENSIONES_IGNORADAS = [
    ".md", ".txt", ".html", ".htm", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".ico", ".ttf", ".otf", ".woff", ".json", ".xml", ".cfg",
    ".ini", ".conf", ".log", ".dll", ".so", ".exe", ".bat",
    ".py", ".js", ".css", ".pdf", ".doc", ".docx", ".nfo", ".sfv"
]

SISTEMAS = {
    "ps2":          {"carpeta": "01_PS2",        "ext": [".iso", ".bin", ".chd", ".elf", ".mdf"],
                     "nombre": "PlayStation 2",      "icono": "🎮", "color": "#0066ff", "emulador": "pcsx2"},
    "psp":          {"carpeta": "02_PSP",        "ext": [".iso", ".cso", ".pbp", ".chd"],
                     "nombre": "PlayStation Portable","icono": "🕹",  "color": "#00f0ff", "emulador": "ppsspp"},
    "gamecube_wii": {"carpeta": "03_GAMECUBE_WII","ext": [".iso", ".gcm", ".wbfs", ".rvz", ".dol"],
                     "nombre": "GameCube / Wii",     "icono": "🐬", "color": "#ff00ff", "emulador": "dolphin"},
    "gba_snes":     {"carpeta": "04_GBA_SNES",   "ext": [".gba", ".gb", ".gbc", ".snes", ".sfc", ".smc",
                                                         ".nes", ".md", ".gen", ".gg", ".sms", ".pce",
                                                         ".ngp", ".ws", ".wsc"],
                     "nombre": "GBA / SNES / NES",   "icono": "🔹", "color": "#00ff88", "emulador": "retroarch"},
    "arcade":       {"carpeta": "05_ARCADE_MAME", "ext": [".zip", ".7z", ".chd"],
                     "nombre": "Arcade MAME",        "icono": "👾", "color": "#ff8800", "emulador": "retroarch"},
}

# Emuladores portables: mapear nombres de archivo a info legible
EMULADORES_INFO = {
    "pcsx2":     {"nombre": "PCSX2",      "icono": "🎮", "color": "#0066ff", "sistema": "PlayStation 2"},
    "ppsspp":    {"nombre": "PPSSPP",     "icono": "🕹",  "color": "#00f0ff", "sistema": "PSP"},
    "dolphin":   {"nombre": "Dolphin",    "icono": "🐬", "color": "#ff00ff", "sistema": "GameCube / Wii"},
    "retroarch": {"nombre": "RetroArch",  "icono": "🔹", "color": "#00ff88", "sistema": "Multi-sistema"},
    "duckstation":{"nombre": "DuckStation","icono": "🦆", "color": "#ff8800", "sistema": "PS1"},
    "flycast":   {"nombre": "Flycast",    "icono": "🌐", "color": "#00ccff", "sistema": "Dreamcast"},
    "mgba":      {"nombre": "mGBA",       "icono": "🎯", "color": "#00ff88", "sistema": "GBA"},
    "melonds":   {"nombre": "melonDS",    "icono": "🍈", "color": "#ff6666", "sistema": "Nintendo DS"},
    "mesen":     {"nombre": "Mesen",      "icono": "⚡", "color": "#ffcc00", "sistema": "NES/SNES"},
}

def carpeta_ignorada(nombre):
    return nombre.lower() in [c.lower() for c in CARPETAS_IGNORADAS]

def es_archivo_valido(archivo, extensiones):
    ext = os.path.splitext(archivo)[1].lower()
    if ext in EXTENSIONES_IGNORADAS:
        return False
    if ext == ".zip":
        return ".zip" in extensiones
    return ext in extensiones

def limpiar_nombre(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    for marca in ["(USA)", "(Europe)", "(Japan)", "(Spain)", "(World)", "[!]",
                  "(En,Fr,De,Es,It)", "(U)", "(E)", "(J)"]:
        nombre = nombre.replace(marca, "")
    return nombre.strip(" -_") or nombre_archivo

def escanear_roms():
    juegos = []
    for sistema_id, sistema in SISTEMAS.items():
        carpeta = os.path.join(ROMS_DIR, sistema["carpeta"])
        if not os.path.isdir(carpeta):
            continue
        for raiz, dirs, archivos in os.walk(carpeta):
            dirs[:] = [d for d in dirs if not carpeta_ignorada(d)]
            if carpeta_ignorada(os.path.basename(raiz)):
                continue
            for archivo in archivos:
                if es_archivo_valido(archivo, sistema["ext"]):
                    ruta = os.path.join(raiz, archivo)
                    try:
                        tamano = os.path.getsize(ruta)
                    except:
                        tamano = 0
                    juegos.append({
                        "id": str(len(juegos)),
                        "tipo": "rom",
                        "nombre": limpiar_nombre(archivo),
                        "archivo": archivo,
                        "ruta": ruta,
                        "sistema": sistema_id,
                        "sistema_nombre": sistema["nombre"],
                        "icono": sistema["icono"],
                        "color": sistema["color"],
                        "emulador": sistema["emulador"],
                        "tamano_mb": round(tamano / (1024 * 1024), 1)
                    })
    return juegos

def escanear_juegos_extra():
    """AppImages y scripts .sh en 08_JUEGOS_EXTRA (raíz, no subcarpetas)."""
    juegos = []
    if not os.path.isdir(JUEGOS_DIR):
        return juegos
    for archivo in os.listdir(JUEGOS_DIR):
        ruta = os.path.join(JUEGOS_DIR, archivo)
        if not os.path.isfile(ruta):
            continue
        ext = os.path.splitext(archivo)[1].lower()
        if ext == ".appimage":
            try:
                tamano = os.path.getsize(ruta)
            except:
                tamano = 0
            juegos.append({
                "id": "juego_" + archivo,
                "tipo": "juego",
                "nombre": limpiar_nombre(archivo),
                "archivo": archivo,
                "ruta": ruta,
                "sistema": "extra",
                "sistema_nombre": "Juegos libres",
                "icono": "🎁",
                "color": "#ff00aa",
                "emulador": "",
                "tamano_mb": round(tamano / (1024 * 1024), 1)
            })
    return juegos

def escanear_emuladores():
    """AppImages en EJECUTABLES_PORTABLES que sean emuladores."""
    emus = []
    if not os.path.isdir(EMUS_DIR):
        return emus
    for archivo in os.listdir(EMUS_DIR):
        if not archivo.lower().endswith(".appimage"):
            continue
        ruta = os.path.join(EMUS_DIR, archivo)
        if not os.path.isfile(ruta):
            continue
        try:
            tamano = os.path.getsize(ruta)
        except:
            tamano = 0
        if tamano < 1024 * 1024:  # menos de 1MB = probablemente corrupto
            continue
        # Detectar por nombre
        nombre_lower = archivo.lower()
        info = None
        for clave, datos in EMULADORES_INFO.items():
            if clave in nombre_lower:
                info = datos
                break
        if not info:
            info = {"nombre": limpiar_nombre(archivo), "icono": "🕹",
                    "color": "#888888", "sistema": "Emulador"}
        emus.append({
            "id": "emu_" + archivo,
            "tipo": "emulador",
            "nombre": info["nombre"],
            "archivo": archivo,
            "ruta": ruta,
            "sistema": "emulador",
            "sistema_nombre": info["sistema"],
            "icono": info["icono"],
            "color": info["color"],
            "emulador": "",
            "tamano_mb": round(tamano / (1024 * 1024), 1)
        })
    return emus

def escanear():
    roms = escanear_roms()
    juegos = escanear_juegos_extra()
    emus = escanear_emuladores()
    todos = roms + juegos + emus
    todos.sort(key=lambda j: (j["tipo"], j["sistema"], j["nombre"].lower()))
    # Reindexar IDs
    for i, j in enumerate(todos):
        j["id"] = str(i)
    resultado = {
        "actualizado": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(todos),
        "total_roms": len(roms),
        "total_juegos": len(juegos),
        "total_emuladores": len(emus),
        "juegos": todos
    }
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    return resultado

if __name__ == "__main__":
    print("========================================")
    print("  Escaner de ROMs y Juegos - El Nino (v3)")
    print("========================================")
    r = escanear()
    print("ROMs:        " + str(r["total_roms"]))
    print("Juegos:      " + str(r["total_juegos"]))
    print("Emuladores:  " + str(r["total_emuladores"]))
    print("TOTAL:       " + str(r["total"]))
    print("")
    print("Guardado en: " + SALIDA)
