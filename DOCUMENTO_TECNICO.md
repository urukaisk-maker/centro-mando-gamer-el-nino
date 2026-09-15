# Documento Tecnico - Proyecto "El Nino"
**Ultima actualizacion:** 12 de septiembre de 2026
**Autor:** Manuel Casimiro Carrasco (urukaisk-maker)
**Sistema:** Garuda Linux (shell fish)
**Disco:** /run/media/urukais/PROYECTOS/
**Repo:** https://github.com/urukaisk-maker/centro-mando-gamer-el-nino
**Demo Vercel:** https://centro-mando-gamer-el-nino-mmcq.vercel.app/
**Demo Pages:** https://urukaisk-maker.github.io/centro-mando-gamer-el-nino/

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
10. Historial de mejoras
11. Pendientes

---

## 1. ARQUITECTURA GENERAL

El proyecto tiene tres capas:

- **Frontend:** HTML, CSS y JavaScript vanilla. Launcher web Cyberpunk con buscador,
  panel de configuracion, estadisticas, chatbot, radio, benchmark, retroachievements,
  mando tactil, kiosco con PIN, seccion dinamica de ROMs y header ocultable.
- **Backend:** Servidor Python 3 con ThreadingTCPServer + SSE. Sirve archivos estaticos
  y expone endpoints para lanzar juegos, matar procesos, hacer backup, escanear ROMs,
  comprimir, modos fiesta/cine, y transmision de estado en vivo (CPU/RAM).
- **Sistema:** Servicios systemd de usuario que arrancan el servidor, importan el
  entorno grafico y programan backups automaticos.

---

## 2. ESTRUCTURA DE CARPETAS

/run/media/urukais/PROYECTOS/
- 01_EL_NINO_LAUNCHER/          Launcher + manual + estadisticas + benchmark
- 02_EMULADORES_Y_ROMS/         ROMs y emuladores
-   01_PS2/ 02_PSP/ 03_GAMECUBE_WII/ 04_GBA_SNES/ 05_ARCADE_MAME/
-   EJECUTABLES_PORTABLES/       AppImages y scripts
-   SAVES_GUARDADOS/             Backups de partidas + configs
- 03_STREAMING_Y_CLIPS/
- 04_MODS_Y_SHADERS/
- 05_HERRAMIENTAS_GAMER/
-   PERFILES_MANDO/              Perfiles Xbox/DualShock/8BitDo
-   instalar_mandos.sh
- 06_MEDIA_Y_WALLPAPERS/        Galeria + 12 wallpapers
- 07_DIARIO_MARIO/              Diario personal
- 08_JUEGOS_EXTRA/              13 juegos completos + scripts
- img/                         (temporal, imagenes sueltas)
- config.json                  Configuracion del servidor
- server.py                    Servidor principal
- escanear_roms.py             Escaner de ROMs
- benchmark.py                 Analisis de hardware
- Backup_Partidas.sh           Backup
- Restaurar_Partidas.sh        Restauracion
- guardar_configs.sh           Guardar configs emuladores
- restaurar_configs.sh         Restaurar configs emuladores
- limpiar_cache.sh             Limpieza
- comprimir_roms.sh            Compresion a CHD
- modo_fiesta.sh               Preparar PC para jugar
- modo_cine.sh                 Preparar PC para ver peliculas
- Iniciar.sh / Detener.sh
- ABRIR EL NINO.bat / .ico
- autorun.inf
- MANUAL.txt / README.md
- DOCUMENTO_TECNICO.md / ARCHITECTURE.md / CONTRIBUTING.md
- python_portable/             Python portable para Windows

---

## 3. SERVIDOR PYTHON (server.py)

### Caracteristicas
- Puerto: 8080 (configurable en config.json)
- Clase: ServidorConcurrente(socketserver.ThreadingTCPServer)
  - allow_reuse_address = True  (evita errores "Address already in use")
  - daemon_threads = True       (hilos se cierran al apagar)
- Registro de procesos: diccionario global procesos_activos con lock
- Detecta IP local al arrancar y la imprime en el log
- Lee configuracion de config.json

