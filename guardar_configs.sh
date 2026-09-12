#!/bin/bash
# ==========================================
#  GUARDAR CONFIGS DE EMULADORES - EL NIÑO
# ==========================================

DISCO="$(cd "$(dirname "$0")" && pwd)"
DESTINO="$DISCO/02_EMULADORES_Y_ROMS/SAVES_GUARDADOS/configs"
mkdir -p "$DESTINO"

FECHA=$(date +%Y%m%d_%H%M%S)
ARCHIVO="$DESTINO/configs_$FECHA.tar.gz"
TEMP=$(mktemp -d)

echo "========================================"
echo "  Guardar configs - El Nino"
echo "========================================"
echo "Destino: $ARCHIVO"
echo ""

# PCSX2
if [ -d "$HOME/.config/PCSX2" ]; then
    mkdir -p "$TEMP/PCSX2"
    cp -r "$HOME/.config/PCSX2/"* "$TEMP/PCSX2/" 2>/dev/null
    echo "OK PCSX2"
elif [ -d "$HOME/.local/share/PCSX2" ]; then
    mkdir -p "$TEMP/PCSX2"
    cp -r "$HOME/.local/share/PCSX2/"* "$TEMP/PCSX2/" 2>/dev/null
    echo "OK PCSX2"
else
    echo "-- PCSX2 no instalado"
fi

# Dolphin
if [ -d "$HOME/.config/dolphin-emu" ]; then
    mkdir -p "$TEMP/Dolphin"
    cp -r "$HOME/.config/dolphin-emu/"* "$TEMP/Dolphin/" 2>/dev/null
    echo "OK Dolphin"
elif [ -d "$HOME/.local/share/dolphin-emu" ]; then
    mkdir -p "$TEMP/Dolphin"
    cp -r "$HOME/.local/share/dolphin-emu/"* "$TEMP/Dolphin/" 2>/dev/null
    echo "OK Dolphin"
else
    echo "-- Dolphin no instalado"
fi

# PPSSPP
if [ -d "$HOME/.config/ppsspp" ]; then
    mkdir -p "$TEMP/PPSSPP"
    cp -r "$HOME/.config/ppsspp/"* "$TEMP/PPSSPP/" 2>/dev/null
    echo "OK PPSSPP"
else
    echo "-- PPSSPP no instalado"
fi

# RetroArch
if [ -d "$HOME/.config/retroarch" ]; then
    mkdir -p "$TEMP/RetroArch"
    cp "$HOME/.config/retroarch/retroarch.cfg" "$TEMP/RetroArch/" 2>/dev/null
    cp -r "$HOME/.config/retroarch/autoconfig" "$TEMP/RetroArch/" 2>/dev/null
    cp -r "$HOME/.config/retroarch/config" "$TEMP/RetroArch/" 2>/dev/null
    echo "OK RetroArch"
else
    echo "-- RetroArch no instalado"
fi

# Empaquetar
cd "$TEMP"
tar -czf "$ARCHIVO" ./* 2>/dev/null
cd "$DISCO"
rm -rf "$TEMP"

TAMANO=$(du -h "$ARCHIVO" | cut -f1)
echo ""
echo "========================================"
echo "  Configs guardadas"
echo "========================================"
echo "Archivo: $ARCHIVO"
echo "Tamano: $TAMANO"

# Limpiar snapshots antiguos (dejar los 5 mas recientes)
cd "$DESTINO"
CONT=0
for f in $(ls -t configs_*.tar.gz 2>/dev/null); do
    CONT=$((CONT + 1))
    if [ $CONT -gt 5 ]; then
        rm -f "$f"
        echo "Borrado antiguo: $f"
    fi
done
cd "$DISCO"

