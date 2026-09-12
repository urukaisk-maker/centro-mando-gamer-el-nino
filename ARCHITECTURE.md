# ARCHITECTURE - El Nino

Diagrama y explicacion de la arquitectura del proyecto.

## VISION GENERAL

```
Launcher Web  <--HTTP-->  Servidor Python  --Bash-->  Emulador/Juego
                                    |
                                    v
                            systemd (servicios usuario)
```

## COMPONENTES

### 1. Launcher Web (01_EL_NINO_LAUNCHER/index.html)
- HTML5 + CSS3 + JavaScript vanilla
- Comunicacion HTTP contra localhost:8080
- Muestra tarjetas, buscador, panel config, chatbot, estadisticas

### 2. Servidor Python (server.py)
- Python 3 + ThreadingTCPServer + subprocess
- Puerto 8080 (configurable en config.json)
- Sirve archivos, expone endpoints, registra procesos

### 3. Emuladores y juegos
- PCSX2, PPSSPP, Dolphin, RetroArch (AppImages)
- 13 juegos completos gratuitos
- El servidor los lanza con subprocess.Popen

### 4. Sistema (systemd)
- elnino.service: arranca el servidor
- elnino-env.service: importa entorno grafico
- elnino-backup.timer: backup automatico domingos 20:00

## FLUJOS

### Jugar
Navegador -> GET /juego/X -> server.py -> bash X.sh -> emulador

### Backup
Navegador -> GET /backup -> server.py -> Backup_Partidas.sh

### Escanear ROMs
Navegador -> GET /escanear-roms -> escanear_roms.py -> juegos.json

## DEPENDENCIAS
- Python 3.10+ (solo stdlib)
- Bash
- systemd
- Frontend: cero dependencias

## COMO CONTRIBUIR

Anadir juego:
1. Copia binario a 08_JUEGOS_EXTRA/
2. Crea .sh que lo lance con $(dirname "$0")
3. Anade boton en el launcher

Anadir emulador:
1. Copia AppImage a EJECUTABLES_PORTABLES/
2. Crea .sh
3. Anade al dict REQUISITOS en server.py

---

Centro de Mando Gamer "El Nino" - 2026 - Manuel Casimiro Carrasco
