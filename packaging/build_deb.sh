#!/usr/bin/env bash
# Empaqueta la app en un .deb autocontenido con venv en /usr/lib/ytplayer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-0.1.0}"
PKG_NAME="ytplayer"
STAGE_DIR="$ROOT/dist/${PKG_NAME}_${VERSION}"
PREFIX="$STAGE_DIR/usr/lib/${PKG_NAME}"
BIN_DIR="$STAGE_DIR/usr/bin"

command -v dpkg-deb >/dev/null || { echo "dpkg-deb requerido"; exit 1; }
command -v python3 >/dev/null || { echo "python3 requerido"; exit 1; }

echo "Limpiando staging..."
rm -rf "$STAGE_DIR"
mkdir -p "$PREFIX" "$BIN_DIR" "$STAGE_DIR/DEBIAN"

echo "Copiando codigo fuente..."
cp "$ROOT/app.py" "$PREFIX/"
cp "$ROOT/requirements.txt" "$PREFIX/"
cp -r "$ROOT/modules" "$PREFIX/"
cp -r "$ROOT/yt_app" "$PREFIX/"
cp -r "$ROOT/themes" "$PREFIX/"
if [ -d "$ROOT/html" ]; then
    cp -r "$ROOT/html" "$PREFIX/"
fi

echo "Creando venv e instalando dependencias..."
python3 -m venv "$PREFIX/.venv"
"$PREFIX/.venv/bin/pip" install --upgrade pip
"$PREFIX/.venv/bin/pip" install -r "$PREFIX/requirements.txt"

echo "Generando wrapper /usr/bin/ytplayer..."
cat > "$BIN_DIR/ytplayer" <<'EOF'
#!/usr/bin/env bash
APP_DIR="/usr/lib/ytplayer"
VENV="$APP_DIR/.venv"
exec "$VENV/bin/python" "$APP_DIR/app.py" "$@"
EOF
chmod +x "$BIN_DIR/ytplayer"

echo "Creando control..."
cat > "$STAGE_DIR/DEBIAN/control" <<EOF
Package: ytplayer
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: all
Maintainer: YTPlayer <noreply@example.com>
Depends: mpv, libmpv1 | libmpv2, python3, python3-venv
Description: Reproductor TUI de YouTube Music con Textual + mpv
EOF

echo "Construyendo paquete..."
dpkg-deb --build "$STAGE_DIR"
echo "Listo: dist/${PKG_NAME}_${VERSION}.deb"
