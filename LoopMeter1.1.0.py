# -*- coding: utf-8 -*-

import os
import sys
import gc
import time
import platform
import psutil

# Настройки инициализации графического конвейера
os.environ["QT_ANGLE_PLATFORM"] = "d3d9"
os.environ["QT_MEDIA_BACKEND"] = "windowsmediafoundation"
os.environ["QT_WMF_ALLOW_HARDWARE_DECODING"] = "1"
os.environ["QSG_RHI_BACKEND"] = "d3d11"

os.environ["QT_LOGGING_RULES"] = "*=false"
os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"

from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QStackedWidget, 
                             QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsOpacityEffect)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QMovie, QBrush, QPixmap, QPixmapCache
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QRect, QPoint, QSizeF, QPropertyAnimation, QVariantAnimation, QRectF

if platform.system() == "Windows":
    import ctypes
    WIN_SUPPORT = True
else:
    WIN_SUPPORT = False

# Глобальный конфигуратор производительности и локализации
APP_SETTINGS = {
    "priority_mode": "BALANCED",  # "BALANCED", "CPU", "MEM"
    "lang": "RU"                  # "RU" или "ENG"
}

TRANSLATIONS = {
    "RU": {
        "START_MENU": "ГЛАВНОЕ МЕНЮ",
        "START": "СТАРТ",
        "SETTINGS": "НАСТРОЙКИ",
        "EXIT": "ВЫХОД",
        "BACK": "НАЗАД",
        "SETTINGS_TITLE": "НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ",
        "CPU_SAVE_TITLE": "ЭКОНОМИЯ ОЗУ",
        "CPU_SAVE_DESC": "Приоритет ЦП\n\nЧастый опрос ЦП,\nкэш RAM очищен,\nданные на лету",
        "BAL_TITLE": "БАЛАНС",
        "BAL_DESC": "Обычный режим\n\nСтандартная нагрузка\nОС распределяет\nресурсы штатно",
        "MEM_SAVE_TITLE": "ЭКОНОМИЯ ЦП",
        "MEM_SAVE_DESC": "Приоритет ОЗУ\n\nРедкий опрос ЦП,\nкэширование UI\nи медиа в ОЗУ",
        "THEME": "ТЕМА",
        "MENU": "МЕНЮ",
        "DBL_CLICK": "Двойной клик для загрузки медиа",
        "R_CLICK": "Правый клик: закрепить/размер окна",
        "OPEN_MEDIA": "Открыть медиа",
        "MADE_WITH": "сделано с душой notvio"
    },
    "ENG": {
        "START_MENU": "MAIN MENU",
        "START": "START",
        "SETTINGS": "SETTINGS",
        "EXIT": "EXIT",
        "BACK": "BACK",
        "SETTINGS_TITLE": "PERFORMANCE SETTINGS",
        "CPU_SAVE_TITLE": "SAVE RAM",
        "CPU_SAVE_DESC": "CPU Priority\n\nFrequent CPU polling,\nRAM cache cleared,\non-the-fly data",
        "BAL_TITLE": "BALANCED",
        "BAL_DESC": "Normal Mode\n\nStandard load\nOS distributes\nresources normally",
        "MEM_SAVE_TITLE": "SAVE CPU",
        "MEM_SAVE_DESC": "RAM Priority\n\nRare CPU polling,\nUI and media\ncached in RAM",
        "THEME": "THEME",
        "MENU": "MENU",
        "DBL_CLICK": "Double-click to Load Media",
        "R_CLICK": "Right-click to Pin/Resize Window",
        "OPEN_MEDIA": "Open Media",
        "MADE_WITH": "made with soul by notvio"
    }
}

