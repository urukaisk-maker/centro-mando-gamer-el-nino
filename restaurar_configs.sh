#!/bin/bash
# ==========================================
#  RESTAURAR CONFIGS DE EMULADORES - EL NIÑO
# ==========================================

DISCO="$(cd "$(dirname "$0")" && pwd)"
ORIGEN="$DISCO/02_EMULADORES_Y_ROMS/SAVES_GUARDADOS/configs"

# Encontrar el mas reciente
ULTIMO=$(ls -t "$ORIGEN"/configs_*.tar.gz 2>/dev/null | head -1)

if [ -z "$ULTIMO" ]; then
    echo "ERROR: no hay snapshots en $ORIGEN"
    exit 1
fi

echo "========================================"
echo "  Restaurar configs - El Nino"
echo "========================================"
echo "Origen: $ULTIMO"
echo ""

TEMP=$(mktemp -d)
cd "$TEMP"
tar -xzf "$ULTIMO"

# PCSX2
if [ -d "$TEMP/PCSX2" ]; then
    mkdir -p "$HOME/.config/PCSX2"
    cp -r "$TEMP/PCSX2/"* "$HOME/.config/PCSX2/" 2>/dev/null
    echo "OK PCSX2 restaurado"
fi

# Dolphin
if [ -d "$TEMP/Dolphin" ]; then
    mkdir -p "$HOME/.config/dolphin-emu"
    cp -r "$TEMP/Dolphin/"* "$HOME/.config/dolphin-emu/" 2>/dev/null
    echo "OK Dolphin restaurado"
fi

# PPSSPP
if [ -d "$TEMP/PPSSPP" ]; then
    mkdir -p "$HOME/.config/ppsspp"
    cp -r "$TEMP/PPSSPP/"* "$HOME/.config/ppsspp/" 2>/dev/null
    echo "OK PPSSPP restaurado"
fi

# RetroArch
if [ -d "$TEMP/RetroArch" ]; then
    mkdir -p "$HOME/.config/retroarch"
    cp "$TEMP/RetroArch/retroarch.cfg" "$HOME/.config/retroarch/" 2>/dev/null
    cp -r "$TEMP/RetroArch/autoconfig" "$HOME/.config/retroarch/" 2>/dev/null
    cp -r "$TEMP/RetroArch/config" "$HOME/.config/retroarch/" 2>/dev/null
    echo "OK RetroArch restaurado"
fi

cd "$DISCO"
rm -rf "$TEMP"

echo ""
echo "========================================"
echo "  Configs restauradas"
echo "========================================"


