THEME_CSS = """
Screen {
    align: center top;
    background: #282a36;
    color: #f8f8f2;
    padding: 1 2;
}
/* Layout principal */
#layout {
    width: 100%;
    max-width: 120;
    height: 100%;
    max-height: 48;
}
#left {
    width: 1fr;
    height: 1fr;
}
#right {
    width: 40;
    min-width: 34;
    background: #1e1f29;
    border: solid #bd93f9;
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
    background: #1e1f29;
    border: solid #ff79c6;
    border-title-color: #ff79c6;
}
#status {
    color: #9ea0b4;
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
    border: solid #ffb86c;
    color: #f8f8f2;
    background: #5a3d11;
}
#results {
    height: 1fr;
    min-height: 16;
    margin: 0;
    border: solid #44475a;
}
#now-playing {
    height: 5;
    content-align: left top;
    color: #f8f8f2;
}
#cover {
    width: 100%;
    height: 18;
    max-width: 100%;
    border: solid #bd93f9;
    content-align: left top;
    overflow: hidden;
}
#cover-status {
    color: #9ea0b4;
    padding: 0 0 1 0;
}
/* Loading cover */
#cover-loading {
    padding: 0;
    margin: 0 0 1 0;
    color: #bd93f9;
}
/* Auto continuar */
#auto-continue {
    margin: 0 0 1 0;
}
/* Barra de progreso */
#visualizer {
    height: 5;
    background: #1e1f29;
    padding: 0 1;
    border: solid #ff79c6;
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
    width: 6;
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
    border: solid #ff79c6;
    margin: 0 2;
    content-align: center middle;
    background: #1e1f29;
    color: #f8f8f2;
}
Button {
    border: solid #bd93f9;
    background: #1e1f29;
    color: #f8f8f2;
}
#btn-play {
    background: #50fa7b;
    color: #1e1f29;
}
#btn-stop {
    border: solid #ff5555;
    color: #f8f8f2;
    background: #5e1e1e;
}
#btn-prev, #btn-next {
    color: #f8f8f2;
}
"""
