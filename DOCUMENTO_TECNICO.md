# Documento Tecnico - Proyecto "El Nino"
**Ultima actualizacion:** 12 de septiembre de 2026
**Autor:** Manuel Casimiro Carrasco (urukaisk-maker)
**Sistema:** Garuda Linux (shell fish)
**Disco:** /run/media/urukais/PROYECTOS/
**Repo:** https://github.com/urukaisk-maker/centro-mando-gamer-el-nino
**Demo:** https://centro-mando-gamer-el-nino.vercel.app/

---

## INDICE

1. Arquitectura general
2. Estructura de carpetas
3. Servidor Python
4. Endpoints disponibles
5. Escaner de ROMs
6. Sistema systemd
7. Launcher web (funciones JS)
8. Scripts auxiliares
9. Notas tecnicas criticas
10. Pendientes

---

## 1. ARQUITECTURA GENERAL

El proyecto tiene tres capas:

- **Frontend:** HTML, CSS y JavaScript vanilla. Launcher web Cyberpunk con buscador, panel de configuracion, estadisticas, chatbot y seccion dinamica de ROMs.
- **Backend:** Servidor Python 3 con ThreadingTCPServer. Sirve archivos estaticos y expone endpoints para lanzar juegos, matar procesos, hacer backup, escanear ROMs, etc.
- **Sistema:** Servicios systemd de usuario que arrancan el servidor, importan el entorno grafico y programan backups automaticos.

---

## 2. ESTRUCTURA DE CARPETAS

/run/media/urukais/PROYECTOS/
- 01_EL_NINO_LAUNCHER/          Launcher principal + manual + estadisticas
- 02_EMULADORES_Y_ROMS/         ROMs y emuladores
-   01_PS2/ 02_PSP/ 03_GAMECUBE_WII/ 04_GBA_SNES/ 05_ARCADE_MAME/
-   EJECUTABLES_PORTABLES/       AppImages y scripts
-   SAVES_GUARDADOS/             Backups de partidas
- 03_STREAMING_Y_CLIPS/
- 04_MODS_Y_SHADERS/
- 05_HERRAMIENTAS_GAMER/
-   PERFILES_MANDO/              Perfiles Xbox/DualShock/8BitDo
-   instalar_mandos.sh
- 06_MEDIA_Y_WALLPAPERS/        Galeria + 12 wallpapers
- 07_DIARIO_MARIO/              Diario personal
- 08_JUEGOS_EXTRA/              13 juegos completos + scripts
- server.py                    Servidor Python
- escanear_roms.py             Escaner de ROMs
- Backup_Partidas.sh           Script de backup
- Restaurar_Partidas.sh        Restauracion
- limpiar_cache.sh             Limpieza
- Iniciar.sh / Detener.sh
- ABRIR EL NINO.bat / .ico
- autorun.inf
- MANUAL.txt / README.md
- DOCUMENTO_TECNICO.md
- python_portable/             Python portable para Windows

---

## 3. SERVIDOR PYTHON (server.py)

### Caracteristicas
- Puerto: 8080
- Clase: ServidorConcurrente(socketserver.ThreadingTCPServer)
  - allow_reuse_address = True  (evita errores "Address already in use")
  - daemon_threads = True       (hilos se cierran al apagar)
- Registro de procesos: diccionario global procesos_activos con lock
- Detecta IP local al arrancar y la imprime en el log

### Logica principal (do_GET)
- /launch/<emulador>   -> Lanzar emulador
- /juego/<nombre>      -> Lanzar juego extra
- /rom/<sis>/<arch>    -> Lanzar ROM escaneada
- /kill/<nombre>       -> Matar proceso
- /estado              -> JSON de procesos activos
- /escanear-roms       -> Reescanear ROMs
- /instalar-mandos     -> Instalar perfiles de mando
- /limpiar             -> Limpieza
- /backup              -> Backup manual
- else                 -> Servir archivos estaticos

---

## 4. ENDPOINTS DISPONIBLES

| Endpoint | Descripcion |
|---|---|
| /launch/<emulador> | Lanza un emulador (pcsx2, dolphin, ppsspp, retroarch) |
| /juego/<nombre> | Lanza un juego extra (cavestory, quake...) |
| /rom/<sistema>/<archivo> | Lanza una ROM escaneada |
| /kill/<nombre> | Mata un proceso. Devuelve {ok, mensaje} |
| /estado | JSON con procesos activos |
| /escanear-roms | Regenera juegos.json |
| /instalar-mandos | Copia perfiles de mando |
| /limpiar | Ejecuta limpieza |
| /backup | Ejecuta backup manual |

---

## 5. ESCANER DE ROMS

Script: escanear_roms.py

Escanea 02_EMULADORES_Y_ROMS/ y genera 01_EL_NINO_LAUNCHER/juegos.json.

### Carpetas ignoradas
retroarch, assets, docs, BIOS, cores, config, shaders, overlays,
thumbnails, playlists, saves, states, screenshots, system, info,
database, cheats, filters, autoconfig, input, menu, menu_drivers,
libretro, dolphin-emu, PCSX2, PPSSPP, wine, squashfs-root,
python_portable, .git, node_modules, __pycache__, src, source

