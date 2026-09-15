#!/usr/bin/env python3
import os, json, time

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ROMS_DIR   = os.path.join(DIRECTORIO, "02_EMULADORES_Y_ROMS")
JUEGOS_DIR = os.path.join(DIRECTORIO, "08_JUEGOS_EXTRA")
EMUS_DIR   = os.path.join(ROMS_DIR, "EJECUTABLES_PORTABLES")
SALIDA     = os.path.join(DIRECTORIO, "01_EL_NINO_LAUNCHER", "juegos.json")

CARPETAS_IGNORADAS = [
    "assets","docs","doc","BIOS","bios","cores","config","configs",
    "shaders","overlays","thumbnails","playlists","saves","states",
    "screenshots","system","info","database","cheats","filters",
    "autoconfig","input","menu","menu_drivers","libretro","dolphin-emu",
    "PCSX2","PPSSPP","wine","squashfs-root","python_portable","windows",
    ".git","node_modules","__pycache__","src","source",
]

EXTENSIONES_IGNORADAS = [
    ".md",".txt",".html",".htm",".png",".jpg",".jpeg",".gif",".svg",
    ".ico",".ttf",".otf",".woff",".json",".xml",".cfg",".ini",".conf",
    ".log",".dll",".so",".exe",".bat",".py",".js",".css",".pdf",".doc",
    ".docx",".nfo",".sfv",
]

SISTEMAS = {
    "ps2": {"carpeta":"01_PS2","ext":[".iso",".bin",".chd",".elf",".mdf"],
            "nombre":"PlayStation 2","icono":"🎮","color":"#0066ff","emulador":"pcsx2"},
    "psp": {"carpeta":"02_PSP","ext":[".iso",".cso",".pbp",".chd"],
            "nombre":"PlayStation Portable","icono":"🕹","color":"#00f0ff","emulador":"ppsspp"},
    "gamecube_wii": {"carpeta":"03_GAMECUBE_WII","ext":[".iso",".gcm",".wbfs",".rvz",".dol"],
            "nombre":"GameCube / Wii","icono":"🐬","color":"#ff00ff","emulador":"dolphin"},
    "gba_snes": {"carpeta":"04_GBA_SNES","ext":[".gba",".gb",".gbc",".snes",".sfc",".smc",".nes",".md",".gen",".gg",".sms",".pce",".ngp",".ws",".wsc"],
            "nombre":"GBA / SNES / NES","icono":"🔹","color":"#00ff88","emulador":"retroarch"},
    "arcade": {"carpeta":"05_ARCADE_MAME","ext":[".zip",".7z",".chd"],
            "nombre":"Arcade MAME","icono":"👾","color":"#ff8800","emulador":"retroarch"},
}

EMULADORES_INFO = {
    "pcsx2":       {"nombre":"PCSX2","icono":"🎮","color":"#0066ff","sistema":"PlayStation 2"},
    "ppsspp":      {"nombre":"PPSSPP","icono":"🕹","color":"#00f0ff","sistema":"PSP"},
    "dolphin":     {"nombre":"Dolphin","icono":"🐬","color":"#ff00ff","sistema":"GameCube / Wii"},
    "retroarch":   {"nombre":"RetroArch","icono":"🔹","color":"#00ff88","sistema":"Multi-sistema"},
    "duckstation": {"nombre":"DuckStation","icono":"🦆","color":"#ff8800","sistema":"PS1"},
    "flycast":     {"nombre":"Flycast","icono":"🌐","color":"#00ccff","sistema":"Dreamcast"},
    "mgba":        {"nombre":"mGBA","icono":"🎯","color":"#00ff88","sistema":"GBA"},
    "melonds":     {"nombre":"melonDS","icono":"🍈","color":"#ff6666","sistema":"Nintendo DS"},
    "mesen":       {"nombre":"Mesen","icono":"⚡","color":"#ffcc00","sistema":"NES/SNES"},
}

def carpeta_ignorada(n):
    return n.lower() in [c.lower() for c in CARPETAS_IGNORADAS]

def es_archivo_valido(archivo, exts):
    ext = os.path.splitext(archivo)[1].lower()
    if ext in EXTENSIONES_IGNORADAS:
        return False
    if ext == ".zip":
        return ".zip" in exts
    return ext in exts

def limpiar_nombre(n):
    base = os.path.splitext(n)[0]
    for m in ["(USA)","(Europe)","(Japan)","(Spain)","(World)","[!]",
              "(En,Fr,De,Es,It)","(U)","(E)","(J)"]:
        base = base.replace(m, "")
    return base.strip(" -_") or n