### Endpoints (todos GET)
- /launch/<emulador>       Lanzar emulador
- /juego/<nombre>          Lanzar juego extra
- /rom/<sis>/<arch>        Lanzar ROM escaneada
- /kill/<nombre>           Matar proceso
- /estado                  JSON de procesos activos
- /eventos                 Server-Sent Events (stream continuo con CPU/RAM)
- /escanear-roms           Reescanear ROMs
- /instalar-mandos         Instalar perfiles de mando
- /limpiar                 Limpieza
- /backup                  Backup manual
- /guardar-configs         Guardar configs emuladores
- /restaurar-configs       Restaurar configs
- /benchmark               Analisis de hardware
- /comprimir-roms          Compresion a CHD
- /modo-fiesta             Preparar PC para jugar
- /modo-cine               Preparar PC para peliculas
- /tecla/<key>             Enviar pulsacion de tecla (xdotool)
- /tecla-down/<key>        Mantener tecla pulsada
- /tecla-up/<key>          Soltar tecla
- else                     Servir archivos estaticos

---

## 4. ESCANER DE ROMS (escanear_roms.py)

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

## 5. SISTEMA SYSTEMD

### elnino.service (Servidor)
Description=Centro de Mando Gamer El Nino
After=network.target graphical-session.target
PartOf=graphical-session.target
Type=simple
WorkingDirectory=/run/media/urukais/PROYECTOS
ExecStart=/usr/bin/python3 /run/media/urukais/PROYECTOS/server.py
Restart=on-failure
RestartSec=3
Environment=DISPLAY=:1
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

### elnino-env.service (importa entorno grafico)
Type=oneshot
ExecStart=/bin/bash -c 'systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS && systemctl --user restart elnino.service'
RemainAfterExit=yes

### elnino-backup.timer (backup automatico)
OnCalendar=Sun *-*-* 20:00:00
Persistent=true
Unit=elnino-backup.service

### Comandos utiles
systemctl --user status elnino.service
systemctl --user restart elnino.service
journalctl --user -u elnino.service -n 30
systemctl --user list-timers elnino-backup.timer

---

## 6. LAUNCHER WEB (Funciones JS)

| Funcion | Descripcion |
|---------|-------------|
| toggleTV() | Modo TV (tecla T) |
| toggleAudio() | Silenciar/activar audio |
| hacerBackup() | Modal + /backup |
| hacerLimpieza() | Modal + /limpiar |
| guardarConfigs() | Modal + /guardar-configs |
| restaurarConfigs() | Modal + /restaurar-configs |
| instalarMandos() | Modal + /instalar-mandos |
| comprimirRoms() | Modal + /comprimir-roms |
| activarModoFiesta() | Modal + /modo-fiesta |
| activarModoCine() | Modal + /modo-cine |
| toggleSettings() | Abre panel configuracion |
| setTheme() | Cambia tema colores |
| setVolumen() | Ajusta volumen |
| editarRedes() | Modal editar redes sociales |
| toggleRadio() / togglePlayRadio() / cambiarEmisora() | Radio retro |
| toggleChatbot() / enviarChat() | Chatbot asistente |
| conectarSSE() | Conectar Server-Sent Events |
| actualizarRecursos() | Actualizar CPU/RAM en vivo |
| actualizarProcesosDesdeSSE() | Actualizar procesos |
| matarProceso() | Modal + /kill/<nombre> |
| cargarRoms() | Carga juegos.json |
| reescanearRoms() | Llama a /escanear-roms |
| kioscoKey() / kioscoBorrar() / kioscoEntrar() | Modo kiosco PIN |
| mostrarToast() | Notificacion cyberpunk |
| mostrarModal() | Modal con Promise (async/await) |

### Paginas secundarias
- manual.html              Manual de uso completo
- estadisticas.html        Graficos de actividad
- benchmark.html           Analisis de hardware
- retroachievements.html   Integracion con RetroAchievements
- mobile.html              Mando tactil para movil
- sorpresa.html            Pagina sorpresa con efectos
- privacidad.html / terminos.html / aviso_legal.html

---

## 7. SCRIPTS AUXILIARES

### escanear_roms.py
Escanea carpetas de ROMs y regenera juegos.json.

### benchmark.py
Lee CPU, RAM, GPU y recomienda configuracion por gama.

### Backup_Partidas.sh
Copia partidas de PCSX2, Dolphin, PPSSPP y RetroArch.

### Restaurar_Partidas.sh
Restaura el backup mas reciente.

### guardar_configs.sh / restaurar_configs.sh
Snapshots de configuraciones de emuladores en .tar.gz.