def apply_priority_mode(mode):
    try:
        p = psutil.Process(os.getpid())
        if mode == "CPU":
            if sys.platform == "win32":
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(-10)
            gc.enable()
            gc.set_threshold(10, 2, 2)
            gc.collect()
            QPixmapCache.clear()
            if sys.platform == "win32" and WIN_SUPPORT:
                try:
                    current_process = ctypes.windll.kernel32.GetCurrentProcess()
                    ctypes.windll.psapi.EmptyWorkingSet(current_process)
                except Exception:
                    pass
        elif mode == "MEM":
            if sys.platform == "win32":
                p.nice(psutil.IDLE_PRIORITY_CLASS)
            else:
                p.nice(19)
            gc.disable()
            QPixmapCache.setCacheLimit(102400)
        else:
            if sys.platform == "win32":
                p.nice(psutil.NORMAL_PRIORITY_CLASS)
            else:
                p.nice(0)
            gc.enable()
            gc.set_threshold(700, 10, 10)
            gc.collect()
            QPixmapCache.setCacheLimit(10240)
    except Exception:
        pass

def apply_fade_in(window, duration=250):
    effect = QGraphicsOpacityEffect(window)
    window.setGraphicsEffect(effect)
    window._fade_effect = effect

    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)

    def on_finished():
        window.setGraphicsEffect(None)
        if hasattr(window, "_fade_effect"):
            del window._fade_effect
        if hasattr(window, "_fade_anim"):
            del window._fade_anim

    anim.finished.connect(on_finished)
    window._fade_anim = anim
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def apply_fade_out(window, duration=300, on_finished_callback=None):
    effect = QGraphicsOpacityEffect(window)
    window.setGraphicsEffect(effect)
    window._fade_effect = effect

    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)

    def on_finished():
        window.setGraphicsEffect(None)
        if hasattr(window, "_fade_effect"):
            del window._fade_effect
        if hasattr(window, "_fade_anim"):
            del window._fade_anim
        if on_finished_callback:
            on_finished_callback()

    anim.finished.connect(on_finished)
    window._fade_anim = anim
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def set_window_topmost(hwnd, topmost=True):
    if not WIN_SUPPORT or not hwnd:
        return
    HWND_STATE = -1 if topmost else -2
    SWP_FLAGS = 0x0002 | 0x0001 | 0x0010
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_STATE, 0, 0, 0, 0, SWP_FLAGS)

def find_companion_audio(media_path):
    base, _ = os.path.splitext(media_path)
    for ext in [".mp3", ".wav"]:
        audio_path = base + ext
        if os.path.exists(audio_path):
            return audio_path
    return None

THEMES = [
    {
        "name": "NEON CYBER",
        "bg": (10, 15, 30, 250),
        "border": (34, 197, 94, 80),
        "cpu_bar": (34, 197, 94, 255),
        "ram_bar": (59, 130, 246, 255),
        "text_main": (255, 255, 255, 255),
        "accent": (34, 197, 94)
    },
    {
        "name": "DEEP PURPLE",
        "bg": (20, 10, 35, 250),
        "border": (168, 85, 247, 80),
        "cpu_bar": (217, 70, 239, 255),
        "ram_bar": (129, 140, 248, 255),
        "text_main": (255, 255, 255, 255),
        "accent": (217, 70, 239)
    },
    {
        "name": "SOLAR FLARE",
        "bg": (25, 12, 10, 250),
        "border": (239, 68, 68, 80),
        "cpu_bar": (249, 115, 22, 255),
        "ram_bar": (234, 179, 8, 255),
        "text_main": (255, 255, 255, 255),
        "accent": (249, 115, 22)
    }
]

class TelemetryWorker(QThread):
    stats_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        psutil.cpu_percent()
        while self.running:
            try:
                cpu_base = psutil.cpu_percent(interval=None)
                ram_base = psutil.virtual_memory().percent

                stats = {
                    "cpu": cpu_base,
                    "ram": ram_base
                }
                self.stats_updated.emit(stats)

                mode = APP_SETTINGS["priority_mode"]
                if mode == "MEM":
                    self.msleep(3000)
                elif mode == "CPU":
                    self.msleep(500)
                else:
                    self.msleep(1200)
            except Exception:
                pass

    def stop(self):
        self.running = False

