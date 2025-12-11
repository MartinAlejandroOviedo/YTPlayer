THEME_CSS = """
Screen {
    align: center top;
    background: #0f172a;
    color: #e5e7eb;
}
/* Layout principal */
#layout {
    width: 100%;
    height: 100%;
}
#left {
    width: 1fr;
    height: 1fr;
}
#right {
    width: 34;
    min-width: 30;
    background: #111827;
    border: solid #22d3ee;
    padding: 1 1;
    height: 1fr;
}
/* Contenedores mayores */
#caja-busqueda {
    width: 100%;
    height: auto;
    padding: 0 1 1 1;
    content-align: center top;
    max-height:24;
}
#caja-listado {
    width: 100%;
    height: 1fr;
    padding: 0 1;
    content-align: center top;
    height: 1fr;
    min-height: 12;
}
#caja-player {
    width: 100%;
    height: 1fr;
    content-align: center top;
    padding: 0;
}
/* Bloque de busqueda */
#search-area {
    width: 100%;
    padding: 1 1;
    background: #111827;
    border: solid #22d3ee;
    border-title-color: #22d3ee;
}
#status {
    color: #9ca3af;
    padding: 0 2;
}
#left Container {
    margin-bottom: 0;
}
/* Bloque caratula */
#cover-block {
    width: 100%;
    height: 18;
    margin: 0 0 3 0;
    content-align: center middle;
}
#top-menu {
    padding: 0 2;
    height: 3;
    align: center middle;
}
#top-menu Select {
    width: 32;
}
#quit-btn {
    width: 10;
    border: solid #f59e0b;
    color: #e5e7eb;
    background: #2b1a07;
}
#results {
    height: 1fr;
    min-height: 16;
    margin: 0;
    border: solid #1f2937;
}
#now-playing {
    height: 5;
    content-align: left top;
    color: #e5e7eb;
}
#cover {
    width: 100%;
    height: 18;
    max-width: 100%;
    border: solid #22d3ee;
    content-align: center middle;

}
#cover-status {
    color: #9ca3af;
    padding: 0 0 1 0;
}
/* Barra de progreso */
#visualizer {
    height: 5;
    background: #111827;
    padding: 0 1;
    border: solid #22d3ee;
}
#progress-block {
    padding: 0 0 1 0;
    height: 3;
}
/* Controles laterales */
#controls {
    padding: 1 0 0 0;
    height: 5;
    content-align: center middle;
}
#controls Button {
    margin: 0 1 0 0;
    width: 10;
}
#volume-display {
    padding: 0 0 1 0;
}
#transport {
    width: 100%;
    padding: 0 1;
    margin: 0 0 0 0;
    content-align: center middle;
    height:3;
}
/* Botonera principal */
#transport Button {
    width: 8;
    height: 3;
    border: solid #22d3ee;
    margin: 0 2;
    content-align: center middle;
    background: #1f2937;
    color: #e5e7eb;
}
Button {
    border: solid #22d3ee;
    background: #1f2937;
    color: #e5e7eb;
}
#btn-play {
    background: #22d3ee;
    color: #0b1220;
}
#btn-stop {
    border: solid #f59e0b;
    color: #e5e7eb;
    background: #2b1a07;
}
#btn-prev, #btn-next {
    color: #e5e7eb;
}
"""