def escanear_roms():
    juegos = []
    for sid, sis in SISTEMAS.items():
        carpeta = os.path.join(ROMS_DIR, sis["carpeta"])
        if not os.path.isdir(carpeta): continue
        for raiz, dirs, archivos in os.walk(carpeta):
            dirs[:] = [d for d in dirs if not carpeta_ignorada(d)]
            if carpeta_ignorada(os.path.basename(raiz)): continue
            for a in archivos:
                if es_archivo_valido(a, sis["ext"]):
                    ruta = os.path.join(raiz, a)
                    try: tam = os.path.getsize(ruta)
                    except: tam = 0
                    juegos.append({
                        "id":str(len(juegos)),"tipo":"rom",
                        "nombre":limpiar_nombre(a),"archivo":a,"ruta":ruta,
                        "sistema":sid,"sistema_nombre":sis["nombre"],
                        "icono":sis["icono"],"color":sis["color"],
                        "emulador":sis["emulador"],
                        "tamano_mb":round(tam/(1024*1024),1)
                    })
    return juegos

def escanear_juegos_extra():
    juegos = []
    if not os.path.isdir(JUEGOS_DIR):
        return juegos
    archivos = os.listdir(JUEGOS_DIR)
    bases = {}
    for a in archivos:
        ruta = os.path.join(JUEGOS_DIR, a)
        if not os.path.isfile(ruta): continue
        ext = os.path.splitext(a)[1].lower()
        if ext not in (".appimage", ".sh"): continue
        base = os.path.splitext(a)[0]
        if base not in bases: bases[base] = {}
        bases[base][ext] = a

    for base, variantes in bases.items():
        if ".appimage" in variantes:
            archivo = variantes[".appimage"]
            icono = "🎁"; color = "#ff00aa"; tipo = "juego"
        elif ".sh" in variantes:
            archivo = variantes[".sh"]
            icono = "🎮"; color = "#00aaff"; tipo = "lanzador"
        else:
            continue
        ruta = os.path.join(JUEGOS_DIR, archivo)
        try: tam = os.path.getsize(ruta)
        except: tam = 0
        juegos.append({
            "id":"juego_" + base,"tipo":tipo,
            "nombre":base,"archivo":archivo,"ruta":ruta,
            "sistema":"extra","sistema_nombre":"Juegos libres",
            "icono":icono,"color":color,"emulador":"",
            "tamano_mb":round(tam/(1024*1024),1)
        })
    return juegos

def escanear_emuladores():
    emus = []
    if not os.path.isdir(EMUS_DIR): return emus
    for a in os.listdir(EMUS_DIR):
        if not a.lower().endswith(".appimage"): continue
        ruta = os.path.join(EMUS_DIR, a)
        if not os.path.isfile(ruta): continue
        try: tam = os.path.getsize(ruta)
        except: tam = 0
        if tam < 1024*1024: continue
        nl = a.lower()
        info = None
        for clave, datos in EMULADORES_INFO.items():
            if clave in nl:
                info = datos; break
        if not info:
            info = {"nombre":limpiar_nombre(a),"icono":"🕹","color":"#888888","sistema":"Emulador"}
        emus.append({
            "id":"emu_" + a,"tipo":"emulador",
            "nombre":info["nombre"],"archivo":a,"ruta":ruta,
            "sistema":"emulador","sistema_nombre":info["sistema"],
            "icono":info["icono"],"color":info["color"],
            "emulador":"","tamano_mb":round(tam/(1024*1024),1)
        })
    return emus

def escanear():
    roms = escanear_roms()
    juegos = escanear_juegos_extra()
    emus = escanear_emuladores()
    todos = roms + juegos + emus
    todos.sort(key=lambda j: (j["tipo"], j["sistema"], j["nombre"].lower()))
    for i, j in enumerate(todos):
        j["id"] = str(i)
    r = {
        "actualizado": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(todos),
        "total_roms": len(roms),
        "total_juegos": len(juegos),
        "total_emuladores": len(emus),
        "juegos": todos
    }
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    return r

if __name__ == "__main__":
    print("========================================")
    print("  Escaner de ROMs y Juegos - El Nino (v4)")
    print("========================================")
    r = escanear()
    print("ROMs:        " + str(r["total_roms"]))
    print("Juegos/.sh:  " + str(r["total_juegos"]))
    print("Emuladores:  " + str(r["total_emuladores"]))
    print("TOTAL:       " + str(r["total"]))
    print("")
    print("Guardado en: " + SALIDA)
