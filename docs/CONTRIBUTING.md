# CONTRIBUTING - El Nino

Guia para quien quiera entender o modificar este proyecto.

## FILOSOFIA

Proyecto personal de regalo. No es producto comercial.

Principios:
1. Portabilidad total (Linux/Windows, sin instalacion)
2. Cero dependencias externas (Python 3 + Bash)
3. Sin frameworks JS (vanilla puro)
4. Todo local (sin servidores, sin telemetria)
5. Regalo antes que producto

## ESTRUCTURA DEL CODIGO

### Backend (server.py)
Servidor HTTP que sirve archivos y expone endpoints.

Para anadir un endpoint:
1. Anade elif self.path.startswith("/nuevo") en do_GET
2. Procesa la peticion
3. Devuelve respuesta

### Frontend (index.html)
Todo en un archivo: CSS en style, HTML, JS en script.

Para anadir una tarjeta:
1. Busca grid-tarjetas en el HTML
2. Copia el patron de otra tarjeta
3. Cambia titulo y enlace

Para anadir una funcion JS:
1. Escribe la funcion en el script final
2. Usa mostrarToast() y mostrarModal() para feedback
3. Engancha con onclick="miFuncion()"

### Scripts (.sh)
Todos usan $(dirname "$0") para ser portables.
NUNCA uses rutas absolutas en los .sh.

## CONVENCIONES

### Nombres
- Archivos: snake_case.py, PascalCase.sh
- Variables Python: snake_case
- Variables JS: camelCase
- IDs CSS: kebab-case

### Colores
- Cian: #00f0ff (primario)
- Rosa: #ff00ff (secundario)
- Fondo: #0a0a0f
- Tarjetas: #1a1a24
- Texto: #e0e0e0

### Idioma
- Codigo: ingles
- Comentarios y UI: espanol

## COMO PROBAR CAMBIOS

### Frontend
1. Edita index.html
2. Limpia cache: pkill -9 brave; rm -rf ~/.cache/BraveSoftware/
3. Recarga con Ctrl+Shift+R

### Backend
1. Edita server.py
2. Verifica: python3 -c "import ast; ast.parse(open('server.py').read())"
3. Reinicia: systemctl --user restart elnino.service
4. Comprueba: curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/

### Scripts
Prueba a mano: bash /ruta/al/script.sh

## ERRORES COMUNES

### Address already in use
pkill -9 -f server.py; systemctl --user restart elnino.service

### RetroArch no arranca desde el servidor
Verifica: systemctl --user status elnino-env.service
Deberia estar active.

### fish no soporta heredocs
Usa printf o python3 -c en lugar de <<EOF

### Los cambios no se ven en el navegador
Cache. Limpia con: rm -rf ~/.cache/BraveSoftware/

## APORTACIONES

1. Abre un issue en GitHub explicando la idea
2. Si es codigo, haz fork y PR
3. No hay prisa ni compromiso: es un regalo personal

## LICENCIA

- Codigo propio: MIT (uso libre)
- Juegos: licencias propias (GPL, MIT, etc.)
- Wallpapers: Unsplash (uso libre)
- Emuladores: licencias propias

---

Centro de Mando Gamer "El Nino" - 2026 - Manuel Casimiro Carrasco
