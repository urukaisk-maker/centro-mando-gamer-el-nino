#!/bin/bash
# ==========================================
#  RESTAURAR PARTIDAS - EL NIÑO
# ==========================================
# Copia la última copia de seguridad de vuelta a
# las carpetas de los emuladores.

DISCO="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$DISCO/02_EMULADORES_Y_ROMS/SAVES_GUARDADOS"

# Encontrar el backup más reciente
ULTIMO=$(ls -td "$BACKUP_DIR"/backup_* 2>/dev/null | head -1)

if [ -z "$ULTIMO" ]; then
    echo "❌ No hay backups en:"
    echo "   $BACKUP_DIR"
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "========================================"
echo "  Restaurar partidas - El Niño"
echo "========================================"
echo "Backup origen: $ULTIMO"
echo ""
read -p "¿Restaurar? (s/n): " resp
if [ "$resp" != "s" ]; then
    echo "Cancelado."
    exit 0
fi

# PCSX2
if [ -d "$ULTIMO/PCSX2" ]; then
    mkdir -p "$HOME/.config/PCSX2/memcards"
    cp -r "$ULTIMO/PCSX2/"* "$HOME/.config/PCSX2/memcards/" 2>/dev/null
    echo "✅ PCSX2 restaurado"
fi

# Dolphin
if [ -d "$ULTIMO/Dolphin" ]; then
    mkdir -p "$HOME/.local/share/dolphin-emu/GC"
    cp -r "$ULTIMO/Dolphin/"* "$HOME/.local/share/dolphin-emu/GC/" 2>/dev/null
    echo "✅ Dolphin restaurado"
fi

# PPSSPP
if [ -d "$ULTIMO/PPSSPP" ]; then
    mkdir -p "$HOME/.config/ppsspp/PSP/SAVEDATA"
    cp -r "$ULTIMO/PPSSPP/"* "$HOME/.config/ppsspp/PSP/SAVEDATA/" 2>/dev/null
    echo "✅ PPSSPP restaurado"
fi

# RetroArch
if [ -d "$ULTIMO/RetroArch" ]; then
    mkdir -p "$HOME/.config/retroarch/saves"
    mkdir -p "$HOME/.config/retroarch/states"
    cp -r "$ULTIMO/RetroArch/saves/"* "$HOME/.config/retroarch/saves/" 2>/dev/null
    cp -r "$ULTIMO/RetroArch/states/"* "$HOME/.config/retroarch/states/" 2>/dev/null
    echo "✅ RetroArch restaurado"
fi

echo ""
echo "✅ Restauración completada."
read -p "Pulsa Enter para salir..."
