"""
Waveform Widget

Valós idejű audio waveform megjelenítés rögzítés közben
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
import numpy as np
from collections import deque
from typing import Optional


class WaveformWidget(QWidget):
    """
    Valós idejű audio waveform megjelenítő widget

    A widget fogadja az audio chunk-okat és scrolling waveform-ot rajzol.
    Circular buffer-t használ az utolsó 2-3 másodperc audio megjelenítésére.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Buffer config
        self.sample_rate = 16000  # Whisper standard
        self.buffer_duration = 3.0  # másodperc
        self.max_samples = int(self.sample_rate * self.buffer_duration)

        # Circular buffer
        self.audio_buffer = deque(maxlen=self.max_samples)

        # Vizualizáció config
        self.background_color = QColor("#1E1E1E")  # Sötét háttér
        self.waveform_color = QColor("#00FF00")  # Zöld waveform
        self.grid_color = QColor("#404040")  # Sötétszürke rács

        # Rendering
        self.downsample_factor = 10  # Csak minden N. sample-t rajzolunk
        self.is_recording = False

        # Méret
        self.setMinimumHeight(100)
        self.setMaximumHeight(200)

        # Timer a smooth refresh-hez (30 FPS)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update)
        self.refresh_timer.setInterval(33)  # ~30 FPS

        # Background fill
        self.setAutoFillBackground(True)

    @pyqtSlot()
    def on_recording_started(self):
        """Rögzítés indult - tisztítjuk a buffert és indítjuk a timer-t"""
        self.audio_buffer.clear()
        self.is_recording = True
        self.refresh_timer.start()

    @pyqtSlot()
    def on_recording_stopped(self):
        """Rögzítés leállt - megállítjuk a timer-t"""
        self.is_recording = False
        self.refresh_timer.stop()
        self.update()  # Utolsó frissítés

    @pyqtSlot(np.ndarray)
    def on_audio_chunk(self, chunk: np.ndarray):
        """
        Új audio chunk érkezett

        Args:
            chunk: Numpy array audio adatokkal (mono, float32, -1 to 1)
        """
        if not self.is_recording:
            return

        # Flatten ha multidim
        if chunk.ndim > 1:
            chunk = chunk.flatten()

        # Hozzáadjuk a buffer-hez
        self.audio_buffer.extend(chunk)

        # A timer fogja triggerelni az update()-et

    def paintEvent(self, event):
        """Qt paint event - waveform rajzolás"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Háttér
        painter.fillRect(self.rect(), self.background_color)

        # Rács rajzolása
        self._draw_grid(painter)

        # Waveform rajzolása
        if len(self.audio_buffer) > 0:
            self._draw_waveform(painter)
        else:
            # Placeholder szöveg ha nincs adat
            painter.setPen(QColor("#808080"))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Nincs audio adat" if not self.is_recording else "Rögzítés..."
            )

    def _draw_grid(self, painter: QPainter):
        """Háttér rács rajzolása"""
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        width = self.width()
        height = self.height()

        # Középvonal (0 amplitúdó)
        painter.drawLine(0, height // 2, width, height // 2)

        # Felső és alsó harmad
        painter.drawLine(0, height // 4, width, height // 4)
        painter.drawLine(0, 3 * height // 4, width, 3 * height // 4)

    def _draw_waveform(self, painter: QPainter):
        """Waveform rajzolása"""
        width = self.width()
        height = self.height()
        center_y = height // 2

        # Samples array-be
        samples = np.array(self.audio_buffer)

        # Downsampling a gyorsabb renderingért
        if len(samples) > width * 2:
            # Átlagoljuk a sample-okat
            target_samples = width
            chunk_size = len(samples) // target_samples
            samples = samples[:chunk_size * target_samples].reshape(-1, chunk_size).mean(axis=1)

        # Normalizálás -1 to 1 range-re
        if samples.max() > 0:
            samples = samples / max(abs(samples.max()), abs(samples.min()))

        # Rajzolás
        pen = QPen(self.waveform_color)
        pen.setWidth(2)
        painter.setPen(pen)

        num_samples = len(samples)
        if num_samples < 2:
            return

        x_step = width / num_samples

        for i in range(num_samples - 1):
            x1 = int(i * x_step)
            x2 = int((i + 1) * x_step)

            # Y koordináták (amplitúdó -> pixel)
            y1 = int(center_y - samples[i] * (height * 0.4))
            y2 = int(center_y - samples[i + 1] * (height * 0.4))

            painter.drawLine(x1, y1, x2, y2)

    def set_colors(self, background: str, waveform: str, grid: str):
        """
        Színek beállítása (theme support)

        Args:
            background: Háttér szín (hex)
            waveform: Waveform szín (hex)
            grid: Rács szín (hex)
        """
        self.background_color = QColor(background)
        self.waveform_color = QColor(waveform)
        self.grid_color = QColor(grid)
        self.update()

    def clear(self):
        """Buffer törlése"""
        self.audio_buffer.clear()
        self.update()
