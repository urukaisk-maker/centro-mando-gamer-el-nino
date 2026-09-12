#!/bin/bash
# ==========================================
#  INSTALADOR DE PERFILES DE MANDO - EL NIÑO
# ==========================================

# Encontrar la carpeta PERFILES_MANDO subiendo desde la ubicacion del script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PERFILES="$SCRIPT_DIR/PERFILES_MANDO"

if [ ! -d "$PERFILES" ]; then
    echo "ERROR: no encuentro PERFILES_MANDO en $SCRIPT_DIR"
    exit 1
fi

echo "========================================"
echo "  Instalar perfiles de mando - El Nino"
echo "========================================"
echo "Origen: $PERFILES"
echo ""

# --- RetroArch ---
echo "1. RetroArch..."
if [ -d "$HOME/.config/retroarch" ]; then
    mkdir -p "$HOME/.config/retroarch/autoconfig/udev"
    if [ -d "$PERFILES/retroarch" ]; then
        for f in "$PERFILES/retroarch/"*.cfg; do
            if [ -f "$f" ]; then
                cp "$f" "$HOME/.config/retroarch/autoconfig/udev/"
            fi
        done
        CONT=$(ls "$HOME/.config/retroarch/autoconfig/udev/"*.cfg 2>/dev/null | wc -l)
        echo "   OK - $CONT perfiles instalados en ~/.config/retroarch/autoconfig/udev/"
    else
        echo "   SKIP - no hay carpeta retroarch en el disco"
    fi
else
    echo "   SKIP - RetroArch no esta instalado en este PC"
fi

# --- PCSX2 ---
echo "2. PCSX2..."
if [ -d "$HOME/.config/PCSX2" ]; then
    mkdir -p "$HOME/.config/PCSX2/perfiles_mando"
    cp "$PERFILES/pcsx2/plantilla.txt" "$HOME/.config/PCSX2/perfiles_mando/" 2>/dev/null
    echo "   OK - plantilla copiada"
elif [ -d "$HOME/.local/share/PCSX2" ]; then
    mkdir -p "$HOME/.local/share/PCSX2/perfiles_mando"
    cp "$PERFILES/pcsx2/plantilla.txt" "$HOME/.local/share/PCSX2/perfiles_mando/" 2>/dev/null
    echo "   OK - plantilla copiada"
else
    echo "   SKIP - PCSX2 no instalado"
fi

# --- PPSSPP ---
echo "3. PPSSPP..."
if [ -d "$HOME/.config/ppsspp" ]; then
    mkdir -p "$HOME/.config/ppsspp/perfiles_mando"
    cp "$PERFILES/ppsspp/plantilla.txt" "$HOME/.config/ppsspp/perfiles_mando/" 2>/dev/null
    echo "   OK - plantilla copiada"
else
    echo "   SKIP - PPSSPP no instalado"
fi

# --- Dolphin ---
echo "4. Dolphin..."
if [ -d "$HOME/.config/dolphin-emu" ]; then
    mkdir -p "$HOME/.config/dolphin-emu/perfiles_mando"
    cp "$PERFILES/dolphin/plantilla.txt" "$HOME/.config/dolphin-emu/perfiles_mando/" 2>/dev/null
    echo "   OK - plantilla copiada"
elif [ -d "$HOME/.local/share/dolphin-emu" ]; then
    mkdir -p "$HOME/.local/share/dolphin-emu/perfiles_mando"
    cp "$PERFILES/dolphin/plantilla.txt" "$HOME/.local/share/dolphin-emu/perfiles_mando/" 2>/dev/null
    echo "   OK - plantilla copiada"
else
    echo "   SKIP - Dolphin no instalado"
fi

echo ""
echo "========================================"
echo "  Instalacion completada"
echo "========================================"