class DragPinWindowHelper:
    def __init__(self, window, name="Window"):
        self.window = window
        self.name = name
        self.drag_start_pos = QPoint()
        self.is_dragging = False
        self.resize_start_global = QPoint()
        self.resize_start_geometry = QRect()
        self.resize_start_time = 0.0
        self.is_resizing = False
        self.is_pinned = True
        self.feedback_text = ""
        self.feedback_expiry = 0.0
        self.hwnd = None

    def resolve_hwnd_and_pin(self):
        if WIN_SUPPORT and not self.hwnd:
            try:
                self.hwnd = int(self.window.winId())
                set_window_topmost(self.hwnd, self.is_pinned)
            except Exception:
                self.hwnd = None

    def handle_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            self.is_dragging = True
        elif event.button() == Qt.MouseButton.RightButton:
            self.resize_start_global = event.globalPosition().toPoint()
            self.resize_start_geometry = self.window.geometry()
            self.resize_start_time = time.time()
            self.is_resizing = True

    def handle_move(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.window.move(event.globalPosition().toPoint() - self.drag_start_pos)
        elif event.buttons() & Qt.MouseButton.RightButton and self.is_resizing:
            delta = event.globalPosition().toPoint() - self.resize_start_global
            min_w = 150 if self.name == "MEDIA" else 200
            min_h = 150 if self.name == "MEDIA" else 100
            new_w = max(min_w, self.resize_start_geometry.width() + delta.x())
            new_h = max(min_h, self.resize_start_geometry.height() + delta.y())
            self.window.resize(new_w, new_h)

    def handle_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.is_resizing = False
            duration = time.time() - self.resize_start_time
            delta = event.globalPosition().toPoint() - self.resize_start_global
            dist = abs(delta.x()) + abs(delta.y())
            if duration < 0.25 and dist < 6:
                self.toggle_pin_state()

    def toggle_pin_state(self):
        self.is_pinned = not self.is_pinned
        
        if WIN_SUPPORT and not self.hwnd:
            try:
                self.hwnd = int(self.window.winId())
            except Exception:
                self.hwnd = None

        if WIN_SUPPORT and self.hwnd:
            set_window_topmost(self.hwnd, self.is_pinned)
        else:
            flags = self.window.windowFlags()
            if self.is_pinned:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowType.WindowStaysOnTopHint
                
            flags |= Qt.WindowType.FramelessWindowHint
            
            self.window.setWindowFlags(flags)
            self.window.show()

        status = "PINNED" if self.is_pinned else "UNPINNED"
        self.feedback_text = f"{self.name}: {status}"
        self.feedback_expiry = time.time() + 1.2
        self.window.update()

    def draw_feedback_if_active(self, painter, w, h, theme):
        if time.time() < self.feedback_expiry:
            painter.setBrush(QColor(0, 0, 0, 220))
            painter.setPen(QPen(QColor(*theme["border"]), 1))
            painter.drawRoundedRect(10, h - 32, w - 20, 24, 4.0, 4.0)
            font = QFont("Arial", 9, QFont.Weight.Bold)
            painter.setFont(font)
            fill_color = QColor(*theme["accent"]) if self.is_pinned else QColor(156, 163, 175)
            painter.setPen(fill_color)
            painter.drawText(18, h - 16, self.feedback_text)

class TelemetryWindow(QWidget):
    def __init__(self, parent_app, stats):
        super().__init__(None)
        self.main_app = parent_app
        self.stats = stats
        self.setGeometry(520, 100, 300, 120)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.window_manager = DragPinWindowHelper(self, name="STATS")
        self.theme_btn_bounds = QRect()
        self.menu_btn_bounds = QRect()
        self._is_closing = False

    def showEvent(self, event):
        super().showEvent(event)
        self.window_manager.resolve_hwnd_and_pin()
        apply_fade_in(self)

    def mousePressEvent(self, event):
        self.window_manager.handle_press(event)
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = event.position().toPoint()
            if self.theme_btn_bounds.contains(click_pos):
                self.main_app.current_theme_idx = (self.main_app.current_theme_idx + 1) % len(THEMES)
                self.window_manager.feedback_text = f"THEME: {THEMES[self.main_app.current_theme_idx]['name']}"
                self.window_manager.feedback_expiry = time.time() + 1.2
                self.update()
                self.main_app.update()
            elif self.menu_btn_bounds.contains(click_pos):
                self.main_app.return_to_start_menu()

    def mouseMoveEvent(self, event):
        self.window_manager.handle_move(event)
        self.update()

    def mouseReleaseEvent(self, event):
        self.window_manager.handle_release(event)
        self.update()

    def close_with_fade(self):
        if not self._is_closing:
            self._is_closing = True
            apply_fade_out(self, duration=300, on_finished_callback=self.close)

    def closeEvent(self, event):
        if not self._is_closing:
            event.ignore()
            self.close_with_fade()
        else:
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[self.main_app.current_theme_idx]
        lang_dict = TRANSLATIONS[APP_SETTINGS["lang"]]
        
        w = self.width()
        h = self.height()
        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, w - 10, h - 10, 10.0, 10.0)
        font_title = QFont("Arial", 11, QFont.Weight.Bold)
        font_btn = QFont("Arial", 9, QFont.Weight.Bold)
        
        self.theme_btn_bounds = QRect(w - 80, 12, 65, 20)
        painter.setBrush(QColor(255, 255, 255, 15))
        painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.theme_btn_bounds, 4.0, 4.0)
        painter.setPen(QColor(*theme["accent"]))
        painter.setFont(font_btn)
        painter.drawText(self.theme_btn_bounds, int(Qt.AlignmentFlag.AlignCenter), lang_dict["THEME"])

        self.menu_btn_bounds = QRect(w - 155, 12, 65, 20)
        painter.setBrush(QColor(255, 255, 255, 15))
        painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.menu_btn_bounds, 4.0, 4.0)
        painter.setPen(QColor(*theme["accent"]))
        painter.drawText(self.menu_btn_bounds, int(Qt.AlignmentFlag.AlignCenter), lang_dict["MENU"])

        cpu_val = self.stats["cpu"]
        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(font_title)
        painter.drawText(18, 30, f"CPU  {cpu_val:.0f}%")
        painter.setBrush(QColor(51, 65, 85, 120))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(18, 38, w - 36, 8)
        cpu_w = int((w - 36) * (cpu_val / 100.0))
        painter.setBrush(QColor(*theme["cpu_bar"]))
        painter.drawRect(18, 38, cpu_w, 8)

        ram_val = self.stats["ram"]
        ram_y = int(h * 0.48)
        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(font_title)
        painter.drawText(18, ram_y + 12, f"RAM  {ram_val:.0f}%")
        bar_y = ram_y + 22
        painter.setBrush(QColor(51, 65, 85, 120))
        painter.drawRect(18, bar_y, w - 36, 8)
        ram_w = int((w - 36) * (ram_val / 100.0))
        painter.setBrush(QColor(*theme["ram_bar"]))
        painter.drawRect(18, bar_y, ram_w, 8)
        self.window_manager.draw_feedback_if_active(painter, w, h, theme)

class MediaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 400, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.running = True
        self.file_path = None
        self.current_theme_idx = 0
        self.stats = {"cpu": 0.0, "ram": 0.0}
        self._is_closing = False

        self.container = QStackedWidget(self)
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene, self)
        self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.graphics_view.setStyleSheet("background: transparent; border: none;")
        self.graphics_view.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        self.container.addWidget(self.gif_label)
        self.container.addWidget(self.graphics_view)

        self.video_player = QMediaPlayer()
        self.video_audio_output = QAudioOutput()
        self.video_player.setAudioOutput(self.video_audio_output)
        self.video_player.setVideoOutput(self.video_item)
        self.video_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.companion_audio_player = QMediaPlayer()
        self.companion_audio_output = QAudioOutput()
        self.companion_audio_player.setAudioOutput(self.companion_audio_output)
        self.companion_audio_player.setLoops(QMediaPlayer.Loops.Infinite)

        self.video_audio_output.setVolume(0.7)
        self.companion_audio_output.setVolume(0.7)
        self.gif_movie = None
        self.window_manager = DragPinWindowHelper(self, name="MEDIA")

        self.worker = TelemetryWorker()
        self.worker.stats_updated.connect(self.update_stats)
        self.worker.start()

        self.telemetry_window = TelemetryWindow(self, self.stats)
        self.telemetry_window.show()

    def update_stats(self, data):
        self.stats.update(data)
        self.telemetry_window.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.window_manager.resolve_hwnd_and_pin()
        apply_fade_in(self)

    def resizeEvent(self, event):
        self.container.setGeometry(10, 10, self.width() - 20, self.height() - 20)
        self.graphics_view.setGeometry(self.container.rect())
        self.video_item.setSize(QSizeF(self.graphics_view.size()))
        if self.gif_movie:
            self.gif_movie.setScaledSize(self.container.size())
        self.update()

    def mousePressEvent(self, event):
        self.window_manager.handle_press(event)

    def mouseMoveEvent(self, event):
        self.window_manager.handle_move(event)
        self.update()

    def mouseReleaseEvent(self, event):
        self.window_manager.handle_release(event)
        self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.load_file_dialog()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.safe_close()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_pause()

    def toggle_pause(self):
        if not self.file_path:
            return
        if self.file_path.lower().endswith('.gif'):
            if self.gif_movie:
                if self.gif_movie.state() == QMovie.MovieState.Running:
                    self.gif_movie.setPaused(True)
                    self.companion_audio_player.pause()
                else:
                    self.gif_movie.setPaused(False)
                    self.companion_audio_player.play()
        else:
            if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.video_player.pause()
                self.companion_audio_player.pause()
            else:
                self.video_player.play()
                if self.companion_audio_player.source().isValid():
                    self.companion_audio_player.play()

    def return_to_start_menu(self):
        self.stop_all_playback()
        if self.worker:
            self.worker.stop()
        if self.telemetry_window:
            self.telemetry_window.close_with_fade()

        def finalize():
            if self.worker:
                self.worker.wait()
            self.close()
            global start_menu
            start_menu = StartMenuWindow()
            start_menu.show()

        apply_fade_out(self, duration=300, on_finished_callback=finalize)

    def load_file_dialog(self):
        lang_dict = TRANSLATIONS[APP_SETTINGS["lang"]]
        path, _ = QFileDialog.getOpenFileName(
            self, lang_dict["OPEN_MEDIA"], "", "Media Files (*.mp4 *.gif *.avi *.mov *.mkv *.mp3 *.wav)"
        )
        if path:
            self.file_path = path
            self.stop_all_playback()
            companion = find_companion_audio(path)

            if path.lower().endswith('.gif'):
                self.container.setCurrentIndex(0)
                self.gif_movie = QMovie(path)
                
                if APP_SETTINGS["priority_mode"] == "MEM":
                    self.gif_movie.setCacheMode(QMovie.CacheMode.CacheAll)
                else:
                    self.gif_movie.setCacheMode(QMovie.CacheMode.CacheNone)

                self.gif_movie.setScaledSize(self.container.size())
                self.gif_label.setMovie(self.gif_movie)
                self.gif_movie.start()
                if companion:
                    self.companion_audio_player.setSource(QUrl.fromLocalFile(companion))
                    self.companion_audio_player.play()
            else:
                self.container.setCurrentIndex(1)
                self.video_player.setSource(QUrl.fromLocalFile(path))
                if companion:
                    self.video_audio_output.setMuted(True)
                    self.companion_audio_player.setSource(QUrl.fromLocalFile(companion))
                    self.companion_audio_player.play()
                else:
                    self.video_audio_output.setMuted(False)
                self.video_player.play()

    def stop_all_playback(self):
        self.video_player.stop()
        self.video_player.setSource(QUrl())
        self.companion_audio_player.stop()
        self.companion_audio_player.setSource(QUrl())
        if self.gif_movie:
            self.gif_movie.stop()
            self.gif_label.setMovie(None)
            self.gif_movie.deleteLater()
            self.gif_movie = None
        gc.collect()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[self.current_theme_idx]
        lang_dict = TRANSLATIONS[APP_SETTINGS["lang"]]
        w = self.width()
        h = self.height()
        
        if not self.file_path:
            painter.setBrush(QColor(*theme["bg"]))
            painter.setPen(QPen(QColor(*theme["border"]), 2))
            painter.drawRoundedRect(10, 10, w - 20, h - 20, 10.0, 10.0)
            cx, cy = w // 2, h // 2
            font_main = QFont("Arial", 12, QFont.Weight.Bold)
            font_sub = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setBrush(QColor(*theme["accent"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(cx - 25, cy - 35, 50, 30)
            painter.drawPolygon(QPoint(cx - 25, cy - 35), QPoint(cx, cy - 50), QPoint(cx + 25, cy - 35))
            painter.setPen(QColor(255, 255, 255, 240))
            painter.setFont(font_main)
            painter.drawText(QRect(10, cy + 15, w - 20, 25), int(Qt.AlignmentFlag.AlignCenter), lang_dict["DBL_CLICK"])
            painter.setPen(QColor(156, 163, 175, 200))
            painter.setFont(font_sub)
            painter.drawText(QRect(10, cy + 40, w - 20, 20), int(Qt.AlignmentFlag.AlignCenter), lang_dict["R_CLICK"])
            
        if time.time() < self.window_manager.feedback_expiry:
            self.window_manager.draw_feedback_if_active(painter, w, h, theme)

    def closeEvent(self, event):
        if not self._is_closing:
            event.ignore()
            self._is_closing = True
            self.stop_all_playback()
            if self.worker:
                self.worker.stop()
            if self.telemetry_window:
                self.telemetry_window.close_with_fade()

            def finalize_close():
                if self.worker:
                    self.worker.wait()
                self.close()

            apply_fade_out(self, duration=300, on_finished_callback=finalize_close)
        else:
            event.accept()

    def safe_close(self):
        self.close()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 480, 240)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.drag_start = QPoint()
        self.is_dragging = False
        self.hovered_btn = None

        self.col_cpu_rect = QRect(20, 70, 135, 100)
        self.col_bal_rect = QRect(172, 70, 135, 100)
        self.col_mem_rect = QRect(325, 70, 135, 100)
        self.btn_back_rect = QRect(180, 185, 120, 35)

    def showEvent(self, event):
        super().showEvent(event)
        apply_fade_in(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self.col_cpu_rect.contains(pos):
                APP_SETTINGS["priority_mode"] = "CPU"
                apply_priority_mode("CPU")
                self.update()
            elif self.col_bal_rect.contains(pos):
                APP_SETTINGS["priority_mode"] = "BALANCED"
                apply_priority_mode("BALANCED")
                self.update()
            elif self.col_mem_rect.contains(pos):
                APP_SETTINGS["priority_mode"] = "MEM"
                apply_priority_mode("MEM")
                self.update()
            elif self.btn_back_rect.contains(pos):
                def open_start():
                    self.close()
                    global start_menu
                    start_menu = StartMenuWindow()
                    start_menu.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_start)
            else:
                self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.is_dragging = True

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        old_hover = self.hovered_btn

        if self.col_cpu_rect.contains(pos):
            self.hovered_btn = "cpu"
        elif self.col_bal_rect.contains(pos):
            self.hovered_btn = "bal"
        elif self.col_mem_rect.contains(pos):
            self.hovered_btn = "mem"
        elif self.btn_back_rect.contains(pos):
            self.hovered_btn = "back"
        else:
            self.hovered_btn = None

        if old_hover != self.hovered_btn:
            self.update()

        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[0]
        lang_dict = TRANSLATIONS[APP_SETTINGS["lang"]]
        w = self.width()
        h = self.height()

        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, w - 10, h - 10, 12.0, 12.0)

        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(QRect(10, 20, w - 20, 25), Qt.AlignmentFlag.AlignCenter, lang_dict["SETTINGS_TITLE"])

        for rect, title, desc, key in [
            (self.col_cpu_rect, lang_dict["CPU_SAVE_TITLE"], lang_dict["CPU_SAVE_DESC"], "cpu"),
            (self.col_bal_rect, lang_dict["BAL_TITLE"], lang_dict["BAL_DESC"], "bal"),
            (self.col_mem_rect, lang_dict["MEM_SAVE_TITLE"], lang_dict["MEM_SAVE_DESC"], "mem")
        ]:
            is_hovered = (self.hovered_btn == key)
            if key == "cpu":
                is_selected = (APP_SETTINGS["priority_mode"] == "CPU")
            elif key == "mem":
                is_selected = (APP_SETTINGS["priority_mode"] == "MEM")
            else:
                is_selected = (APP_SETTINGS["priority_mode"] == "BALANCED")

            if is_selected:
                painter.setBrush(QColor(*theme["accent"], 40))
                painter.setPen(QPen(QColor(*theme["accent"]), 2))
            elif is_hovered:
                painter.setBrush(QColor(255, 255, 255, 20))
                painter.setPen(QPen(QColor(*theme["accent"]), 1))
            else:
                painter.setBrush(QColor(255, 255, 255, 10))
                painter.setPen(QPen(QColor(*theme["border"]), 1))

            painter.drawRoundedRect(rect, 8.0, 8.0)

            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255) if is_selected else QColor(*theme["accent"]))
            painter.drawText(QRect(rect.x(), rect.y() + 12, rect.width(), 20), Qt.AlignmentFlag.AlignCenter, title)

            painter.setFont(QFont("Arial", 8))
            painter.setPen(QColor(*theme["text_main"]))
            painter.drawText(QRect(rect.x() + 5, rect.y() + 35, rect.width() - 10, 60), Qt.AlignmentFlag.AlignCenter, desc)

        is_back_hovered = (self.hovered_btn == "back")
        if is_back_hovered:
            painter.setBrush(QColor(*theme["accent"], 40))
            painter.setPen(QPen(QColor(*theme["accent"]), 2))
        else:
            painter.setBrush(QColor(255, 255, 255, 12))
            painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.btn_back_rect, 6.0, 6.0)

        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255) if is_back_hovered else QColor(*theme["accent"]))
        painter.drawText(self.btn_back_rect, int(Qt.AlignmentFlag.AlignCenter), lang_dict["BACK"])

class StartMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 420, 390)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.drag_start = QPoint()
        self.is_dragging = False
        self.hovered_btn = None

        btn_w = 220
        btn_h = 42
        spacing = 15
        y_pos = 120
        
        self.btn_start = QRect((self.width() - btn_w) // 2, y_pos, btn_w, btn_h)
        self.btn_settings = QRect((self.width() - btn_w) // 2, y_pos + btn_h + spacing, btn_w, btn_h)
        self.btn_exit = QRect((self.width() - btn_w) // 2, y_pos + 2 * (btn_h + spacing), btn_w, btn_h)

        self.lang_switcher_rect = QRect(15, 15, 80, 26)
        self.lang_progress = 0.0 if APP_SETTINGS["lang"] == "RU" else 1.0
        self.lang_anim = QVariantAnimation(self)
        self.lang_anim.setDuration(250)
        self.lang_anim.valueChanged.connect(self._update_lang_progress)

    def _update_lang_progress(self, value):
        self.lang_progress = value
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        apply_fade_in(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self.lang_switcher_rect.contains(pos):
                new_lang = "ENG" if APP_SETTINGS["lang"] == "RU" else "RU"
                APP_SETTINGS["lang"] = new_lang
                self.lang_anim.setStartValue(self.lang_progress)
                self.lang_anim.setEndValue(1.0 if new_lang == "ENG" else 0.0)
                self.lang_anim.start()
            elif self.btn_start.contains(pos):
                def open_main():
                    self.close()
                    global media_app
                    media_app = MediaWindow()
                    media_app.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_main)
            elif self.btn_settings.contains(pos):
                def open_settings():
                    self.close()
                    global settings_app
                    settings_app = SettingsWindow()
                    settings_app.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_settings)
            elif self.btn_exit.contains(pos):
                apply_fade_out(self, duration=300, on_finished_callback=QApplication.quit)
            else:
                self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.is_dragging = True

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        old_hover = self.hovered_btn

        if self.btn_start.contains(pos):
            self.hovered_btn = "start"
        elif self.btn_settings.contains(pos):
            self.hovered_btn = "settings"
        elif self.btn_exit.contains(pos):
            self.hovered_btn = "exit"
        else:
            self.hovered_btn = None

        if old_hover != self.hovered_btn:
            self.update()

        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def draw_ru_flag(self, painter, rect):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(Qt.PenStyle.NoPen)
        
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(x, y, w, 3)
        
        painter.setBrush(QColor(0, 57, 166))
        painter.drawRect(x, y + 3, w, 3)
        
        painter.setBrush(QColor(213, 43, 30))
        painter.drawRect(x, y + 6, w, 3)
        
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(x, y, w - 1, h - 1)
        painter.restore()

    def draw_en_flag(self, painter, rect):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(1, 33, 105))
        painter.drawRect(x, y, w, h)
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(x, y, x + w, y + h)
        painter.drawLine(x, y + h, x + w, y)
        
        painter.setPen(QPen(QColor(200, 16, 46), 1))
        painter.drawLine(x, y, x + w, y + h)
        painter.drawLine(x, y + h, x + w, y)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(x + 4, y, 4, h)
        painter.drawRect(x, y + 3, w, 3)
        
        painter.setBrush(QColor(200, 16, 46))
        painter.drawRect(x + 5, y, 2, h)
        painter.drawRect(x, y + 4, w, 1)
        
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(x, y, w - 1, h - 1)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[0]
        lang_dict = TRANSLATIONS[APP_SETTINGS["lang"]]
        w = self.width()
        h = self.height()

        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, w - 10, h - 10, 12.0, 12.0)

        painter.setBrush(QColor(255, 255, 255, 15))
        painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.lang_switcher_rect, 13.0, 13.0)

        pill_x = self.lang_switcher_rect.x() + int(self.lang_progress * (self.lang_switcher_rect.width() / 2))
        pill_rect = QRect(pill_x, self.lang_switcher_rect.y(), self.lang_switcher_rect.width() // 2, self.lang_switcher_rect.height())
        painter.setBrush(QColor(*theme["accent"], 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(pill_rect, 13.0, 13.0)

        self.draw_ru_flag(painter, QRect(self.lang_switcher_rect.x() + 8, self.lang_switcher_rect.y() + 8, 12, 9))
        self.draw_en_flag(painter, QRect(self.lang_switcher_rect.x() + 48, self.lang_switcher_rect.y() + 8, 12, 9))

        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        painter.drawText(QRect(self.lang_switcher_rect.x() + 23, self.lang_switcher_rect.y(), 15, self.lang_switcher_rect.height()), Qt.AlignmentFlag.AlignCenter, "RU")
        painter.drawText(QRect(self.lang_switcher_rect.x() + 63, self.lang_switcher_rect.y(), 15, self.lang_switcher_rect.height()), Qt.AlignmentFlag.AlignCenter, "EN")

        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(10, 30, w - 20, 30), Qt.AlignmentFlag.AlignCenter, lang_dict["START_MENU"])

        font_btn = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font_btn)

        for btn_rect, label, key in [
            (self.btn_start, lang_dict["START"], "start"),
            (self.btn_settings, lang_dict["SETTINGS"], "settings"),
            (self.btn_exit, lang_dict["EXIT"], "exit")
        ]:
            is_hovered = (self.hovered_btn == key)
            if is_hovered:
                painter.setBrush(QColor(*theme["accent"], 40))
                painter.setPen(QPen(QColor(*theme["accent"]), 2))
            else:
                painter.setBrush(QColor(255, 255, 255, 12))
                painter.setPen(QPen(QColor(*theme["border"]), 1))
            
            painter.drawRoundedRect(btn_rect, 6.0, 6.0)
            
            if is_hovered:
                painter.setPen(QColor(255, 255, 255))
            else:
                painter.setPen(QColor(*theme["accent"]))
                
            painter.drawText(btn_rect, int(Qt.AlignmentFlag.AlignCenter), label)

        footer_text = lang_dict["MADE_WITH"]
        font_footer = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(font_footer)
        fm = painter.fontMetrics()
        
        text_w = fm.horizontalAdvance(footer_text)
        heart_text = " ♡"
        heart_w = fm.horizontalAdvance(heart_text)
        
        total_w = text_w + heart_w
        start_x = (w - total_w) // 2
        footer_y = h - 20
        
        painter.setPen(QColor(156, 163, 175, 150))
        painter.drawText(start_x, footer_y, footer_text)
        
        painter.setPen(QColor(*theme["accent"]))
        painter.drawText(start_x + text_w, footer_y, heart_text)

if __name__ == "__main__":
    apply_priority_mode(APP_SETTINGS["priority_mode"])
    app = QApplication(sys.argv)
    start_menu = StartMenuWindow()
    start_menu.show()
    sys.exit(app.exec())