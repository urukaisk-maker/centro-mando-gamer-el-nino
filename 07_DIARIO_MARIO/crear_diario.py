import os

html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Diario de Mario</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0f;
            color: #e0e6ed;
            min-height: 100vh;
            background-image: radial-gradient(circle at 20% 20%, rgba(0, 240, 255, 0.4), transparent),
                              radial-gradient(circle at 80% 80%, rgba(255, 0, 255, 0.4), transparent);
            background-attachment: fixed;
        }

        /* Pantalla de bienvenida */
        #bienvenida {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
            padding: 2rem;
        }
        #bienvenida h1 {
            color: #00f0ff;
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 0 0 20px #00f0ff;
        }
        #bienvenida p {
            color: #aaa;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        #bienvenida button {
            background: #00f0ff;
            color: #000;
            border: none;
            padding: 1rem 2.5rem;
            font-size: 1.3rem;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
        }

        /* Pantalla principal */
        #principal {
            display: none;
        }
        header {
            background: rgba(26, 26, 36, 0.9);
            border-bottom: 2px solid #00f0ff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        header h1 {
            color: #00f0ff;
            margin: 0;
            font-size: 1.5rem;
        }
        header button {
            background: #00f0ff;
            color: #000;
            border: none;
            padding: 0.6rem 1.4rem;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }
        header button:hover {
            background: #ff00ff;
            color: #fff;
        }

        /* Layout */
        .layout {
            max-width: 1300px;
            margin: 2rem auto;
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 2rem;
            padding: 0 1rem;
        }
        .sidebar {
            background: #1a1a24;
            border-radius: 12px;
            padding: 1.5rem;
            height: fit-content;
        }
        .sidebar h2 {
            color: #00f0ff;
            margin-bottom: 1rem;
            border-bottom: 1px solid #2a2a3a;
            padding-bottom: 0.5rem;
        }
        .cat-list {
            list-style: none;
            margin-bottom: 2rem;
        }
        .cat-list li {
            background: #12121a;
            border: 1px solid #2a2a3a;
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.4rem;
            cursor: pointer;
            font-size: 0.95rem;
            color: #e0e6ed;
        }
        .cat-list li:hover {
            border-color: #00f0ff;
            background: #22222e;
        }

        /* Calendario */
        .cal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .cal-header button {
            background: #12121a;
            border: 1px solid #2a2a3a;
            color: #e0e6ed;
            border-radius: 6px;
            padding: 0.3rem 0.7rem;
            cursor: pointer;
        }
        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.2rem;
            text-align: center;
        }
        .cal-weekday {
            font-weight: bold;
            color: #8899aa;
            font-size: 0.75rem;
            padding: 0.3rem 0;
        }
        .cal-day {
            padding: 0.4rem 0;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
        }
        .cal-day:hover {
            background: #00f0ff;
            color: #000;
        }
        .cal-day.selected {
            background: #ff00ff;
            color: #fff;
        }
        .cal-day.today {
            border: 1px solid #00f0ff;
        }
        .cal-day.empty {
            cursor: default;
        }

        /* Entradas */
        .main {
            background: #1a1a24;
            border-radius: 12px;
            padding: 2rem;
        }
        .entrada {
            background: #12121a;
            border-left: 4px solid #00f0ff;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
        }
        .entrada h4 {
            color: #00f0ff;
            margin-bottom: 0.3rem;
        }
        .entrada p {
            color: #aaa;
            font-size: 0.95rem;
        }
        .entrada .fecha {
            display: inline-block;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #00f0ff;
            background: rgba(0, 240, 255, 0.1);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
        }
        .entrada .categoria {
            display: inline-block;
            margin-left: 0.5rem;
            font-size: 0.8rem;
            color: #ff00ff;
            background: rgba(255, 0, 255, 0.1);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
        }

        /* Botones */
        .botones {
            display: flex;
            gap: 0.8rem;
            margin-top: 1.5rem;
        }
        .btn {
            background: #00f0ff;
            color: #000;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover {
            background: #ff00ff;
            color: #fff;
        }

        /* Footer */
        footer {
            text-align: center;
            padding: 1.5rem;
            border-top: 1px solid #2a2a3a;
            margin-top: 2rem;
            color: #888;
            font-size: 0.85rem;
        }
        footer a {
            color: #00f0ff;
            text-decoration: none;
            margin: 0 6px;
        }
    </style>
