THEME_CSS = """
Screen {
    align: center top;
    background: #1b0c0c;
    color: #f8e4c9;
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
    background: #241010;
    border: solid #f2a65a;
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
    background: #241010;
    border: solid #f2a65a;
    border-title-color: #f2a65a;
}
#status {
    color: #c49a85;
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
    border: solid #e76f51;
    color: #f8e4c9;
    background: #4a1a12;
}
#results {
    height: 1fr;
    min-height: 16;
    margin: 0;
    border: solid #3b1a1a;
}
#now-playing {
    height: 5;
    content-align: left top;
    color: #f8e4c9;
}
#cover {
    width: 18;
    height: 18;
    max-width: 100%;
    border: solid #f2a65a;
    content-align: left top;
    overflow: hidden;
}
#cover-status {
    color: #c49a85;
    padding: 0 0 1 0;
}
/* Barra de progreso */
#visualizer {
    height: 5;
    background: #2e1717;
    padding: 0 1;
    border: solid #f2a65a;
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
}
/* Botonera principal */
#transport Button {
    width: 8;
    height: 3;
    border: solid #f2a65a;
    margin: 0 2;
    content-align: center middle;
    background: #2e1717;
    color: #f8e4c9;
}
Button {
    border: solid #f2a65a;
    background: #2e1717;
    color: #f8e4c9;
}
#btn-play {
    background: #f2a65a;
    color: #1b0c0c;
}
#btn-stop {
    border: solid #e76f51;
    color: #f8e4c9;
    background: #4a1a12;
}
#btn-prev, #btn-next {
    color: #f8e4c9;
}
"""
