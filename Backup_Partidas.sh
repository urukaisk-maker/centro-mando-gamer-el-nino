#!/bin/bash
# ==========================================
#  BACKUP DE PARTIDAS - EL NIÑO
# ==========================================

DISCO="$(cd "$(dirname "$0")" && pwd)"
BACKUP="$DISCO/02_EMULADORES_Y_ROMS/SAVES_GUARDADOS/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"

echo "========================================"
echo "  Backup de partidas - El Nino"
echo "========================================"
echo "Destino: $BACKUP"
echo ""

# --- PCSX2 (PS2) ---
if [ -d "$HOME/.config/PCSX2/memcards" ]; then
    mkdir -p "$BACKUP/PCSX2"
    cp -r "$HOME/.config/PCSX2/memcards/"* "$BACKUP/PCSX2/" 2>/dev/null
    echo "OK PCSX2"
elif [ -d "$HOME/.local/share/PCSX2/memcards" ]; then
    mkdir -p "$BACKUP/PCSX2"
    cp -r "$HOME/.local/share/PCSX2/memcards/"* "$BACKUP/PCSX2/" 2>/dev/null
    echo "OK PCSX2"
else
    echo "-- PCSX2: sin partidas"
fi

# --- Dolphin (GC/Wii) ---
if [ -d "$HOME/.local/share/dolphin-emu/GC" ]; then
    mkdir -p "$BACKUP/Dolphin"
    cp -r "$HOME/.local/share/dolphin-emu/GC/"* "$BACKUP/Dolphin/" 2>/dev/null
    cp -r "$HOME/.local/share/dolphin-emu/Wii/"* "$BACKUP/Dolphin/" 2>/dev/null
    echo "OK Dolphin"
elif [ -d "$HOME/.dolphin-emu/GC" ]; then
    mkdir -p "$BACKUP/Dolphin"
    cp -r "$HOME/.dolphin-emu/GC/"* "$BACKUP/Dolphin/" 2>/dev/null
    echo "OK Dolphin"
else
    echo "-- Dolphin: sin partidas"
fi

# --- PPSSPP (PSP) ---
if [ -d "$HOME/.config/ppsspp/PSP/SAVEDATA" ]; then
    mkdir -p "$BACKUP/PPSSPP"
    cp -r "$HOME/.config/ppsspp/PSP/SAVEDATA/"* "$BACKUP/PPSSPP/" 2>/dev/null
    echo "OK PPSSPP"
else
    echo "-- PPSSPP: sin partidas"
fi

# --- RetroArch ---
if [ -d "$HOME/.config/retroarch/saves" ]; then
    mkdir -p "$BACKUP/RetroArch/saves"
    cp -r "$HOME/.config/retroarch/saves/"* "$BACKUP/RetroArch/saves/" 2>/dev/null
    echo "OK RetroArch saves"
fi
if [ -d "$HOME/.config/retroarch/states" ]; then
    mkdir -p "$BACKUP/RetroArch/states"
    cp -r "$HOME/.config/retroarch/states/"* "$BACKUP/RetroArch/states/" 2>/dev/null
    echo "OK RetroArch states"
fi

# --- Diario de Mario ---
if ls "$HOME/Descargas/diario_mario_"*.json >/dev/null 2>&1; then
    mkdir -p "$BACKUP/Diario"
    cp $HOME/Descargas/diario_mario_*.json "$BACKUP/Diario/" 2>/dev/null
    echo "OK Diario exportado"
fi

echo ""
echo "========================================"
echo "  Backup completado"
echo "========================================"
echo "Ubicacion: $BACKUP"