### Extensiones validas
- PS2:      .iso .bin .chd .elf .mdf
- PSP:      .iso .cso .pbp .chd
- GC/Wii:   .iso .gcm .wbfs .rvz .dol
- GBA/SNES: .gba .gb .gbc .snes .sfc .smc .nes .md .gen .gg .sms .pce
- Arcade:   .zip .7z .chd

---

## 6. SISTEMA SYSTEMD

### elnino.service (Servidor)
[Unit]
Description=Centro de Mando Gamer El Nino
After=network.target graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=/run/media/urukais/PROYECTOS
ExecStart=/usr/bin/python3 /run/media/urukais/PROYECTOS/server.py
Restart=on-failure
RestartSec=3
Environment=DISPLAY=:1
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

[Install]
WantedBy=default.target

### elnino-env.service (importa entorno grafico)
[Service]
Type=oneshot
ExecStart=/bin/bash -c 'systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS && systemctl --user restart elnino.service'
RemainAfterExit=yes

### elnino-backup.timer (backup automatico)
[Timer]
OnCalendar=Sun *-*-* 20:00:00
Persistent=true
Unit=elnino-backup.service

### Comandos utiles
systemctl --user status elnino.service
systemctl --user restart elnino.service
journalctl --user -u elnino.service -n 30
systemctl --user list-timers elnino-backup.timer
systemctl --user start elnino-backup.service

---

## 7. LAUNCHER WEB (Funciones JS)

| Funcion | Descripcion |
|---|---|
| toggleTV() | Modo TV (tecla T) |
| toggleAudio() | Silenciar/activar audio |
| hacerBackup() | Modal + /backup |
| hacerLimpieza() | Modal + /limpiar |
| instalarMandos() | Modal + /instalar-mandos |
| toggleSettings() | Abre panel configuracion |
| setTheme() | Cambia tema colores |
| setVolumen() | Ajusta volumen |
| editarRedes() | Modal editar redes sociales |
| toggleChatbot() | Abre/cierra chatbot |
| enviarChat() | Envia mensaje al chatbot |
| actualizarProcesos() | Panel flotante cada 5s |
| matarProceso() | Modal + /kill/<nombre> |
| cargarRoms() | Carga juegos.json |
| reescanearRoms() | Llama a /escanear-roms |
| mostrarToast() | Notificacion cyberpunk |
| mostrarModal() | Modal con Promise (async/await) |

### Sistema de pop-ups
- Toast: notificaciones esquina superior derecha
- Modal: confirmaciones con Promise (async/await)

---

## 8. SCRIPTS AUXILIARES

### escanear_roms.py
Escanea carpetas de ROMs y regenera juegos.json.

### Backup_Partidas.sh
Copia partidas de PCSX2, Dolphin, PPSSPP y RetroArch.
Incluye el diario exportado.

### Restaurar_Partidas.sh
Restaura el backup mas reciente.

### limpiar_cache.sh
Borra __pycache__, backups antiguos (deja 5), locks, .bak, temporales.

### instalar_mandos.sh
Copia perfiles de mando a RetroArch, PCSX2, PPSSPP y Dolphin.

### Iniciar.sh
Reinicia el servicio systemd, arranca servidor si no responde,
abre Brave/Chromium/Firefox con el launcher.

### Detener.sh
Mata el proceso del servidor.

---

## 9. NOTAS TECNICAS CRITICAS

- Shell fish NO soporta heredocs (<<EOF). Usar printf o python3 -c.
- Nunca pegar URLs en la terminal. Van al navegador.
- El disco se monta en /run/media/urukais/PROYECTOS/ (sin el "1").
- fish se atraganta con bloques largos. Pegar de uno en uno.
- Scripts .sh usan $(dirname "$0") para ser portables.
- grep en fish: usar -F para busquedas literales.
- Servicio systemd de usuario NO tiene entorno grafico por defecto.
  Por eso elnino-env.service importa las variables al iniciar sesion.
- RetroArch desde el servidor necesita:
  DISPLAY, WAYLAND_DISPLAY, XDG_RUNTIME_DIR, DBUS_SESSION_BUS_ADDRESS.

---

## 10. PENDIENTES

1. Probar el .bat en un Windows real
2. BIOS y ROMs propias de Mario
3. Actualizar el manual con las nuevas funciones
4. Documentar los perfiles de mando con mas detalle

---

## COMANDOS DE REFERENCIA RAPIDA

Arrancar el servidor manualmente:
    bash /run/media/urukais/PROYECTOS/Iniciar.sh

Comprobar el servidor:
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/01_EL_NINO_LAUNCHER/index.html

Ver procesos activos:
    curl -s http://localhost:8080/estado

Ver la IP local para el movil:
    ip route get 8.8.8.8

Regenerar el JSON de ROMs:
    python3 /run/media/urukais/PROYECTOS/escanear_roms.py

Ver logs del servidor en tiempo real:
    journalctl --user -u elnino.service -f

---

Centro de Mando Gamer "El Nino" - 2026 - Manuel Casimiro Carrasco
