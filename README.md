# YTPlayer

Reproductor TUI de YouTube Music hecho con Textual y mpv. Busca canciones, muestra covers, visualiza energia en vivo y reproduce usando mpv con yt-dlp.

## Vista previa
![Vista previa del player](img/Captura%20de%20pantalla_20251212_203710.png)

## Caracteristicas
- Busqueda rapida de canciones via ytmusicapi (tabla con titulo, artista, album, duracion).
- Reproduccion en terminal con mpv (play/pause, seek, volumen, continuar siguiente).
- Pestaña de letras en tabla (tiempo + texto), resalta linea activa al ritmo de la cancion; fetch automatico (YouTube Music, LRCLib con duracion, Lyrist, lyrics.ovh) y boton "Usar cookies" para mejorar resultados.
- Visualizador tipo sparkline (captura audio real con sounddevice; fallback sintentico si no hay).
- Descarga y muestra cover; fallback a ascii-art si no puede renderizar imagen.
- Selector de dispositivo de audio, barra de progreso, checkbox de auto-continue y normalizador de volumen (dynaudnorm en mpv) para igualar niveles entre temas.
- Temas dinamicos: dark, dracula, caramel, light (Ctrl+1..4).

## Requisitos del sistema
- Python 3.10+.
- mpv + libmpv (para reproducir). En Debian/Ubuntu: `sudo apt install mpv libmpv1 python3-venv`.
- yt-dlp se instala via `requirements.txt`.
- Opcional para visualizador real: `libportaudio2` y permisos de captura (p.ej. `sudo apt install libportaudio2`).

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
- Checkbox "Normalizar" aplica dynaudnorm para igualar volumen entre temas.
- Boton "Usar cookies" permite cargar cookies de YouTube Music para mejorar letras/resultados (coloca cookies.json en `~/.config/ytplayer/` o usa las env vars `YTMUSIC_COOKIES`/`YTMUSIC_COOKIE_FILE`).
- Selector superior permite elegir dispositivo de audio de mpv.

### Atajos clave
- `/` enfoca el cuadro de busqueda.
- `Enter` reproduce la fila seleccionada.
- `Space` play/pause.
- `-` / `=` volumen.
- `Left` / `Right` seek +/- 5s; `<<` / `>>` botones para saltos largos.
- `Ctrl+1..4` cambia tema.
- `Ctrl+C` sale.

## Temas disponibles
- dark (default), dracula, caramel, light. Se aplican al vuelo sin reiniciar.

## Empaquetado .deb
El script ya deja el paquete listo en `releases/`.
```bash
bash packaging/build_deb.sh 0.1.4   # ajusta la version
ls releases/ytplayer_0.1.4.deb
sudo apt install ./releases/ytplayer_0.1.4.deb
```
El paquete instala la app en `/usr/lib/ytplayer` con su venv y expone `ytplayer` en `/usr/bin/ytplayer`. Dependencias declaradas: `mpv, libmpv1 | libmpv2, python3, python3-venv`.

## Notas
- ytmusicapi funciona sin credenciales basicas, pero puedes configurar cookies si necesitas resultados regionales.
- Si el visualizador no muestra movimiento, revisa permisos de audio/captura; la app cae a modo sintetico.
- Los logs de mpv se muestran en el estado cuando hay errores de reproduccion.

## Licencia
MIT. Ver `LICENSE`.
