#!/usr/bin/env python3
# ==========================================
#  TIMELINE DE SAVES - EL NINO
# ==========================================
# Vigila las carpetas de saves de los emuladores
# y crea copias con timestamp para tener historico.

import os, json, time, shutil, hashlib

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
TIMELINE_DIR = os.path.join(DIRECTORIO, "02_EMULADORES_Y_ROMS", "SAVES_GUARDADOS", "timeline")
os.makedirs(TIMELINE_DIR, exist_ok=True)

# Carpetas de saves por emulador
FUENTES = {
    "PCSX2-memcards": os.path.expanduser("~/.config/PCSX2/memcards"),
    "PCSX2-memcards-alt": os.path.expanduser("~/.local/share/PCSX2/memcards"),
    "PCSX2-states": os.path.expanduser("~/.config/PCSX2/sstates"),
    "Dolphin-GC": os.path.expanduser("~/.local/share/dolphin-emu/GC"),
    "Dolphin-Wii": os.path.expanduser("~/.local/share/dolphin-emu/Wii"),
    "Dolphin-States": os.path.expanduser("~/.local/share/dolphin-emu/StateSaves"),
    "PPSSPP-SAVEDATA": os.path.expanduser("~/.config/ppsspp/PSP/SAVEDATA"),
    "PPSSPP-States": os.path.expanduser("~/.config/ppsspp/PSP/PPSSPP_STATE"),
    "RetroArch-saves": os.path.expanduser("~/.config/retroarch/saves"),
    "RetroArch-states": os.path.expanduser("~/.config/retroarch/states")
}

def hash_archivo(ruta):
    """Hash MD5 rapido de un archivo."""
    try:
        with open(ruta, "rb") as f:
            return hashlib.md5(f.read(8192)).hexdigest() + "_" + str(os.path.getsize(ruta))
    except:
        return None

def cargar_indice():
    p = os.path.join(TIMELINE_DIR, "indice.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except:
            pass
    return {"entradas": [], "ultimo_escaneo": None}

def guardar_indice(indice):
    p = os.path.join(TIMELINE_DIR, "indice.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

def escanear():
    indice = cargar_indice()
    hashes_conocidos = {e["hash"]: e for e in indice["entradas"]}
    nuevos = 0
    total_archivos = 0

    for fuente, ruta in FUENTES.items():
        if not os.path.isdir(ruta):
            continue
        for raiz, dirs, archivos in os.walk(ruta):
            for archivo in archivos:
                # Solo archivos de save (no carpetas de config)
                ext = os.path.splitext(archivo)[1].lower()
                if ext not in [".ps2", ".mcd", ".gci", ".raw", ".sav", ".state", ".ppst", ".dsz", ".srm", ".dat", ".bin"]:
                    continue
                ruta_completa = os.path.join(raiz, archivo)
                total_archivos += 1
                h = hash_archivo(ruta_completa)
                if not h:
                    continue
                if h in hashes_conocidos:
                    continue

                # Es nuevo: copiar con timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                destino_dir = os.path.join(TIMELINE_DIR, fuente)
                os.makedirs(destino_dir, exist_ok=True)
                destino = os.path.join(destino_dir, timestamp + "_" + archivo)
                try:
                    shutil.copy2(ruta_completa, destino)
                    tamano = os.path.getsize(ruta_completa)
                    entrada = {
                        "hash": h,
                        "fuente": fuente,
                        "archivo": archivo,
                        "ruta_original": ruta_completa,
                        "ruta_copia": destino,
                        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": time.time(),
                        "tamano_kb": round(tamano / 1024, 1)
                    }
                    indice["entradas"].append(entrada)
                    hashes_conocidos[h] = entrada
                    nuevos += 1
                except Exception as e:
                    print("Error copiando " + archivo + ": " + str(e))

    indice["entradas"].sort(key=lambda e: e["timestamp"], reverse=True)
    indice["ultimo_escaneo"] = time.strftime("%Y-%m-%d %H:%M:%S")
    guardar_indice(indice)

    return {
        "nuevos": nuevos,
        "total_archivos": total_archivos,
        "total_historico": len(indice["entradas"]),
        "fuentes_activas": sum(1 for f in FUENTES.values() if os.path.isdir(f))
    }

if __name__ == "__main__":
    print("========================================")
    print("  Timeline de saves - El Nino")
    print("========================================")
    r = escanear()
    print("Fuentes activas: " + str(r["fuentes_activas"]))
    print("Archivos detectados: " + str(r["total_archivos"]))
    print("Nuevos snapshots: " + str(r["nuevos"]))
    print("Total en historico: " + str(r["total_historico"]))
    print("")
    print("Guardado en: " + TIMELINE_DIR)
