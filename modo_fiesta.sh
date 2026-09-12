#!/bin/bash
# ==========================================
#  MODO FIESTA - EL NIÑO
# ==========================================
# Prepara el PC para jugar con amigos

echo "========================================"
echo "  MODO FIESTA - El Nino"
echo "========================================"
echo ""

# Cerrar navegadores y apps pesadas
echo "1. Cerrando apps pesadas..."
pkill -f firefox 2>/dev/null && echo "   Firefox cerrado"
pkill -f chromium 2>/dev/null && echo "   Chromium cerrado"
pkill -f brave 2>/dev/null && echo "   Brave cerrado"
pkill -f thunderbird 2>/dev/null && echo "   Thunderbird cerrado"
pkill -f libreoffice 2>/dev/null && echo "   LibreOffice cerrado"
echo "   OK"

# Subir volumen al 80%
echo "2. Subiendo volumen..."
if command -v amixer >/dev/null 2>&1; then
    amixer set Master 80% >/dev/null 2>&1 && echo "   Volumen al 80%"
elif command -v pactl >/dev/null 2>&1; then
    pactl set-sink-volume @DEFAULT_SINK@ 80% >/dev/null 2>&1 && echo "   Volumen al 80%"
fi

# Desactivar salvapantallas
echo "3. Desactivando salvapantallas..."
if command -v xset >/dev/null 2>&1; then
    xset s off 2>/dev/null
    xset -dpms 2>/dev/null
    echo "   Salvapantallas desactivado (temporal)"
fi

# Abrir RetroArch si esta instalado
echo "4. Abriendo RetroArch..."
if command -v retroarch >/dev/null 2>&1; then
    nohup retroarch >/dev/null 2>&1 &
    echo "   RetroArch abierto"
else
    echo "   RetroArch no instalado, abriendo launcher"
    nohup xdg-open "http://localhost:8080/01_EL_NINO_LAUNCHER/index.html" >/dev/null 2>&1 &
fi

echo ""
echo "========================================"
echo "  MODO FIESTA ACTIVADO"
echo "========================================"
echo "Todo listo para jugar."
