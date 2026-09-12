# Propuestas de Mejora - Centro de Mando Gamer "El Nino"

Documento con ideas y sugerencias para evolucionar el proyecto.
Guardado el 13 de septiembre de 2026.

---

## FASE 1 - Limpieza y Arquitectura de Codigo

### Objetivo
Dejar el codigo mantenible y escalable con el minimo esfuerzo.

### Mejoras
1. **Variables CSS (:root):** Centralizar colores, sombras, brillos y gradientes
   en variables al inicio del CSS. Permite cambiar la paleta editando una linea.
2. **Semantica HTML:** Sustituir <div> genericos por <section>, <header>, <nav>,
   y usar <button> para controles clicables. Anadir :focus-visible para teclado.
3. **Organizacion CSS:** Agrupar reglas por bloques (Base, Layout, Componentes)
   y comentar secciones clave del JavaScript.

---

## FASE 2 - Pulido de Experiencia de Usuario (UX/UI)

### Objetivo
Hacer que la interfaz se sienta tactil, viva y profesional.

### Mejoras
1. **Estados de Botones:** Anadir efecto "hundimiento" (:active) y estado
   .active para marcar que boton esta en uso.
2. **Microinteracciones:** Transiciones suaves (box-shadow .15s, transform .05s)
   y leve escalado (scale(0.995)) al hacer clic.
3. **Gestion de Audio:** Evitar solapamiento de sonidos con currentTime = 0.
   Anadir controles de volumen y mute.

---

## FASE 3 - Nuevas Funcionalidades

### Objetivo
Anadir utilidad real sin saturar el panel.

### Mejoras
1. **Reloj y Estado del Sistema:** Reloj digital en tiempo real (HH:MM:SS) y
   barra de estado inferior (SISTEMA: OPERATIVO | MODO: NORMAL).
2. **Pantalla de Arranque:** Fade-in con texto "INICIALIZANDO SISTEMA..."
   al cargar la pagina.
3. **Ventanas Modales:** Emergentes con bordes glow para "Acerca de" y
   "Configuracion", usando localStorage para recordar preferencias.
4. **Modo Alerta:** Interruptor que cambia el esquema de cian a rojo/ambar
   para simular alerta del centro de mando.

---

## FASE 4 - Presentacion en GitHub

### Objetivo
Hacer que el repositorio destaque ante otros desarrolladores.

### Mejoras
1. **README Profesional:** Descripcion clara, tecnologias, instrucciones de
   instalacion y preview.png del centro de mando.
2. **Favicon y Metadatos:** Icono personalizado + meta tags (titulo, descripcion,
   theme-color) para movil y redes sociales.
3. **Demo Banner Animado (GIF/MP4):** GIF corto mostrando la interfaz Cyberpunk,
   las particulas, la navegacion y la apertura de un juego.
4. **Matriz de Compatibilidad:** Tabla visual con badges mostrando estado de
   cada modulo (PCSX2, Dolphin, juegos PC...).
5. **Diagrama Mermaid.js:** Explicacion visual de las capas:
   Launcher Web -> Servidor Python -> Scripts Bash/Batch -> Emuladores.
6. **Licencia MIT/GPLv3 + CONTRIBUTING.md:** Aspecto de software profesional.

---

## MEJORAS EXTRA - "Malla de Seguridad"

### Self-Healing del sistema
- Script `restaurar_fabrica.sh` que devuelve las configuraciones de los
  emuladores a su estado inicial con un clic. (YA IMPLEMENTADO como
  `guardar_configs.sh` + `restaurar_configs.sh`)

---

## PLAN DE ACCION SUGERIDO

### Hoy
- Crear variables CSS
- Mejorar README

### Esta semana
- Anadir estados de botones
- Reloj de sistema

### Futuro
- Explorar modales
- Secuencia de arranque
- Demo banner animado
- Licencia y CONTRIBUTING

---

*Documento guardado para futuras sesiones de desarrollo.*
