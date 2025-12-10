"""Visualizer helper to fetch energy from PulseAudio monitor (via sounddevice) with fallback."""
import queue
import threading
import time
from typing import Optional

import numpy as np

try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except Exception:
    SOUNDDEVICE_AVAILABLE = False


class Visualizer:
    """Captura energia real desde un dispositivo de entrada (p.ej. monitor PulseAudio)."""

    def __init__(
        self,
        mpv_player: Optional[object] = None,
        device: Optional[int] = None,
        samplerate: int = 44100,
        chunk: int = 1024,
    ) -> None:
        self.mpv_player = mpv_player  # instancia interna de mpv para fallback
        self.device = device
        self.samplerate = samplerate
        self.chunk = chunk
        self.energy_queue: queue.Queue[float] = queue.Queue(maxsize=1)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stream = None
        self._use_real_audio = False

    def start(self) -> None:
        """Inicia captura; si falla, usa generador sintetico."""
        if SOUNDDEVICE_AVAILABLE:
            try:
                self._stream = sd.InputStream(
                    device=self.device,
                    channels=2,
                    samplerate=self.samplerate,
                    blocksize=self.chunk,
                    dtype="float32",
                    callback=self._audio_callback,
                )
                self._stream.start()
                self._use_real_audio = True
                return
            except Exception as exc:  # noqa: BLE001
                print(f"[Visualizer] No se pudo iniciar captura real: {exc}")

        # fallback: generar energia sinteticamente
        self._use_real_audio = False
        self._thread = threading.Thread(target=self._fake_energy_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Detiene captura/hilo."""
        self._stop_event.set()
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _audio_callback(self, indata, frames, time_info, status) -> None:  # type: ignore[override]
        if status:
            return
        mono = np.mean(indata, axis=1)
        fft_data = np.abs(np.fft.rfft(mono))
        max_val = np.max(fft_data) or 1.0
        energy = float(np.mean(fft_data / max_val))
        self._push_energy(energy)

    def _fake_energy_loop(self) -> None:
        """Genera energia aproximada en base a mpv (volumen)."""
        while not self._stop_event.is_set():
            energy = 0.0
            if self.mpv_player:
                try:
                    vol = float(getattr(self.mpv_player, "volume", 50) or 50)
                    energy = min(max(vol / 100.0, 0.0), 1.0)
                except Exception:
                    energy = 0.0
            self._push_energy(energy)
            time.sleep(0.1)

    def _push_energy(self, energy: float) -> None:
        try:
            self.energy_queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self.energy_queue.put_nowait(energy)
        except queue.Full:
            pass

    def get_energy(self) -> float:
        """Devuelve el ultimo valor de energia disponible."""
        try:
            return self.energy_queue.get_nowait()
        except queue.Empty:
            return 0.0

    @property
    def is_real(self) -> bool:
        return self._use_real_audio