### limpiar_cache.sh
Borra __pycache__, backups antiguos (deja 5), locks, .bak, temporales.

### comprimir_roms.sh
Convierte ISOs de PS2/GameCube a .chd (40-60% menos espacio).

### modo_fiesta.sh
Cierra navegadores, sube volumen al 80%, desactiva salvapantallas, abre RetroArch.

### modo_cine.sh
Cierra navegadores, ajusta volumen al 60%, abre Kodi/Stremio/VLC.

### instalar_mandos.sh
Copia perfiles de mando a RetroArch, PCSX2, PPSSPP y Dolphin.

### Iniciar.sh / Detener.sh
Reinicia el servicio systemd, abre el navegador con el launcher.

---

## 8. NOTAS TECNICAS CRITICAS

- Shell fish NO soporta heredocs (<<EOF). Usar printf o python3 -c.
- Nunca pegar URLs en la terminal. Van al navegador.
- El disco se monta en /run/media/urukais/PROYECTOS/ (sin el "1").
- fish se atraganta con bloques largos. Pegar de uno en uno.
- Scripts .sh usan $(dirname "$0") para ser portables.
- grep en fish: usar -F para busquedas literales o escapar parentesis.
- Servicio systemd de usuario NO tiene entorno grafico por defecto.
  Por eso elnino-env.service importa las variables al iniciar sesion.
- RetroArch desde el servidor necesita:
  DISPLAY, WAYLAND_DISPLAY, XDG_RUNTIME_DIR, DBUS_SESSION_BUS_ADDRESS.
- Cuando escribimos JS con \n en Python, verificar sintaxis con node -c.
- El service worker NO cachea el HTML (solo iconos y manifest) para que
  los cambios se vean al recargar sin tener que limpiar cache.

---

## 9. HISTORIAL DE MEJORAS

### Sesion 1 (Infraestructura)
- PID management (registro de procesos activos)
- Kill switch (endpoint /kill + panel flotante)
- IP local (accesible desde movil)
- Script de limpieza + boton

### Sesion 2 (ROMs dinamicas)
- Escaner automatico de ROMs
- Seccion "Mi coleccion de juegos" auto-generada
- Boton Reescanear + Jugar funcional
- Servicio systemd con entorno grafico

### Sesion 3 (Mandos y portabilidad)
- Rutas dinamicas en todos los scripts
- Perfiles de mando (Xbox, DualShock, 8BitDo)
- Boton Mandos

### Fase 1
- Radio retro (4 emisoras: J-Pop, K-Pop, Gensokyo, Fallback)
- Self-healing de configs
- Modo kiosco con PIN
- Mando tactil virtual (mobile.html)

### Fase 2
- Benchmark de rendimiento
- RetroAchievements (esperando activacion de cuenta)
- PWA con Chromium (manifest + service worker)
- Compresion de ROMs a .chd

### Fase 3
- Server-Sent Events (CPU/RAM en vivo)
- Modo Fiesta / Cine
- Header ocultable al scroll
- 12 wallpapers nuevos

---

## 10. PENDIENTES

1. Probar el .bat en un Windows real
2. Activar cuenta de RetroAchievements (necesita 250 puntos o 14 dias)
3. Save State Timeline (Fase 3 pendiente)
4. Scraper de trailers (Fase 3 pendiente)

---

## COMANDOS DE REFERENCIA RAPIDA

Arrancar el servidor:
    bash /run/media/urukais/PROYECTOS/Iniciar.sh

Comprobar el servidor:
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/01_EL_NINO_LAUNCHER/index.html

Ver procesos activos:
    curl -s http://localhost:8080/estado

Ver CPU/RAM en vivo:
    curl -s -m 3 http://localhost:8080/eventos

Ver la IP local:
    ip route get 8.8.8.8

Regenerar el JSON de ROMs:
    python3 /run/media/urukais/PROYECTOS/escanear_roms.py

Ver logs del servidor:
    journalctl --user -u elnino.service -f

Verificar sintaxis JS:
    python3 -c "import re; c=open('/run/media/urukais/PROYECTOS/01_EL_NINO_LAUNCHER/index.html').read(); m=re.search(r'<script>(.*?)</script>', c, re.DOTALL); open('/tmp/launcher.js','w').write(m.group(1))"
    node -c /tmp/launcher.js

---

Centro de Mando Gamer "El Nino" - 2026 - Manuel Casimiro Carrasco
