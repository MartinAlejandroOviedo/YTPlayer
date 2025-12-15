# YTPlayer Documentation (English)

## Description
Terminal UI YouTube Music player built with Textual and mpv. Search, play, show cover art, view live energy sparkline, and control volume/seek via keyboard or on-screen buttons.

## Preview
![Player preview](../img/Captura%20de%20pantalla_20251212_203710.png)

## Requirements
- Python 3.10+.
- mpv + libmpv (for playback). On Debian/Ubuntu: `sudo apt install mpv libmpv1 python3-venv`.
- yt-dlp is installed via `requirements.txt`.
- Optional for real audio capture visualizer: `libportaudio2` and capture permissions (`sudo apt install libportaudio2`).

## Install from source
```bash
git clone https://github.com/<your-user>/YTPlayer.git
cd YTPlayer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Quick use
- `python app.py` launches the UI.
- Type a query and press Enter or click Search.
- Select a row and press Enter or click Play.
- Switch theme with Ctrl+1..5, adjust volume with `-` / `=`, seek with left/right arrows.
- "Continuar" checkbox auto-advances to the next row when a track ends.
- "Normalizar" checkbox applies mpv's dynaudnorm to even out volume between tracks.
- Options tab has an equalizer selector with presets (flat, rock, pop, jazz, house, techno).
- Top selector lets you pick the mpv audio device.

## Key bindings
- `/` focuses the search box.
- `Enter` plays the selected row.
- `Space` play/pause.
- `-` / `=` volume.
- `Left` / `Right` seek +/- 5s.
- `Ctrl+1..5` change theme.
- `Ctrl+C` quit.

## On-screen controls
- Left panel: audio device selector and Exit button, search box + Search button, transport bar (<<, Play/Pause, Stop, >>), and results table.
- Right panel: Player tab with cover art + loading state, now playing info, progress label and bar, volume status, volume buttons, sparkline visualizer. Options tab with equalizer selector + Continuar/Normalizar checkboxes. Lyrics tab with status, loader, and lyrics text.

## Themes
mini (default, compact), dark, dracula, caramel, light. Apply instantly without restarting. Shortcuts: Ctrl+1..5.

## .deb packaging
Script outputs the package into `releases/`.
```bash
bash packaging/build_deb.sh 0.1.5    # prompts for version and maintainer (default 0.1.0)
ls releases/ytplayer_0.1.5.deb
sudo apt install ./releases/ytplayer_0.1.5.deb
```
Installs the app into `/usr/lib/ytplayer` with its venv and exposes `ytplayer` in `/usr/bin/ytplayer`. Declared deps: `mpv, libmpv1 | libmpv2, python3, python3-venv`.

## Notes / troubleshooting
- ytmusicapi works unauthenticated, but you can configure cookies if you need regional results.
- If the visualizer is flat, check audio/capture permissions; the app falls back to synthetic mode.
- mpv errors show in the status area when they occur (e.g., playback or volume issues).