</head>
<body>
    <div id="bienvenida">
        <h1>¡HOLA, MARIO!</h1>
        <p>Este es tu diario personal. Aquí puedes escribir tus pensamientos, aventuras y recuerdos.</p>
        <button onclick="entrar()">🚀 Entrar al diario</button>
    </div>
    <div id="principal">
        <header>
            <h1>📖 DIARIO DE MARIO</h1>
            <button onclick="window.scrollTo({top:0,behavior:'smooth'})">🏠 Inicio</button>
        </header>
        <div class="layout">
            <aside class="sidebar">
                <h2>📂 Categorías</h2>
                <ul class="cat-list">
                    <li onclick="filtrar('Todas')">📋 Todas</li>
                    <li onclick="filtrar('Vida Diaria')">☀️ Vida Diaria</li>
                    <li onclick="filtrar('Reflexiones')">💭 Reflexiones</li>
                    <li onclick="filtrar('Metas y Sueños')">🎯 Metas y Sueños</li>
                    <li onclick="filtrar('Relaciones')">❤️ Relaciones</li>
                    <li onclick="filtrar('Salud y Bienestar')">🌱 Salud y Bienestar</li>
                    <li onclick="filtrar('Trabajo y Estudios')">💼 Trabajo y Estudios</li>
                    <li onclick="filtrar('Aficiones')">🎮 Aficiones</li>
                    <li onclick="filtrar('Eventos Especiales')">🎉 Eventos Especiales</li>
                    <li onclick="filtrar('Finanzas')">💰 Finanzas</li>
                    <li onclick="filtrar('Espiritualidad')">✨ Espiritualidad</li>
                </ul>

                <h2>🗓️ Calendario</h2>
                <div class="cal-header">
                    <button onclick="cambiarMes(-1)">‹</button>
                    <strong id="tituloMes"></strong>
                    <button onclick="cambiarMes(1)">›</button>
                </div>
                <div class="cal-grid" id="calGrid"></div>
            </aside>

            <main class="main">
                <h2 id="tituloSeccion" style="color:#ff00ff;margin-bottom:1rem">Todas las entradas</h2>
                <div id="contenedorEntradas">
                    <div class="entrada" data-cat="Vida Diaria">
                        <h4>Inicio del proyecto</h4>
                        <p>Hoy he comenzado a diseñar el Centro de Mando Gamer El Niño. La idea es tener todo en un solo disco: emuladores, streaming, mods y un diario personal.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Vida Diaria</span>
                    </div>
                    <div class="entrada" data-cat="Aficiones">
                        <h4>Shadow of the Colossus</h4>
                        <p>Uno de los juegos más épicos de PS2. Gráficos impresionantes para su época y una historia que emociona.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Aficiones</span>
                    </div>
                    <div class="entrada" data-cat="Aficiones">
                        <h4>Mario Kart Wii</h4>
                        <p>El clásico de las carreras. Perfecto para jugar en familia.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Aficiones</span>
                    </div>
                    <div class="entrada" data-cat="Reflexiones">
                        <h4>Pensamiento del día</h4>
                        <p>A veces lo más difícil es empezar, pero una vez que empiezas todo fluye.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Reflexiones</span>
                    </div>
                    <div class="entrada" data-cat="Metas y Sueños">
                        <h4>Ampliar biblioteca</h4>
                        <p>Quiero añadir más juegos de GameCube al disco.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Metas y Sueños</span>
                    </div>
                    <div class="entrada" data-cat="Relaciones">
                        <h4>Llamada con un amigo</h4>
                        <p>He llamado a un amigo y hemos estado hablando de videojuegos.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Relaciones</span>
                    </div>
                    <div class="entrada" data-cat="Salud y Bienestar">
                        <h4>Ejercicio</h4>
                        <p>He salido a caminar 30 minutos después de comer.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Salud y Bienestar</span>
                    </div>
                    <div class="entrada" data-cat="Trabajo y Estudios">
                        <h4>Avance del proyecto</h4>
                        <p>He estado organizando las carpetas del disco externo.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Trabajo y Estudios</span>
                    </div>
                    <div class="entrada" data-cat="Eventos Especiales">
                        <h4>Cumpleaños de Mario</h4>
                        <p>Hoy es el cumpleaños de Mario. ¡Feliz cumpleaños!</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Eventos Especiales</span>
                    </div>
                    <div class="entrada" data-cat="Finanzas">
                        <h4>Ahorro</h4>
                        <p>He apartado 20€ para comprar un juego en oferta.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Finanzas</span>
                    </div>
                    <div class="entrada" data-cat="Espiritualidad">
                        <h4>Meditación</h4>
                        <p>He meditado 10 minutos y me siento más tranquilo.</p>
                        <span class="fecha">📅 2026-09-08</span><span class="categoria">Espiritualidad</span>
                    </div>
                </div>
                <div class="botones">
                    <button class="btn" onclick="nuevaEntrada()">✏️ Nueva entrada</button>
                </div>
            </main>
        </div>
    </div>

    <footer>
        <strong>Manuel Casimiro Carrasco</strong> | <a href="mailto:urukaisk@gmail.com">urukaisk@gmail.com</a> | 📍 Reus, Tarragona<br>
        🌐 <a href="https://unique-biscochitos-31bcea.netlify.app/">Portfolio</a> | 💻 <a href="https://thriving-otter-cc1e25.netlify.app/">Urukais Klick</a> | ✨ <a href="https://rad-dolphin-182dfb.netlify.app/">Los Guardianes Silenciosos</a> | 🐙 <a href="https://github.com/urukaisk-maker">GitHub</a>
    </footer>

    <script>
        function entrar() {
            document.getElementById('bienvenida').style.display = 'none';
            document.getElementById('principal').style.display = 'block';
            dibujarCalendario();
        }

        function filtrar(cat) {
            const entradas = document.querySelectorAll('.entrada');
            entradas.forEach(e => {
                if (cat === 'Todas' || e.getAttribute('data-cat') === cat) {
                    e.style.display = 'block';
                } else {
                    e.style.display = 'none';
                }
            });
            const titulo = document.getElementById('tituloSeccion');
            if (cat === 'Todas') {
                titulo.textContent = 'Todas las entradas';
            } else {
                titulo.textContent = 'Entradas en ' + cat;
            }
        }

        function nuevaEntrada() {
            const titulo = prompt('Título:');
            const contenido = prompt('Contenido:');
            if (!titulo || !contenido) return;
            const fecha = new Date().toISOString().split('T')[0];
            const cont = document.getElementById('contenedorEntradas');
            const div = document.createElement('div');
            div.className = 'entrada';
            div.setAttribute('data-cat', 'Vida Diaria');
            div.innerHTML = '<h4>' + titulo + '</h4><p>' + contenido + '</p><span class="fecha">📅 ' + fecha + '</span><span class="categoria">Vida Diaria</span>';
            cont.appendChild(div);
        }

        // Calendario simple (solo muestra el mes actual)
        let mesActual = new Date().getMonth();
        let anioActual = new Date().getFullYear();

        function dibujarCalendario() {
            const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
            document.getElementById('tituloMes').textContent = meses[mesActual] + ' ' + anioActual;
            const grid = document.getElementById('calGrid');
            grid.innerHTML = '';
            const diasSemana = ['L','M','X','J','V','S','D'];
            diasSemana.forEach(d => {
                const div = document.createElement('div');
                div.className = 'cal-weekday';
                div.textContent = d;
                grid.appendChild(div);
            });
            const primerDia = new Date(anioActual, mesActual, 1).getDay();
            const totalDias = new Date(anioActual, mesActual + 1, 0).getDate();
            for (let i = 0; i < primerDia; i++) {
                const div = document.createElement('div');
                div.className = 'cal-day empty';
                grid.appendChild(div);
            }
            for (let d = 1; d <= totalDias; d++) {
                const div = document.createElement('div');
                div.className = 'cal-day';
                div.textContent = d;
                grid.appendChild(div);
            }
        }

        function cambiarMes(delta) {
            mesActual += delta;
            if (mesActual < 0) { mesActual = 11; anioActual--; }
            if (mesActual > 11) { mesActual = 0; anioActual++; }
            dibujarCalendario();
        }
    </script>
</body>
</html>"""

ruta = "/run/media/urukais/PROYECTOS/07_DIARIO_MARIO/index.html"

with open(ruta, "w", encoding="utf-8") as f:
    f.write(html)

print("Diario creado correctamente en:", ruta)
