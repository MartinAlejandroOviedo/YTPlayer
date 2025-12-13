#!/usr/bin/env bash
# Empaqueta la app en un .deb autocontenido con venv en /usr/lib/ytplayer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_VERSION="0.1.0"
DEFAULT_MAINTAINER_NAME="Martin Alejandro Oviedo"
DEFAULT_MAINTAINER_EMAIL="martinoviedo@disroot.org"

# Permitir setear por env o argumento. Si no hay TTY, usar defaults.
VERSION="${VERSION:-${1:-}}"
MAINTAINER_NAME="${MAINTAINER_NAME:-}"
MAINTAINER_EMAIL="${MAINTAINER_EMAIL:-}"
PKG_NAME="ytplayer"

if [[ -z "$VERSION" ]]; then
    if [[ -t 0 ]]; then
        read -rp "Ingrese la versión [${DEFAULT_VERSION}]: " version_input
        VERSION="${version_input:-$DEFAULT_VERSION}"
    else
        VERSION="$DEFAULT_VERSION"
        echo "VERSION no proporcionada, usando valor por defecto: $VERSION"
    fi
fi

if [[ -z "$MAINTAINER_NAME" ]]; then
    if [[ -t 0 ]]; then
        read -rp "Nombre del mantenedor [${DEFAULT_MAINTAINER_NAME}]: " maintainer_name_input
        MAINTAINER_NAME="${maintainer_name_input:-$DEFAULT_MAINTAINER_NAME}"
    else
        MAINTAINER_NAME="$DEFAULT_MAINTAINER_NAME"
        echo "MAINTAINER_NAME no proporcionado, usando valor por defecto: $MAINTAINER_NAME"
    fi
fi

if [[ -z "$MAINTAINER_EMAIL" ]]; then
    if [[ -t 0 ]]; then
        read -rp "Email del mantenedor [${DEFAULT_MAINTAINER_EMAIL}]: " maintainer_email_input
        MAINTAINER_EMAIL="${maintainer_email_input:-$DEFAULT_MAINTAINER_EMAIL}"
    else
        MAINTAINER_EMAIL="$DEFAULT_MAINTAINER_EMAIL"
        echo "MAINTAINER_EMAIL no proporcionado, usando valor por defecto: $MAINTAINER_EMAIL"
    fi
fi

STAGE_DIR="$ROOT/dist/${PKG_NAME}_${VERSION}"
PREFIX="$STAGE_DIR/usr/lib/${PKG_NAME}"
BIN_DIR="$STAGE_DIR/usr/bin"
RELEASES_DIR="$ROOT/releases"
RELEASE_PKG="$RELEASES_DIR/${PKG_NAME}_${VERSION}.deb"

command -v dpkg-deb >/dev/null || { echo "dpkg-deb requerido"; exit 1; }
command -v python3 >/dev/null || { echo "python3 requerido"; exit 1; }

echo "Limpiando staging..."
rm -rf "$STAGE_DIR"
mkdir -p "$PREFIX" "$BIN_DIR" "$STAGE_DIR/DEBIAN"
mkdir -p "$RELEASES_DIR"
rm -f "$RELEASE_PKG"

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
cat > "$BIN_DIR/ytplayer" <<'EOF_WRAPPER'
#!/usr/bin/env bash
APP_DIR="/usr/lib/ytplayer"
VENV="$APP_DIR/.venv"
# Exponer binarios de la venv (yt-dlp) para que mpv los encuentre.
export PATH="$VENV/bin:$PATH"
exec "$VENV/bin/python" "$APP_DIR/app.py" "$@"
EOF_WRAPPER
chmod +x "$BIN_DIR/ytplayer"

echo "Creando control..."
cat > "$STAGE_DIR/DEBIAN/control" <<EOF_CONTROL
Package: ytplayer
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: all
Maintainer: ${MAINTAINER_NAME} <${MAINTAINER_EMAIL}>
Depends: mpv, libmpv1 | libmpv2, python3, python3-venv
Description: Reproductor TUI de YouTube Music con Textual + mpv
EOF_CONTROL

echo "Construyendo paquete..."
dpkg-deb --build "$STAGE_DIR" "$RELEASE_PKG"
echo "Listo: $RELEASE_PKG"
