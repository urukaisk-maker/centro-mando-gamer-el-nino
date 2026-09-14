#!/bin/bash
# ==========================================
#  LIMPIEZA Y MANTENIMIENTO - EL NIÑO
# ==========================================

DISCO="$(cd "$(dirname "$0")" && pwd)"
ESPACIO_ANTES=$(du -sm "$DISCO" 2>/dev/null | cut -f1)

echo "========================================"
echo "  Limpieza y mantenimiento - El Nino"
echo "========================================"
echo "Disco: $DISCO"
echo "Espacio antes: ${ESPACIO_ANTES} MB"
echo ""

# 1. Limpiar __pycache__ y .pyc
echo "1. Limpiando cache de Python..."
find "$DISCO" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$DISCO" -type f -name "*.pyc" -delete 2>/dev/null
echo "   OK"

# 2. Limpiar backups antiguos (dejar solo los 5 mas recientes)
echo "2. Limpiando backups antiguos..."
BACKUP_DIR="$DISCO/02_EMULADORES_Y_ROMS/SAVES_GUARDADOS"
if [ -d "$BACKUP_DIR" ]; then
    cd "$BACKUP_DIR"
    BACKUPS=$(ls -td backup_* 2>/dev/null)
    CONT=0
    for b in $BACKUPS; do
        CONT=$((CONT+1))
        if [ $CONT -gt 5 ]; then
            rm -rf "$b"
            echo "   Borrado: $b"
        fi
    done
    if [ $CONT -le 5 ]; then
        echo "   Solo hay $CONT backups, no se borra ninguno"
    fi
    cd "$DISCO"
else
    echo "   No hay carpeta de backups"
fi

# 3. Limpiar locks de LibreOffice / Kate / etc
echo "3. Limpiando archivos de bloqueo..."
find "$DISCO" -type f -name ".~lock.*" -delete 2>/dev/null
find "$DISCO" -type f -name "*.kate-swp" -delete 2>/dev/null
find "$DISCO" -type f -name "*.save" -delete 2>/dev/null
echo "   OK"

# 4. Limpiar logs temporales del servidor
echo "4. Limpiando logs temporales..."
rm -f /tmp/elnino_server.log 2>/dev/null
echo "   OK"

# 5. Limpiar archivos .bak
echo "5. Limpiando archivos .bak..."
find "$DISCO" -type f -name "*.bak" ! -path "*/squashfs-root/*" ! -path "*/python_portable/*" -delete 2>/dev/null
echo "   OK"

# 6. Limpiar archivos temporales del navegador si los hay
echo "6. Limpiando archivos temporales..."
find "$DISCO" -type f -name "*.tmp" -delete 2>/dev/null
find "$DISCO" -type f -name "*.temp" -delete 2>/dev/null
find "$DISCO" -type f -name "Thumbs.db" -delete 2>/dev/null
find "$DISCO" -type f -name ".DS_Store" -delete 2>/dev/null
echo "   OK"

ESPACIO_DESPUES=$(du -sm "$DISCO" 2>/dev/null | cut -f1)
LIBERADO=$((ESPACIO_ANTES - ESPACIO_DESPUES))

echo ""
echo "========================================"
echo "  Limpieza completada"
echo "========================================"
echo "Espacio antes:    ${ESPACIO_ANTES} MB"
echo "Espacio despues:  ${ESPACIO_DESPUES} MB"
echo "Espacio liberado: ${LIBERADO} MB"
echo ""
