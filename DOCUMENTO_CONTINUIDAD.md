# DOCUMENTO DE CONTINUIDAD – PROYECTO EL NIÑO

## Entorno
- Disco: /dev/sdb1 — exfat — UUID EEDF-BB48 — etiqueta PROYECTOS
- Ruta montaje REAL: /run/media/urukais/PROYECTOS (SIN el 1)
- Montar si no está: udisksctl mount -b /dev/sdb1
- Shell: fish — NO heredocs, usar printf o python3 -c
- Servidor: python3 server.py (puerto 8080)

## Completado (10 sep 2026)
- Launcher web Cyberpunk funcional
- server.py estable puerto 8080
- Emuladores OK: PCSX2, PPSSPP, Dolphin, mGBA, RetroArch+fceumm
- Fix Wayland mGBA: export QT_QPA_PLATFORM=xcb en mGBA.sh y mGBA_Tobu.sh
- Zombies /tmp/.mount_mGBA-* limpiados
- ROMs: Famidash.nes (786K) + 2048.nes (16K) funcionando
- README.md creado

## Pendiente
- tobutobugirl.gba (script listo)
- BIOS PS2 y GameCube
- Probar Iniciar.bat en Windows
- Personalizar launcher: foto, parallax, particulas, icono.ico
- RetroAchievements
- Repo publico GitHub

## Notas criticas
1. Fish shell, NUNCA bash. Nada de heredocs.
2. grep con pipe escapado falla → usar grep -E
3. Verificar SIEMPRE lsblk -f antes de operar
4. Disco real sdb1, NO sdd1. Ruta real PROYECTOS, NO PROYECTOS1.
5. URLs GitHub → validar con api.github.com/repos/USUARIO/REPO/releases/latest
6. itch.io pago opcional → buscar en GitHub/Bitbucket
7. Avisos Net::DBus y xset = ruido inofensivo de xdg-screensaver
8. mGBA Wayland: siempre export QT_QPA_PLATFORM=xcb antes de lanzar
