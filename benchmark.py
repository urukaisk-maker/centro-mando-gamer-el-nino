#!/usr/bin/env python3
import subprocess, os, json, time, platform, re

def ejecutar(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return ""

def leer_cpu():
    info = {"modelo": "Desconocido", "nucleos": 0, "hilos": 0, "mhz": 0}
    try:
        with open("/proc/cpuinfo") as f:
            contenido = f.read()
        match = re.search(r"model name\s*:\s*(.+)", contenido)
        if match:
            info["modelo"] = match.group(1).strip()
        info["nucleos"] = contenido.count("cpu cores")
        info["hilos"] = contenido.count("processor\t:")
        match = re.search(r"cpu MHz\s*:\s*([\d.]+)", contenido)
        if match:
            info["mhz"] = float(match.group(1))
    except:
        pass
    return info

def leer_ram():
    try:
        with open("/proc/meminfo") as f:
            contenido = f.read()
        match = re.search(r"MemTotal:\s+(\d+)", contenido)
        if match:
            return round(int(match.group(1)) / 1024 / 1024, 1)
    except:
        pass
    return 0

def leer_gpu():
    gpus = []
    salida = ejecutar("lspci | grep -iE 'vga|3d|display'")
    for linea in salida.split("\n"):
        if linea.strip():
            # Extraer el nombre despues de los dos puntos
            partes = linea.split(":", 2)
            if len(partes) >= 3:
                gpus.append(partes[2].strip())
    return gpus

def leer_disco():
    salida = ejecutar("df -h / | tail -1")
    if salida:
        partes = salida.split()
        if len(partes) >= 2:
            return partes[1]
    return "?"

def puntuar(cpu, ram, gpus):
    puntos = 0
    detalle = []

    # CPU
    hilos = cpu["hilos"]
    if hilos >= 16:
        puntos += 30
        detalle.append("CPU potente (" + str(hilos) + " hilos)")
    elif hilos >= 8:
        puntos += 20
        detalle.append("CPU buena (" + str(hilos) + " hilos)")
    elif hilos >= 4:
        puntos += 10
        detalle.append("CPU media (" + str(hilos) + " hilos)")
    else:
        detalle.append("CPU basica (" + str(hilos) + " hilos)")

    # RAM
    if ram >= 16:
        puntos += 30
        detalle.append("RAM: " + str(ram) + " GB (excelente)")
    elif ram >= 8:
        puntos += 20
        detalle.append("RAM: " + str(ram) + " GB (buena)")
    elif ram >= 4:
        puntos += 10
        detalle.append("RAM: " + str(ram) + " GB (suficiente)")
    else:
        detalle.append("RAM: " + str(ram) + " GB (justa)")

    # GPU
    gpu_texto = " ".join(gpus).lower()
    tiene_dedicada = any(x in gpu_texto for x in ["nvidia", "geforce", "radeon", "amd", "rx ", "gtx", "rtx"])
    if tiene_dedicada:
        puntos += 40
        detalle.append("GPU dedicada detectada")
    else:
        puntos += 15
        detalle.append("GPU integrada")

    # Categoria final
    if puntos >= 80:
        categoria = "ALTA"
        color = "#00ff88"
    elif puntos >= 50:
        categoria = "MEDIA"
        color = "#00f0ff"
    else:
        categoria = "BASICA"
        color = "#ff8800"

    return puntos, categoria, color, detalle

def recomendar(categoria):
    recs = {}
    if categoria == "ALTA":
        recs["PCSX2"] = {"renderizador": "Vulkan", "resolucion": "3x Native (1080p+)", "filtros": "Activados", "notas": "Todo al maximo"}
        recs["Dolphin"] = {"renderizador": "Vulkan", "resolucion": "3x Native (1080p+)", "antialiasing": "8x MSAA", "notas": "Todo al maximo"}
        recs["PPSSPP"] = {"renderizador": "Vulkan", "resolucion": "3x PSP", "notas": "Todo al maximo"}
        recs["RetroArch"] = {"filtros": "Shaders CRT/Scanlines", "notas": "Shader fancy activado"}
    elif categoria == "MEDIA":
        recs["PCSX2"] = {"renderizador": "Vulkan", "resolucion": "2x Native (720p)", "filtros": "Basicos", "notas": "Buen equilibrio"}
        recs["Dolphin"] = {"renderizador": "Vulkan", "resolucion": "2x Native (720p)", "antialiasing": "4x MSAA", "notas": "Buen equilibrio"}
        recs["PPSSPP"] = {"renderizador": "Vulkan", "resolucion": "2x PSP", "notas": "Buen equilibrio"}
        recs["RetroArch"] = {"filtros": "Shaders simples", "notas": "Shader ligero"}
    else:
        recs["PCSX2"] = {"renderizador": "OpenGL", "resolucion": "1x Native (480p)", "filtros": "Desactivados", "notas": "Prioriza velocidad"}
        recs["Dolphin"] = {"renderizador": "OpenGL", "resolucion": "1x Native (480p)", "antialiasing": "Desactivado", "notas": "Prioriza velocidad"}
        recs["PPSSPP"] = {"renderizador": "OpenGL", "resolucion": "1x PSP", "notas": "Prioriza velocidad"}
        recs["RetroArch"] = {"filtros": "Desactivados", "notas": "Sin shaders"}
    return recs

def main():
    cpu = leer_cpu()
    ram = leer_ram()
    gpus = leer_gpu()
    disco = leer_disco()
    puntos, categoria, color, detalle = puntuar(cpu, ram, gpus)
    recs = recomendar(categoria)

    resultado = {
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sistema": platform.system() + " " + platform.release(),
        "cpu": cpu,
        "ram_gb": ram,
        "gpus": gpus,
        "disco_libre": disco,
        "puntos": puntos,
        "categoria": categoria,
        "color": color,
        "detalle": detalle,
        "recomendaciones": recs
    }

    salida = "/run/media/urukais/PROYECTOS/01_EL_NINO_LAUNCHER/benchmark.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print("Benchmark completado: " + categoria + " (" + str(puntos) + "/100)")
    return resultado

if __name__ == "__main__":
    main()

