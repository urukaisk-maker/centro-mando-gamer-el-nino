#!/bin/bash
# ==========================================
#  COMPRIMIR ROMS A CHD - EL NIÑO
# ==========================================
# Convierte ISOs de PS2/GameCube/Wii a formato .chd
# (ocupa un 40-60% menos sin perder calidad)

DISCO="$(cd "$(dirname "$0")" && pwd)"
ROMS_DIR="$DISCO/02_EMULADORES_Y_ROMS"

# Carpetas a escanear
CARPETAS=("01_PS2" "03_GAMECUBE_WII")

# Extensiones de ISO
EXTENSIONES=("iso" "gcm" "wbfs")

# Configuracion
BORRAR_ORIGINAL=0  # 1 = borrar ISO al terminar, 0 = conservar
MODO_PRUEBA=0      # 1 = solo muestra que haria, no convierte

# Comprobar chdman
if ! command -v chdman >/dev/null 2>&1; then
    echo "ERROR: chdman no esta instalado"
    echo "Instalalo con: sudo pacman -S mame-tools"
    exit 1
fi

echo "========================================"
echo "  Comprimir ROMs a CHD - El Nino"
echo "========================================"
echo ""

# Contar ISOs totales
TOTAL=0
for carpeta in "${CARPETAS[@]}"; do
    ruta="$ROMS_DIR/$carpeta"
    if [ -d "$ruta" ]; then
        for ext in "${EXTENSIONES[@]}"; do
            num=$(find "$ruta" -type f -iname "*.$ext" 2>/dev/null | wc -l)
            TOTAL=$((TOTAL + num))
        done
    fi
done

if [ "$TOTAL" -eq 0 ]; then
    echo "No hay ISOs para comprimir."
    echo ""
    echo "Anade juegos a:"
    for carpeta in "${CARPETAS[@]}"; do
        echo "  - 02_EMULADORES_Y_ROMS/$carpeta/"
    done
    exit 0
fi

echo "ISOs encontradas: $TOTAL"
echo "Espacio antes:"
du -sh "$ROMS_DIR" 2>/dev/null | cut -f1 | sed 's/^/  /'
echo ""

# Procesar cada carpeta
AHORRADO=0
CONVERTIDAS=0

for carpeta in "${CARPETAS[@]}"; do
    ruta="$ROMS_DIR/$carpeta"
    [ ! -d "$ruta" ] && continue

    echo "--- Procesando: $carpeta ---"

    for ext in "${EXTENSIONES[@]}"; do
        # Buscar archivos y procesar uno a uno
        find "$ruta" -type f -iname "*.$ext" 2>/dev/null | while read -r archivo; do
            nombre=$(basename "$archivo")
            sin_ext="${archivo%.*}"
            archivo_chd="${sin_ext}.chd"

            # Si ya existe el CHD, saltar
            if [ -f "$archivo_chd" ]; then
                echo "SKIP: ya existe $nombre.chd"
                continue
            fi

            tamano_iso=$(du -m "$archivo" 2>/dev/null | cut -f1)
            echo ""
            echo "Convirtiendo: $nombre ($tamano_iso MB)"

            if [ "$MODO_PRUEBA" -eq 1 ]; then
                echo "  [MODO PRUEBA] Se convertiria a: $(basename "$archivo_chd")"
                continue
            fi

            # Detectar tipo: CD o DVD (PS2 y GC suelen ser DVD)
            # Los juegos de PS2 de menos de 700 MB suelen ser CD
            if [ "$tamano_iso" -lt 750 ]; then
                TIPO="createcd"
            else
                TIPO="createdvd"
            fi

            # Convertir
            chdman $TIPO -i "$archivo" -o "$archivo_chd" > /dev/null 2>&1

            if [ -f "$archivo_chd" ]; then
                tamano_chd=$(du -m "$archivo_chd" 2>/dev/null | cut -f1)
                ahorro=$((tamano_iso - tamano_chd))
                echo "  OK: $tamano_iso MB -> $tamano_chd MB (ahorro: $ahorro MB)"

                if [ "$BORRAR_ORIGINAL" -eq 1 ]; then
                    rm -f "$archivo"
                    echo "  Original borrado"
                else
                    echo "  Original conservado (edita BORRAR_ORIGINAL=1 para borrarlo)"
                fi
            else
                echo "  ERROR: no se pudo convertir"
            fi
        done
    done
done

echo ""
echo "========================================"
echo "  Compresion terminada"
echo "========================================"
echo "Espacio despues:"
du -sh "$ROMS_DIR" 2>/dev/null | cut -f1 | sed 's/^/  /'
echo ""
echo "Nota: el proceso puede tardar 5-15 min por juego."
echo "Para borrar las ISOs originales, edita BORRAR_ORIGINAL=1"
