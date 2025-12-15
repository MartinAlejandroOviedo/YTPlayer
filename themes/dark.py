THEME_CSS = """
Screen {
    align: center top;
    background: #0f172a;
    color: #e5e7eb;
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
    background: #111827;
    border: solid #22d3ee;
    padding: 1 1;
    height: 1fr;
}
#right-tabs {
    width: 100%;
    height: 1fr;
}
#lyrics-tab {
    height: 1fr;
}
#player-tab {
    height: 1fr;
}
#options-tab {
    height: 1fr;
}
#options-content {
    width: 100%;
    height: 1fr;
    padding: 1;
    background: #0f172a;
    border: solid #22d3ee;
    content-align: left top;
}
#options-title {
    color: #e5e7eb;
    padding: 0 0 1 0;
}
#options-content Select {
    margin: 0 0 1 0;
    width: 28;
}
#options-content Checkbox {
    margin: 0 0 1 0;
}
#lyrics-content {
    width: 100%;
    height: 1fr;
    padding: 1;
    background: #0f172a;
    border: solid #22d3ee;
    content-align: left top;
}
#lyrics-offset-controls {
    padding: 0 0 1 0;
    height: 3;
    content-align: left middle;
}
#lyrics-offset-controls Button {
    width: 14;
    height: 3;
    margin: 0 1 0 0;
}
#lyrics-offset-label {
    padding: 0 0 0 1;
    color: #9ca3af;
}
#lyrics-table {
    width: 100%;
    height: 1fr;
    background: #0b1220;
    border: solid #22d3ee;
    color: #e5e7eb;
}
#lyrics-table .datatable--header {
    background: #111827;
    color: #22d3ee;
}
#lyrics-table .datatable--cell {
    color: #e5e7eb;
}
#lyrics-table .datatable--row {
    color: #e5e7eb;
}
#lyrics-loading {
    margin: 0 0 1 0;
    color: #22d3ee;
}
#lyrics-status {
    color: #9ca3af;
    padding: 0 0 1 0;
}
#lyrics-text {
    height: 1fr;
    border: solid #1f2937;
    background: #0b1220;
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
    width: 8;
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
/* Loading cover */
#cover-loading {
    padding: 0;
    margin: 0 0 1 0;
    color: #22d3ee;
}
/* Auto continuar */
#auto-continue {
    margin: 0 0 1 0;
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
    width: 4;
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
    width: 5;
    height: 3;
    border: solid #22d3ee;
    margin: 0 1;
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
