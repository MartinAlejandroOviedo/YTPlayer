THEME_CSS = """
Screen {
    align: center top;
    background: #f3f4f6;
    color: #0f172a;
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
    background: #ffffff;
    border: solid #3b82f6;
    padding: 1 1;
    height: 1fr;
}
/* Contenedores mayores */
#caja-busqueda {
    width: 100%;
    height: auto;
    padding: 0 1 1 1;
    content-align: center top;
}
#caja-listado {
    width: 100%;
    height: 1fr;
    padding: 0 1;
    content-align: center top;
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
    background: #ffffff;
    border: solid #3b82f6;
    border-title-color: #3b82f6;
}
#status {
    color: #4b5563;
    padding: 0 2;
}
#left Container {
    margin-bottom: 1;
}
/* Bloque caratula */
#cover-block {
    width: 100%;
    height: 18;
    padding: 0;
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
    color: #0f172a;
    background: #fef3c7;
}
#results {
    height: 1fr;
    min-height: 16;
    margin: 0;
    border: solid #e5e7eb;
}
#now-playing {
    height: 5;
    content-align: left top;
    color: #0f172a;
}
#cover {
    width: 18;
    height: 18;
    max-width: 100%;
    border: solid #3b82f6;
    content-align: left top;
    overflow: hidden;
}
#cover-status {
    color: #4b5563;
    padding: 0 0 1 0;
}
/* Loading cover */
#cover-loading {
    padding: 0;
    margin: 0 0 1 0;
    color: #3b82f6;
}
/* Auto continuar */
#auto-continue {
    margin: 0 0 1 0;
}
/* Barra de progreso */
#visualizer {
    height: 5;
    background: #f8fafc;
    padding: 0 1;
    border: solid #3b82f6;
}
#progress-block {
    padding: 0 0 1 0;
    height: 3;
    width: 100%;
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
}
/* Botonera principal */
#transport Button {
    width: 8;
    height: 3;
    border: solid #3b82f6;
    margin: 0 2;
    content-align: center middle;
    background: #e0f2fe;
    color: #0f172a;
}
Button {
    border: solid #3b82f6;
    background: #e0f2fe;
    color: #0f172a;
}
#btn-play {
    background: #22c55e;
    color: #0f172a;
}
#btn-stop {
    border: solid #f97316;
    color: #0f172a;
    background: #fed7aa;
}
#btn-prev, #btn-next {
    color: #0f172a;
}
"""
