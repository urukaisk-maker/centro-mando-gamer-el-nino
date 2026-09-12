#!/usr/bin/env python3
# ==========================================
#  ESCANER DE ROMS - EL NINO (v2)
# ==========================================
import os, json, time

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ROMS_DIR = os.path.join(DIRECTORIO, "02_EMULADORES_Y_ROMS")
SALIDA = os.path.join(DIRECTORIO, "01_EL_NINO_LAUNCHER", "juegos.json")

# Carpetas que NO se escanean (emuladores, docs, assets...)
CARPETAS_IGNORADAS = [
    "retroarch", "RetroArch", "RetroArch-Win64", "RetroArch-Linux",
    "assets", "docs", "doc", "documentation", "BIOS", "bios",
    "cores", "config", "configs", "shaders", "overlays",
    "thumbnails", "playlists", "saves", "states", "screenshots",
    "system", "info", "database", "cheats", "filters", "autoconfig",
    "input", "menu", "menu_drivers", "libretro", "dolphin-emu",
    "PCSX2", "PPSSPP", "wine", "squashfs-root", "python_portable",
    ".git", "node_modules", "__pycache__", "src", "source",
]

# Extensiones que NO son ROMs (nunca)
EXTENSIONES_IGNORADAS = [
    ".md", ".txt", ".html", ".htm", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".ico", ".ttf", ".otf", ".woff", ".json", ".xml", ".cfg",
    ".ini", ".conf", ".log", ".dll", ".so", ".exe", ".bat", ".sh",
    ".py", ".js", ".css", ".pdf", ".doc", ".docx", ".nfo", ".sfv"
]

SISTEMAS = {
    "ps2": {
        "carpeta": "01_PS2",
        "extensiones": [".iso", ".bin", ".chd", ".elf", ".mdf"],
        "nombre": "PlayStation 2", "icono": "🎮", "color": "#0066ff", "emulador": "pcsx2"
    },
    "psp": {
        "carpeta": "02_PSP",
        "extensiones": [".iso", ".cso", ".pbp", ".chd"],
        "nombre": "PlayStation Portable", "icono": "🕹", "color": "#00f0ff", "emulador": "ppsspp"
    },
    "gamecube_wii": {
        "carpeta": "03_GAMECUBE_WII",
        "extensiones": [".iso", ".gcm", ".wbfs", ".rvz", ".dol"],
        "nombre": "GameCube / Wii", "icono": "🐬", "color": "#ff00ff", "emulador": "dolphin"
    },
    "gba_snes": {
        "carpeta": "04_GBA_SNES",
        "extensiones": [".gba", ".gb", ".gbc", ".snes", ".sfc", ".smc", ".nes", ".md", ".gen", ".gg", ".sms", ".pce", ".ngp", ".ws", ".wsc"],
        "nombre": "GBA / SNES / NES", "icono": "🔹", "color": "#00ff88", "emulador": "retroarch"
    },
    "arcade": {
        "carpeta": "05_ARCADE_MAME",
        "extensiones": [".zip", ".7z", ".chd"],
        "nombre": "Arcade MAME", "icono": "👾", "color": "#ff8800", "emulador": "retroarch"
    }
}

def carpeta_ignorada(nombre):
    return nombre.lower() in [c.lower() for c in CARPETAS_IGNORADAS]

def es_archivo_valido(archivo, extensiones):
    ext = os.path.splitext(archivo)[1].lower()
    if ext in EXTENSIONES_IGNORADAS:
        return False
    # Solo zip permitido para arcade
    if ext == ".zip":
        return ".zip" in extensiones
    return ext in extensiones

def limpiar_nombre(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    for marca in ["(USA)", "(Europe)", "(Japan)", "(Spain)", "(World)", "[!]", "(En,Fr,De,Es,It)", "(U)", "(E)", "(J)"]:
        nombre = nombre.replace(marca, "")
    return nombre.strip(" -_") or nombre_archivo

def escanear():
    juegos = []
    for sistema_id, sistema in SISTEMAS.items():
        carpeta = os.path.join(ROMS_DIR, sistema["carpeta"])
        if not os.path.isdir(carpeta):
            continue
        for raiz, dirs, archivos in os.walk(carpeta):
            # Saltar carpetas ignoradas
            dirs[:] = [d for d in dirs if not carpeta_ignorada(d)]
            if carpeta_ignorada(os.path.basename(raiz)):
                continue
            for archivo in archivos:
                if es_archivo_valido(archivo, sistema["extensiones"]):
                    ruta_completa = os.path.join(raiz, archivo)
                    try:
                        tamano = os.path.getsize(ruta_completa)
                    except:
                        tamano = 0
                    juegos.append({
                        "id": str(len(juegos)),
                        "nombre": limpiar_nombre(archivo),
                        "archivo": archivo,
                        "ruta": ruta_completa,
                        "sistema": sistema_id,
                        "sistema_nombre": sistema["nombre"],
                        "icono": sistema["icono"],
                        "color": sistema["color"],
                        "emulador": sistema["emulador"],
                        "tamano_mb": round(tamano / (1024 * 1024), 1)
                    })

    juegos.sort(key=lambda j: (j["sistema"], j["nombre"].lower()))
    resultado = {
        "actualizado": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(juegos),
        "juegos": juegos
    }
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    return resultado

if __name__ == "__main__":
    print("========================================")
    print("  Escaner de ROMs - El Nino (v2)")
    print("========================================")
    r = escanear()
    print("ROMs encontradas: " + str(r["total"]))
    print("")
    por_sistema = {}
    for j in r["juegos"]:
        por_sistema[j["sistema_nombre"]] = por_sistema.get(j["sistema_nombre"], 0) + 1
    for s, c in por_sistema.items():
        print("  " + s + ": " + str(c))
    print("")
    print("Guardado en: " + SALIDA)
