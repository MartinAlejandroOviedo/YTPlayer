# Documentacion YTPlayer

## Descripcion
Reproductor TUI de YouTube Music construido con Textual y mpv. Permite buscar, reproducir, mostrar caratulas, visualizar energia en vivo y controlar volumen/seek desde teclado o botones en pantalla.

## Vista previa
![Vista previa del player](../img/Captura%20de%20pantalla_20251212_203710.png)

## Requisitos
- Python 3.10+.
- mpv + libmpv (para reproducir). En Debian/Ubuntu: `sudo apt install mpv libmpv1 python3-venv`.
- yt-dlp se instala via `requirements.txt`.
- Opcional para visualizador real: `libportaudio2` y permisos de captura (`sudo apt install libportaudio2`).

## Instalacion desde fuente
```bash
git clone https://github.com/<tu-usuario>/YTPlayer.git
cd YTPlayer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Uso rapido
- `python app.py` lanza la UI.
- Escribe una consulta y Enter o click en Buscar.
- Selecciona una fila y presiona Enter o el boton Play.
- Cambia tema con Ctrl+1..4, volumen con `-` / `=`, seek con flechas izquierda/derecha.
- Checkbox "Continuar" avanza automaticamente a la siguiente fila al terminar una pista.
- Selector superior permite elegir dispositivo de audio de mpv.

## Atajos clave
- `/` enfoca el cuadro de busqueda.
- `Enter` reproduce la fila seleccionada.
- `Space` play/pause.
- `-` / `=` volumen.
- `Left` / `Right` seek +/- 5s.
- `Ctrl+1..4` cambia tema.
- `Ctrl+C` sale.

## Controles en pantalla
- Panel izquierdo: selector de dispositivo y boton Salir, cuadro de busqueda + boton Buscar, barra de transporte (<<, Play/Pause, Stop, >>) y tabla de resultados.
- Panel derecho: caratula + estado de carga, info de pista actual, progreso y barra, estado de volumen y checkbox Continuar, botonera de volumen, visualizador tipo sparkline.

## Temas disponibles
dark (default), dracula, caramel, light. Se aplican al vuelo sin reiniciar.

## Empaquetado .deb
El script deja el paquete en `releases/`.
```bash
bash packaging/build_deb.sh    # solicita version y datos de mantenedor (por defecto 0.1.0)
ls releases/ytplayer_<version>.deb
sudo apt install ./releases/ytplayer_<version>.deb
```
Instala la app en `/usr/lib/ytplayer` con su venv y expone `ytplayer` en `/usr/bin/ytplayer`. Dependencias declaradas: `mpv, libmpv1 | libmpv2, python3, python3-venv`.

## Notas y solucion de problemas
- ytmusicapi funciona sin credenciales basicas, pero puedes configurar cookies si necesitas resultados regionales.
- Si el visualizador no se mueve, revisa permisos de audio/captura; la app cae a modo sintetico.
- Los errores de mpv se muestran en el estado inferior cuando ocurren (p.ej. volumen o reproduccion).
