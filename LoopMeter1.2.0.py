# -*- coding: utf-8 -*-

import os
import sys
import gc
import time
import platform
import psutil
import json

os.environ["QT_ANGLE_PLATFORM"] = "d3d9"
os.environ["QT_MEDIA_BACKEND"] = "windowsmediafoundation"
os.environ["QT_WMF_ALLOW_HARDWARE_DECODING"] = "1"
os.environ["QSG_RHI_BACKEND"] = "d3d11"
os.environ["QT_LOGGING_RULES"] = "*=false"
os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"

from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QStackedWidget, 
                             QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsOpacityEffect,
                             QMessageBox, QTextEdit, QLineEdit)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QMovie, QBrush, QPixmap, QPixmapCache, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QRect, QPoint, QSizeF, QPropertyAnimation, QVariantAnimation, QRectF, QPointF

if platform.system() == "Windows":
    import ctypes
    WIN_SUPPORT = True
else:
    WIN_SUPPORT = False

# Глобальные параметры (Deep Purple по умолчанию - индекс 1)
APP_SETTINGS = {
    "priority_mode": "BALANCED", 
    "lang": "RU",                 
    "show_telemetry": True,       
    "show_player": True,          
    "theme_idx": 1,               
    "last_media_path": None,      
    "root_dir": "NO_SAVE"         
}

WINDOW_POSITIONS = {
    "start_menu": QPoint(-1, -1),
    "settings": QPoint(-1, -1),
    "media_window": QPoint(-1, -1),
    "telemetry_window": QPoint(-1, -1)
}

TRANSLATIONS = {
    "RU": {
        "START_MENU": "ГЛАВНОЕ МЕНЮ",
        "START": "СТАРТ",
        "SETTINGS": "НАСТРОЙКИ",
        "EXIT": "ВЫХОД",
        "BACK": "НАЗАД",
        "CPU_SAVE_TITLE": "ЭКОНОМИЯ ОЗУ",
        "CPU_SAVE_DESC": "Приоритет ЦП\n\nЧастый опрос ЦП,\nкэш RAM очищен",
        "BAL_TITLE": "БАЛАНС",
        "BAL_DESC": "Обычный режим\n\nСтандартная нагрузка\nресурсы штатно",
        "MEM_SAVE_TITLE": "ЭКОНОМИЯ ЦП",
        "MEM_SAVE_DESC": "Приоритет ОЗУ\n\nРедкий опрос ЦП,\nкэширование в ОЗУ",
        "THEME": "ТЕМА",
        "MENU": "МЕНЮ",
        "DBL_CLICK": "Двойной клик для загрузки медиа",
        "R_CLICK": "Правый клик: закрепить/размер",
        "OPEN_MEDIA": "Открыть медиа",
        "MADE_WITH": "сделано с душой notvio",
        "ERROR_TITLE": "Ошибка",
        "ERROR_MSG": "Нельзя отключить обе функции!\nОставьте плеер или мониторинг.",
        "CAT_PERFORMANCE": "ПРОИЗВОДИТЕЛЬНОСТЬ",
        "CAT_INTERFACE": "ИНТЕРФЕЙС",
        "CAT_THEMES": "ТЕМЫ",
        "HIDE_TELEMETRY": "Скрыть показатели",
        "HIDE_TELEMETRY_DESC": "Скрывает окно нагрузки (CPU/RAM)",
        "HIDE_PLAYER": "Скрыть плеер",
        "HIDE_PLAYER_DESC": "Скрывает главное окно медиа",
        "DISK_TITLE": "ВЫБОР ДИСКА ДЛЯ ДАННЫХ",
        "DISK_DESC": "Приложение создаст папку 'LoopMeter' на выбранном диске для конфигов.",
        "DISK_ERR_TITLE": "Диск недоступен",
        "DISK_ERR_MSG": "Нет прав для записи на этот диск.",
        "NO_SAVE_MODE": "Без сохранения",
        "CMD_WELCOME": "Терминал LoopMeter.\nВведите /help для списка команд.\n\n",
        "CMD_HELP": ("Команды:\n"
                     "  /save config <имя> - Сохранить конфиг\n"
                     "  /load config <имя> - Загрузить конфиг\n"
                     "  /delete config <имя> - Удалить конфиг\n"
                     "  /list - Список файлов\n"
                     "  /clear - Очистить\n"),
        "CFG_EMPTY": "Нет сохраненных конфигураций",
        "CFG_CLICK_LOAD": "Кликните чтобы загрузить"
    },
    "ENG": {
        "START_MENU": "MAIN MENU",
        "START": "START",
        "SETTINGS": "SETTINGS",
        "EXIT": "EXIT",
        "BACK": "BACK",
        "CPU_SAVE_TITLE": "SAVE RAM",
        "CPU_SAVE_DESC": "CPU Priority\n\nFrequent CPU polling,\nRAM cache cleared",
        "BAL_TITLE": "BALANCED",
        "BAL_DESC": "Normal Mode\n\nStandard load\nresources normally",
        "MEM_SAVE_TITLE": "SAVE CPU",
        "MEM_SAVE_DESC": "RAM Priority\n\nRare CPU polling,\ncached in RAM",
        "THEME": "THEME",
        "MENU": "MENU",
        "DBL_CLICK": "Double-click to Load Media",
        "R_CLICK": "Right-click to Pin/Resize",
        "OPEN_MEDIA": "Open Media",
        "MADE_WITH": "made with soul by notvio",
        "ERROR_TITLE": "Error",
        "ERROR_MSG": "Cannot disable both functions!\nKeep player or monitoring.",
        "CAT_PERFORMANCE": "PERFORMANCE",
        "CAT_INTERFACE": "INTERFACE",
        "CAT_THEMES": "THEMES",
        "HIDE_TELEMETRY": "Hide Telemetry",
        "HIDE_TELEMETRY_DESC": "Hides the CPU/RAM overlay",
        "HIDE_PLAYER": "Hide Player",
        "HIDE_PLAYER_DESC": "Hides the main media window",
        "DISK_TITLE": "SELECT STORAGE DISK",
        "DISK_DESC": "The app will create a 'LoopMeter' folder on the chosen drive.",
        "DISK_ERR_TITLE": "Disk Error",
        "DISK_ERR_MSG": "No write permissions for this disk.",
        "NO_SAVE_MODE": "No Saving",
        "CMD_WELCOME": "LoopMeter Terminal.\nType /help for commands.\n\n",
        "CMD_HELP": ("Commands:\n"
                     "  /save config <name> - Save config\n"
                     "  /load config <name> - Load config\n"
                     "  /delete config <name> - Delete config\n"
                     "  /list - List files\n"
                     "  /clear - Clear screen\n"),
        "CFG_EMPTY": "No saved configurations found",
        "CFG_CLICK_LOAD": "Click to load"
    }
}

THEMES = [
    {"name": "NEON CYBER", "bg": (10, 15, 30, 250), "border": (34, 197, 94, 80), "cpu_bar": (34, 197, 94, 255), "ram_bar": (59, 130, 246, 255), "text_main": (255, 255, 255, 255), "accent": (34, 197, 94), "grad1": "#22c55e", "grad2": "#3b82f6"},
    {"name": "DEEP PURPLE", "bg": (20, 10, 35, 250), "border": (168, 85, 247, 80), "cpu_bar": (217, 70, 239, 255), "ram_bar": (129, 140, 248, 255), "text_main": (255, 255, 255, 255), "accent": (217, 70, 239), "grad1": "#d946ef", "grad2": "#818cf8"},
    {"name": "SOLAR FLARE", "bg": (25, 12, 10, 250), "border": (239, 68, 68, 80), "cpu_bar": (249, 115, 22, 255), "ram_bar": (234, 179, 8, 255), "text_main": (255, 255, 255, 255), "accent": (249, 115, 22), "grad1": "#f97316", "grad2": "#eab308"},
    {"name": "VIOLET-BLUE", "bg": (15, 15, 30, 250), "border": (84, 51, 255, 80), "cpu_bar": (84, 51, 255, 255), "ram_bar": (0, 255, 255, 255), "text_main": (255, 255, 255, 255), "accent": (84, 51, 255), "grad1": "#5433ff", "grad2": "#00ffff"},
    {"name": "CANDY", "bg": (25, 10, 25, 250), "border": (252, 0, 255, 80), "cpu_bar": (252, 0, 255, 255), "ram_bar": (0, 219, 222, 255), "text_main": (255, 255, 255, 255), "accent": (252, 0, 255), "grad1": "#fc00ff", "grad2": "#00dbde"},
    {"name": "GALAXY", "bg": (15, 20, 25, 250), "border": (44, 62, 80, 80), "cpu_bar": (44, 62, 80, 255), "ram_bar": (253, 116, 108, 255), "text_main": (255, 255, 255, 255), "accent": (253, 116, 108), "grad1": "#2c3e50", "grad2": "#fd746c"},
    {"name": "SUNSET", "bg": (25, 15, 10, 250), "border": (255, 69, 0, 80), "cpu_bar": (255, 69, 0, 255), "ram_bar": (255, 165, 0, 255), "text_main": (255, 255, 255, 255), "accent": (255, 69, 0), "grad1": "#ff4500", "grad2": "#ffa500"},
    {"name": "EUCALYPTUS", "bg": (10, 25, 20, 250), "border": (68, 215, 168, 80), "cpu_bar": (68, 215, 168, 255), "ram_bar": (0, 100, 66, 255), "text_main": (255, 255, 255, 255), "accent": (68, 215, 168), "grad1": "#44d7a8", "grad2": "#006442"},
    {"name": "SIMPLE GRAY", "bg": (20, 20, 20, 250), "border": (150, 150, 150, 80), "cpu_bar": (200, 200, 200, 255), "ram_bar": (100, 100, 100, 255), "text_main": (255, 255, 255, 255), "accent": (150, 150, 150), "grad1": "#969696", "grad2": "#646464"}
]

def apply_priority_mode(mode):
    try:
        p = psutil.Process(os.getpid())
        if mode == "CPU":
            p.nice(psutil.HIGH_PRIORITY_CLASS if sys.platform == "win32" else -10)
            gc.enable()
            gc.set_threshold(10, 2, 2)
            gc.collect()
            QPixmapCache.clear()
        elif mode == "MEM":
            p.nice(psutil.IDLE_PRIORITY_CLASS if sys.platform == "win32" else 19)
            gc.disable()
            QPixmapCache.setCacheLimit(102400)
        else:
            p.nice(psutil.NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 0)
            gc.enable()
            gc.set_threshold(700, 10, 10)
            gc.collect()
            QPixmapCache.setCacheLimit(10240)
    except Exception:
        pass

def check_existing_install():
    for drive in ["C", "D"]:
        path = f"{drive}:/LoopMeter/configs/session.json"
        if os.path.exists(path):
            APP_SETTINGS["root_dir"] = f"{drive}:/LoopMeter"
            load_current_session()
            return True
    return False

def test_and_setup_directory(drive_letter):
    if drive_letter == "NO_SAVE":
        APP_SETTINGS["root_dir"] = "NO_SAVE"
        return True
    root_path = f"{drive_letter}:/LoopMeter"
    try:
        os.makedirs(os.path.join(root_path, "configs"), exist_ok=True)
        readme_file = os.path.join(root_path, "readme.txt")
        if not os.path.exists(readme_file):
            content = (
                "Привет! Я очень стараюсь над разработкой этой программы и искренне надеюсь на твой фидбек!\n"
                "Чтобы вернуться назад в меню, когда ты зашел в медиаплеер, просто нажми клавишу Escape (Esc) на клавиатуре.\n\n"
                "Hello! I am trying really hard on this program and sincerely hope for your feedback!\n"
                "To return back to the menu when you are inside the media player, simply press the Escape (Esc) key on your keyboard."
            )
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)
        APP_SETTINGS["root_dir"] = root_path
        return True
    except Exception:
        return False

def get_config_filepath(name):
    base_dir = os.path.join(APP_SETTINGS["root_dir"], "configs")
    return os.path.join(base_dir, f"{name}.json")

def load_config_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            APP_SETTINGS["theme_idx"] = data.get("theme_idx", APP_SETTINGS["theme_idx"])
            APP_SETTINGS["priority_mode"] = data.get("priority_mode", APP_SETTINGS["priority_mode"])
            apply_priority_mode(APP_SETTINGS["priority_mode"])
            APP_SETTINGS["lang"] = data.get("lang", APP_SETTINGS["lang"])
            APP_SETTINGS["show_telemetry"] = data.get("show_telemetry", APP_SETTINGS["show_telemetry"])
            APP_SETTINGS["show_player"] = data.get("show_player", APP_SETTINGS["show_player"])
            APP_SETTINGS["last_media_path"] = data.get("last_media_path", APP_SETTINGS["last_media_path"])
            pos = data.get("positions", {})
            for key in WINDOW_POSITIONS:
                if key in pos:
                    WINDOW_POSITIONS[key] = QPoint(pos[key][0], pos[key][1])
            return True
    except Exception:
        return False

def save_config_data(file_path):
    try:
        data = {
            "theme_idx": APP_SETTINGS["theme_idx"],
            "priority_mode": APP_SETTINGS["priority_mode"],
            "lang": APP_SETTINGS["lang"],
            "show_telemetry": APP_SETTINGS["show_telemetry"],
            "show_player": APP_SETTINGS["show_player"],
            "last_media_path": APP_SETTINGS["last_media_path"],
            "positions": { k: [v.x(), v.y()] for k, v in WINDOW_POSITIONS.items() }
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def save_current_session():
    if APP_SETTINGS["root_dir"] == "NO_SAVE": return
    save_config_data(os.path.join(APP_SETTINGS["root_dir"], "configs", "session.json"))

def load_current_session():
    if APP_SETTINGS["root_dir"] == "NO_SAVE": return
    session_file = os.path.join(APP_SETTINGS["root_dir"], "configs", "session.json")
    if os.path.exists(session_file):
        load_config_data(session_file)

def apply_fade_in(window, duration=250):
    effect = QGraphicsOpacityEffect(window)
    window.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.finished.connect(lambda: window.setGraphicsEffect(None))
    window._fade_anim = anim
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def apply_fade_out(window, duration=300, on_finished_callback=None):
    effect = QGraphicsOpacityEffect(window)
    window.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    def on_fin():
        window.setGraphicsEffect(None)
        if on_finished_callback: on_finished_callback()
    anim.finished.connect(on_fin)
    window._fade_anim = anim
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def set_window_topmost(hwnd, topmost=True):
    if not WIN_SUPPORT or not hwnd: return
    ctypes.windll.user32.SetWindowPos(hwnd, -1 if topmost else -2, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)

def find_companion_audio(media_path):
    base, _ = os.path.splitext(media_path)
    for ext in [".mp3", ".wav"]:
        audio_path = base + ext
        if os.path.exists(audio_path):
            return audio_path
    return None

class TelemetryWorker(QThread):
    stats_updated = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.running = True
    def run(self):
        psutil.cpu_percent()
        while self.running:
            try:
                self.stats_updated.emit({"cpu": psutil.cpu_percent(interval=None), "ram": psutil.virtual_memory().percent})
                mode = APP_SETTINGS["priority_mode"]
                self.msleep(3000 if mode == "MEM" else (500 if mode == "CPU" else 1200))
            except: pass
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
            try: self.hwnd = int(self.window.winId())
            except Exception: self.hwnd = None

        if WIN_SUPPORT and self.hwnd:
            set_window_topmost(self.hwnd, self.is_pinned)
        else:
            flags = self.window.windowFlags()
            if self.is_pinned: flags |= Qt.WindowType.WindowStaysOnTopHint
            else: flags &= ~Qt.WindowType.WindowStaysOnTopHint
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


class DiskSelectionDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 420, 240)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.move((QApplication.primaryScreen().geometry().width() - self.width()) // 2, 
                  (QApplication.primaryScreen().geometry().height() - self.height()) // 2)
        
        self.drag_start = QPoint()
        self.is_dragging = False
        self.hovered_btn = None
        
        self.btn_c_rect = QRect(25, 130, 115, 45)
        self.btn_d_rect = QRect(150, 130, 115, 45)
        self.btn_nosave_rect = QRect(275, 130, 120, 45)

    def showEvent(self, event):
        super().showEvent(event)
        apply_fade_in(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self.btn_c_rect.contains(pos): self.process_disk("C")
            elif self.btn_d_rect.contains(pos): self.process_disk("D")
            elif self.btn_nosave_rect.contains(pos): self.process_disk("NO_SAVE")
            else:
                self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.is_dragging = True

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self.btn_c_rect.contains(pos): self.hovered_btn = "C"
        elif self.btn_d_rect.contains(pos): self.hovered_btn = "D"
        elif self.btn_nosave_rect.contains(pos): self.hovered_btn = "NOSAVE"
        else: self.hovered_btn = None
        self.update()
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.is_dragging = False

    def process_disk(self, choice):
        if not test_and_setup_directory(choice):
            if QMessageBox.warning(self, "Ошибка", "Нет прав для записи", QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Ignore) == QMessageBox.StandardButton.Ignore:
                test_and_setup_directory("NO_SAVE")
            else: return 
        if APP_SETTINGS["root_dir"] != "NO_SAVE": load_current_session()
        def open_main():
            self.close()
            global start_menu
            start_menu = StartMenuWindow()
            start_menu.show()
        apply_fade_out(self, duration=300, on_finished_callback=open_main)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        lang = TRANSLATIONS[APP_SETTINGS["lang"]]
        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, self.width() - 10, self.height() - 10, 12.0, 12.0)
        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(QRect(10, 25, self.width() - 20, 25), Qt.AlignmentFlag.AlignCenter, lang["DISK_TITLE"])
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QColor(156, 163, 175))
        painter.drawText(QRect(20, 55, self.width() - 40, 55), int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap), lang["DISK_DESC"])

        for rect, text, key in [(self.btn_c_rect, "C:", "C"), (self.btn_d_rect, "D:", "D"), (self.btn_nosave_rect, lang["NO_SAVE_MODE"], "NOSAVE")]:
            hovered = (self.hovered_btn == key)
            painter.setBrush(QColor(*theme["accent"], 40) if hovered else QColor(255, 255, 255, 12))
            painter.setPen(QPen(QColor(*theme["accent"]), 2) if hovered else QPen(QColor(*theme["border"]), 1))
            painter.drawRoundedRect(rect, 6.0, 6.0)
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255) if hovered else QColor(*theme["accent"]))
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)


class StartMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 420, 390)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        if WINDOW_POSITIONS["start_menu"].x() != -1: self.move(WINDOW_POSITIONS["start_menu"])
        else: self.move((QApplication.primaryScreen().geometry().width() - self.width()) // 2, (QApplication.primaryScreen().geometry().height() - self.height()) // 2)

        self.drag_start = QPoint()
        self.is_dragging = False
        self.hovered_btn = None

        y_pos = 120
        self.btn_start = QRect((self.width() - 220) // 2, y_pos, 220, 42)
        self.btn_settings = QRect((self.width() - 220) // 2, y_pos + 57, 220, 42)
        self.btn_exit = QRect((self.width() - 220) // 2, y_pos + 114, 220, 42)

        self.lang_switcher_rect = QRect(15, 15, 80, 26)
        self.lang_progress = 0.0 if APP_SETTINGS["lang"] == "RU" else 1.0
        self.lang_anim = QVariantAnimation(self)
        self.lang_anim.setDuration(250)
        self.lang_anim.valueChanged.connect(self._update_lang_progress)

    def moveEvent(self, event):
        super().moveEvent(event)
        WINDOW_POSITIONS["start_menu"] = self.pos()

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
                APP_SETTINGS["lang"] = "ENG" if APP_SETTINGS["lang"] == "RU" else "RU"
                self.lang_anim.setStartValue(self.lang_progress)
                self.lang_anim.setEndValue(1.0 if APP_SETTINGS["lang"] == "ENG" else 0.0)
                self.lang_anim.start()
            elif self.btn_start.contains(pos):
                def open_main():
                    self.close()
                    global media_app
                    media_app = MediaWindow()
                    media_app.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_main)
            elif self.btn_settings.contains(pos):
                def open_set():
                    self.close()
                    global settings_app
                    settings_app = SettingsWindow()
                    settings_app.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_set)
            elif self.btn_exit.contains(pos):
                apply_fade_out(self, duration=300, on_finished_callback=QApplication.quit)
            else:
                self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.is_dragging = True

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self.btn_start.contains(pos): self.hovered_btn = "start"
        elif self.btn_settings.contains(pos): self.hovered_btn = "settings"
        elif self.btn_exit.contains(pos): self.hovered_btn = "exit"
        else: self.hovered_btn = None
        self.update()
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.is_dragging = False

    def draw_ru_flag(self, painter, rect):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        painter.setBrush(QColor(255, 255, 255)); painter.drawRect(x, y, w, 3)
        painter.setBrush(QColor(0, 57, 166)); painter.drawRect(x, y + 3, w, 3)
        painter.setBrush(QColor(213, 43, 30)); painter.drawRect(x, y + 6, w, 3)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1)); painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(x, y, w - 1, h - 1)
        painter.restore()

    def draw_en_flag(self, painter, rect):
        painter.save()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QColor(1, 33, 105)); painter.drawRect(x, y, w, h)
        painter.setPen(QPen(QColor(255, 255, 255), 2)); painter.drawLine(x, y, x + w, y + h); painter.drawLine(x, y + h, x + w, y)
        painter.setPen(QPen(QColor(200, 16, 46), 1)); painter.drawLine(x, y, x + w, y + h); painter.drawLine(x, y + h, x + w, y)
        painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(x + 4, y, 4, h); painter.drawRect(x, y + 3, w, 3)
        painter.setBrush(QColor(200, 16, 46)); painter.drawRect(x + 5, y, 2, h); painter.drawRect(x, y + 4, w, 1)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1)); painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(x, y, w - 1, h - 1)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        lang = TRANSLATIONS[APP_SETTINGS["lang"]]
        
        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, self.width() - 10, self.height() - 10, 12.0, 12.0)

        # Переключатель языков
        painter.setBrush(QColor(255, 255, 255, 15)); painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.lang_switcher_rect, 13.0, 13.0)
        pill_x = self.lang_switcher_rect.x() + int(self.lang_progress * (self.lang_switcher_rect.width() / 2))
        painter.setBrush(QColor(*theme["accent"], 80)); painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRect(pill_x, self.lang_switcher_rect.y(), self.lang_switcher_rect.width() // 2, self.lang_switcher_rect.height()), 13.0, 13.0)
        
        self.draw_ru_flag(painter, QRect(self.lang_switcher_rect.x() + 8, self.lang_switcher_rect.y() + 8, 12, 9))
        self.draw_en_flag(painter, QRect(self.lang_switcher_rect.x() + 48, self.lang_switcher_rect.y() + 8, 12, 9))

        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(10, 30, self.width() - 20, 30), Qt.AlignmentFlag.AlignCenter, lang["START_MENU"])

        for rect, label, key in [(self.btn_start, lang["START"], "start"), (self.btn_settings, lang["SETTINGS"], "settings"), (self.btn_exit, lang["EXIT"], "exit")]:
            hov = (self.hovered_btn == key)
            painter.setBrush(QColor(*theme["accent"], 40) if hov else QColor(255, 255, 255, 12))
            painter.setPen(QPen(QColor(*theme["accent"]), 2) if hov else QPen(QColor(*theme["border"]), 1))
            painter.drawRoundedRect(rect, 6.0, 6.0)
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255) if hov else QColor(*theme["accent"]))
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), label)

    def closeEvent(self, event):
        WINDOW_POSITIONS["start_menu"] = self.pos()
        save_current_session()
        event.accept()

# ==================== SETTINGS WINDOW ====================
class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 640, 420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        if WINDOW_POSITIONS["settings"].x() != -1: self.move(WINDOW_POSITIONS["settings"])
        else: self.move((QApplication.primaryScreen().geometry().width() - self.width()) // 2, (QApplication.primaryScreen().geometry().height() - self.height()) // 2)

        self.drag_start = QPoint()
        self.is_dragging = False
        self.hovered_btn = None
        self.right_pane_mode = "perf" 

        # Боковое меню
        self.cat_perf_rect = QRect(15, 60, 160, 40)
        self.cat_interface_rect = QRect(15, 110, 160, 40)
        self.cat_themes_rect = QRect(15, 160, 160, 40)
        self.btn_back_rect = QRect(15, 365, 160, 40)

        # Векторные иконки сверху справа
        self.folder_icon_rect = QRect(545, 20, 32, 32)
        self.gear_icon_rect = QRect(585, 20, 32, 32)

        # Плитки Производительности
        self.col_cpu_rect = QRect(200, 110, 134, 180)
        self.col_bal_rect = QRect(346, 110, 134, 180)
        self.col_mem_rect = QRect(492, 110, 134, 180)

        # Плитки Интерфейса
        self.toggle_telemetry_rect = QRect(210, 110, 410, 80)
        self.toggle_player_rect = QRect(210, 205, 410, 80)

        # Терминал
        self.console_output = QTextEdit(self)
        self.console_output.setGeometry(200, 80, 420, 270)
        self.console_output.setReadOnly(True)
        self.console_output.setFrameStyle(0)
        self.console_output.hide()

        self.console_input = QLineEdit(self)
        self.console_input.setGeometry(200, 365, 420, 32)
        self.console_input.returnPressed.connect(self.handle_command)
        self.console_input.hide()

        self.term_eff_out = QGraphicsOpacityEffect(self.console_output)
        self.term_eff_in = QGraphicsOpacityEffect(self.console_input)
        self.console_output.setGraphicsEffect(self.term_eff_out)
        self.console_input.setGraphicsEffect(self.term_eff_in)

        # Анимация прозрачности правой панели
        self.pane_opacity = 1.0
        self.pane_anim = QVariantAnimation(self)
        self.pane_anim.setDuration(200)
        self.pane_anim.valueChanged.connect(self._update_pane_opacity)

        self.setup_terminal_style()
        self.print_to_console(TRANSLATIONS[APP_SETTINGS["lang"]]["CMD_WELCOME"], "accent")
        self.config_list_rects = []
        self.theme_list_rects = [] 

    def _update_pane_opacity(self, value):
        self.pane_opacity = value
        self.term_eff_out.setOpacity(value)
        self.term_eff_in.setOpacity(value)
        self.update()

    def moveEvent(self, event):
        super().moveEvent(event)
        WINDOW_POSITIONS["settings"] = self.pos()

    def showEvent(self, event):
        super().showEvent(event)
        apply_fade_in(self)

    def setup_terminal_style(self):
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        bg_hex = f"rgba({theme['bg'][0]}, {theme['bg'][1]}, {theme['bg'][2]}, 0.85)"
        border_hex = f"rgba({theme['border'][0]}, {theme['border'][1]}, {theme['border'][2]}, 0.7)"
        accent_hex = f"rgb({theme['accent'][0]}, {theme['accent'][1]}, {theme['accent'][2]})"

        self.console_output.setStyleSheet(f"QTextEdit {{ background-color: {bg_hex}; color: #FFFFFF; border: 1px solid {border_hex}; border-radius: 6px; font-family: 'Consolas', monospace; font-size: 11px; padding: 10px; }}")
        self.console_input.setStyleSheet(f"QLineEdit {{ background-color: {bg_hex}; color: #FFFFFF; border: 1px solid {border_hex}; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 12px; padding-left: 10px; }} QLineEdit:focus {{ border: 1.5px solid {accent_hex}; }}")

    def print_to_console(self, text, color_type="main"):
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        accent = f"rgb({theme['accent'][0]}, {theme['accent'][1]}, {theme['accent'][2]})"
        if color_type == "accent": html = f"<span style='color: {accent}; font-weight: bold;'>{text}</span>"
        elif color_type == "error": html = f"<span style='color: #ef4444; font-weight: bold;'>[ERROR] {text}</span>"
        elif color_type == "success": html = f"<span style='color: #10b981; font-weight: bold;'>[SUCCESS] {text}</span>"
        else: html = f"<span style='color: #e5e7eb;'>{text}</span>"
        self.console_output.append(html)
        self.console_output.ensureCursorVisible()

    def handle_command(self):
        raw_cmd = self.console_input.text().strip()
        self.console_input.clear()
        if not raw_cmd: return
        self.print_to_console(f"\n> {raw_cmd}", "main")
        parts = raw_cmd.split()
        cmd = parts[0].lower()

        if cmd == "/help": self.print_to_console(TRANSLATIONS[APP_SETTINGS["lang"]]["CMD_HELP"], "main")
        elif cmd == "/clear":
            self.console_output.clear()
            self.print_to_console(TRANSLATIONS[APP_SETTINGS["lang"]]["CMD_WELCOME"], "accent")
        elif cmd == "/list":
            if APP_SETTINGS["root_dir"] == "NO_SAVE":
                self.print_to_console("Saves disabled.", "error")
                return
            cdir = os.path.join(APP_SETTINGS["root_dir"], "configs")
            if os.path.exists(cdir):
                files = [f[:-5] for f in os.listdir(cdir) if f.endswith(".json") and f != "session.json"]
                if files: self.print_to_console("Configs:\n" + "\n".join(f" - {f}" for f in files), "accent")
                else: self.print_to_console("No configs found.", "main")
        elif cmd == "/save":
            if len(parts) < 3 or parts[1].lower() != "config":
                self.print_to_console("Syntax: /save config <name>", "error")
                return
            if save_config_data(get_config_filepath(parts[2])):
                self.print_to_console(f"Saved: {parts[2]}", "success")
                self.update()
        elif cmd == "/load":
            if len(parts) < 3 or parts[1].lower() != "config":
                self.print_to_console("Syntax: /load config <name>", "error")
                return
            path = get_config_filepath(parts[2])
            if os.path.exists(path):
                if load_config_data(path):
                    self.print_to_console(f"Loaded: {parts[2]}", "success")
                    self.setup_terminal_style()
                    self.update()
            else: self.print_to_console("Not found.", "error")
        elif cmd == "/delete":
            if len(parts) < 3 or parts[1].lower() != "config": return
            path = get_config_filepath(parts[2])
            if os.path.exists(path):
                os.remove(path)
                self.print_to_console(f"Deleted: {parts[2]}", "success")
                self.update()
        else: self.print_to_console(f"Unknown: {cmd}", "error")

    def toggle_right_pane(self, mode):
        if self.right_pane_mode == mode: return
        self.right_pane_mode = mode
        
        self.pane_anim.setStartValue(0.0)
        self.pane_anim.setEndValue(1.0)
        self.pane_anim.start()

        if mode == "terminal":
            self.console_output.show()
            self.console_input.show()
            self.console_input.setFocus()
        else:
            self.console_output.hide()
            self.console_input.hide()
            self.console_input.clearFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # Левое меню
            if self.cat_perf_rect.contains(pos): self.toggle_right_pane("perf")
            elif self.cat_interface_rect.contains(pos): self.toggle_right_pane("interface")
            elif self.cat_themes_rect.contains(pos): self.toggle_right_pane("themes")
            elif self.btn_back_rect.contains(pos):
                def open_start():
                    self.close()
                    global start_menu
                    start_menu = StartMenuWindow()
                    start_menu.show()
                apply_fade_out(self, duration=300, on_finished_callback=open_start)
                
            # Иконки Топ-Райт
            elif self.folder_icon_rect.contains(pos): self.toggle_right_pane("config_list")
            elif self.gear_icon_rect.contains(pos): self.toggle_right_pane("terminal")
            
            # Сетка тем
            elif self.right_pane_mode == "themes":
                for rect, idx in self.theme_list_rects:
                    if rect.contains(pos):
                        APP_SETTINGS["theme_idx"] = idx
                        self.setup_terminal_style()
                        self.update()
                        break
                else:
                    self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self.is_dragging = True

            elif self.right_pane_mode == "config_list":
                for rect, cfg_name in self.config_list_rects:
                    if rect.contains(pos):
                        path = get_config_filepath(cfg_name)
                        if os.path.exists(path):
                            load_config_data(path)
                            self.setup_terminal_style()
                            self.update()
                        break
                else:
                    self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self.is_dragging = True

            elif self.right_pane_mode == "perf":
                if self.col_cpu_rect.contains(pos): APP_SETTINGS["priority_mode"] = "CPU"; apply_priority_mode("CPU"); self.update()
                elif self.col_bal_rect.contains(pos): APP_SETTINGS["priority_mode"] = "BALANCED"; apply_priority_mode("BALANCED"); self.update()
                elif self.col_mem_rect.contains(pos): APP_SETTINGS["priority_mode"] = "MEM"; apply_priority_mode("MEM"); self.update()
                else: self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); self.is_dragging = True
            
            elif self.right_pane_mode == "interface":
                if self.toggle_telemetry_rect.contains(pos):
                    if APP_SETTINGS["show_telemetry"] and not APP_SETTINGS["show_player"]: QMessageBox.critical(self, "Error", TRANSLATIONS[APP_SETTINGS["lang"]]["ERROR_MSG"])
                    else: APP_SETTINGS["show_telemetry"] = not APP_SETTINGS["show_telemetry"]; self.update()
                elif self.toggle_player_rect.contains(pos):
                    if APP_SETTINGS["show_player"] and not APP_SETTINGS["show_telemetry"]: QMessageBox.critical(self, "Error", TRANSLATIONS[APP_SETTINGS["lang"]]["ERROR_MSG"])
                    else: APP_SETTINGS["show_player"] = not APP_SETTINGS["show_player"]; self.update()
                else: self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); self.is_dragging = True
            else:
                self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); self.is_dragging = True

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        old_hover = self.hovered_btn

        if self.cat_perf_rect.contains(pos): self.hovered_btn = "cat_perf"
        elif self.cat_interface_rect.contains(pos): self.hovered_btn = "cat_interface"
        elif self.cat_themes_rect.contains(pos): self.hovered_btn = "cat_themes"
        elif self.btn_back_rect.contains(pos): self.hovered_btn = "back"
        elif self.folder_icon_rect.contains(pos): self.hovered_btn = "folder"
        elif self.gear_icon_rect.contains(pos): self.hovered_btn = "gear"
        
        elif self.right_pane_mode == "themes":
            self.hovered_btn = None
            for rect, idx in self.theme_list_rects:
                if rect.contains(pos): self.hovered_btn = f"theme_{idx}"; break
                
        elif self.right_pane_mode == "config_list":
            self.hovered_btn = None
            for rect, cfg_name in self.config_list_rects:
                if rect.contains(pos): self.hovered_btn = f"cfg_{cfg_name}"; break
                
        elif self.right_pane_mode == "perf":
            if self.col_cpu_rect.contains(pos): self.hovered_btn = "cpu"
            elif self.col_bal_rect.contains(pos): self.hovered_btn = "bal"
            elif self.col_mem_rect.contains(pos): self.hovered_btn = "mem"
            else: self.hovered_btn = None
            
        elif self.right_pane_mode == "interface":
            if self.toggle_telemetry_rect.contains(pos): self.hovered_btn = "toggle_telemetry"
            elif self.toggle_player_rect.contains(pos): self.hovered_btn = "toggle_player"
            else: self.hovered_btn = None
        else: self.hovered_btn = None

        if old_hover != self.hovered_btn: self.update()
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.is_dragging = False

    def draw_folder_icon(self, painter, rect, color):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        x, y = rect.x() + 6, rect.y() + 8
        w, h = rect.width() - 12, rect.height() - 16
        
        path = QPainterPath()
        path.moveTo(x, y + h*0.2)
        path.lineTo(x + w*0.35, y + h*0.2)
        path.lineTo(x + w*0.5, y + h*0.35)
        path.lineTo(x + w, y + h*0.35)
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        path.closeSubpath()
        
        painter.drawPath(path)
        painter.drawLine(x, int(y + h*0.35), int(x + w), int(y + h*0.35))
        painter.restore()

    def draw_gear_icon(self, painter, rect, color):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = rect.center().x(), rect.center().y()
        r = (min(rect.width(), rect.height()) - 16) / 2.0
        
        painter.setPen(QPen(color, r * 0.45, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.translate(cx, cy)
        for i in range(6):
            painter.drawLine(0, int(-r*1.4), 0, int(r*1.4))
            painter.rotate(30)
            
        painter.setPen(QPen(color, r * 0.45))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, 0), r*1.1, r*1.1)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        lang = TRANSLATIONS[APP_SETTINGS["lang"]]
        
        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, self.width() - 10, self.height() - 10, 12.0, 12.0)

        painter.setBrush(QColor(255, 255, 255, 5))
        painter.setPen(QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(10, 10, 175, self.height() - 20, 10.0, 10.0)

        painter.setPen(QColor(*theme["text_main"]))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRect(10, 25, 175, 25), Qt.AlignmentFlag.AlignCenter, lang["SETTINGS"])

        for rect, label, mode, hov_key in [
            (self.cat_perf_rect, lang["CAT_PERFORMANCE"], "perf", "cat_perf"),
            (self.cat_interface_rect, lang["CAT_INTERFACE"], "interface", "cat_interface"),
            (self.cat_themes_rect, lang["CAT_THEMES"], "themes", "cat_themes")
        ]:
            is_active = (self.right_pane_mode == mode)
            is_hover = (self.hovered_btn == hov_key)
            painter.setBrush(QColor(*theme["accent"], 40) if is_active else (QColor(255, 255, 255, 15) if is_hover else QColor(255, 255, 255, 5)))
            painter.setPen(QPen(QColor(*theme["accent"]), 2) if is_active else (QPen(QColor(*theme["accent"]), 1) if is_hover else QPen(QColor(*theme["border"]), 1)))
            painter.drawRoundedRect(rect, 6.0, 6.0)
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255) if is_active else QColor(*theme["accent"]))
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), label)

        is_back_hovered = (self.hovered_btn == "back")
        painter.setBrush(QColor(*theme["accent"], 40) if is_back_hovered else QColor(255, 255, 255, 12))
        painter.setPen(QPen(QColor(*theme["accent"]), 2) if is_back_hovered else QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.btn_back_rect, 6.0, 6.0)
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255) if is_back_hovered else QColor(*theme["accent"]))
        painter.drawText(self.btn_back_rect, int(Qt.AlignmentFlag.AlignCenter), lang["BACK"])

        f_hov = (self.hovered_btn == "folder") or (self.right_pane_mode == "config_list")
        painter.setBrush(QColor(*theme["accent"], 40) if f_hov else QColor(255, 255, 255, 10))
        painter.setPen(QPen(QColor(*theme["accent"]), 2) if f_hov else QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.folder_icon_rect, 6.0, 6.0)
        self.draw_folder_icon(painter, self.folder_icon_rect, QColor(255, 255, 255) if f_hov else QColor(*theme["accent"]))

        g_hov = (self.hovered_btn == "gear") or (self.right_pane_mode == "terminal")
        painter.setBrush(QColor(*theme["accent"], 40) if g_hov else QColor(255, 255, 255, 10))
        painter.setPen(QPen(QColor(*theme["accent"]), 2) if g_hov else QPen(QColor(*theme["border"]), 1))
        painter.drawRoundedRect(self.gear_icon_rect, 6.0, 6.0)
        self.draw_gear_icon(painter, self.gear_icon_rect, QColor(255, 255, 255) if g_hov else QColor(*theme["accent"]))

        painter.setOpacity(self.pane_opacity)

        if self.right_pane_mode == "themes":
            painter.setPen(QColor(*theme["text_main"]))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(QRect(200, 30, 340, 30), Qt.AlignmentFlag.AlignCenter, lang["CAT_THEMES"])

            self.theme_list_rects.clear()
            x_start, y_start = 200, 80
            w_item, h_item = 130, 80
            gap_x, gap_y = 15, 15
            col, row = 0, 0

            for idx, th in enumerate(THEMES):
                rect = QRect(x_start + col*(w_item+gap_x), y_start + row*(h_item+gap_y), w_item, h_item)
                self.theme_list_rects.append((rect, idx))

                is_selected = (APP_SETTINGS["theme_idx"] == idx)
                hov = (self.hovered_btn == f"theme_{idx}")

                # Исправление QPointF для градиента
                grad = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
                grad.setColorAt(0.0, QColor(th.get("grad1", "#ffffff")))
                grad.setColorAt(1.0, QColor(th.get("grad2", "#000000")))
                painter.setBrush(QBrush(grad))

                if is_selected:
                    painter.setPen(QPen(QColor(255, 255, 255), 3))
                elif hov:
                    painter.setPen(QPen(QColor(255, 255, 255, 150), 2))
                else:
                    painter.setPen(Qt.PenStyle.NoPen)

                painter.drawRoundedRect(rect, 8.0, 8.0)

                painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                painter.setPen(QColor(0, 0, 0, 150))
                painter.drawText(QRect(rect.x()+1, rect.y()+1, rect.width(), rect.height()), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, th["name"])
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, th["name"])

                col += 1
                if col > 2:
                    col = 0
                    row += 1

        elif self.right_pane_mode == "perf":
            painter.setPen(QColor(*theme["text_main"]))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(QRect(200, 30, 340, 30), Qt.AlignmentFlag.AlignCenter, lang["CAT_PERFORMANCE"])
            for rect, title, desc, key in [(self.col_cpu_rect, lang["CPU_SAVE_TITLE"], lang["CPU_SAVE_DESC"], "cpu"),
                                           (self.col_bal_rect, lang["BAL_TITLE"], lang["BAL_DESC"], "bal"),
                                           (self.col_mem_rect, lang["MEM_SAVE_TITLE"], lang["MEM_SAVE_DESC"], "mem")]:
                is_selected = (APP_SETTINGS["priority_mode"] == key.upper() if key != "bal" else APP_SETTINGS["priority_mode"] == "BALANCED")
                hov = (self.hovered_btn == key)
                painter.setBrush(QColor(*theme["accent"], 40) if is_selected else (QColor(255,255,255,20) if hov else QColor(255,255,255,10)))
                painter.setPen(QPen(QColor(*theme["accent"]), 2) if is_selected else (QPen(QColor(*theme["accent"]), 1) if hov else QPen(QColor(*theme["border"]), 1)))
                painter.drawRoundedRect(rect, 8.0, 8.0)
                painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                painter.setPen(QColor(255, 255, 255) if is_selected else QColor(*theme["accent"]))
                painter.drawText(QRect(rect.x(), rect.y() + 15, rect.width(), 20), Qt.AlignmentFlag.AlignCenter, title)
                painter.setFont(QFont("Arial", 8))
                painter.setPen(QColor(*theme["text_main"]))
                painter.drawText(QRect(rect.x() + 5, rect.y() + 45, rect.width() - 10, 110), Qt.AlignmentFlag.AlignCenter, desc)

        elif self.right_pane_mode == "interface":
            painter.setPen(QColor(*theme["text_main"]))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(QRect(200, 30, 340, 30), Qt.AlignmentFlag.AlignCenter, lang["CAT_INTERFACE"])
            for rect, title, desc, is_en, key in [
                (self.toggle_telemetry_rect, lang["HIDE_TELEMETRY"], lang["HIDE_TELEMETRY_DESC"], not APP_SETTINGS["show_telemetry"], "toggle_telemetry"),
                (self.toggle_player_rect, lang["HIDE_PLAYER"], lang["HIDE_PLAYER_DESC"], not APP_SETTINGS["show_player"], "toggle_player")]:
                hov = (self.hovered_btn == key)
                painter.setBrush(QColor(*theme["accent"], 40) if is_en else (QColor(255,255,255,20) if hov else QColor(255,255,255,10)))
                painter.setPen(QPen(QColor(*theme["accent"]), 2) if is_en else (QPen(QColor(*theme["accent"]), 1) if hov else QPen(QColor(*theme["border"]), 1)))
                painter.drawRoundedRect(rect, 8.0, 8.0)
                painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                painter.setPen(QColor(255, 255, 255) if is_en else QColor(*theme["accent"]))
                painter.drawText(rect.x() + 15, rect.y() + 28, title)
                painter.setFont(QFont("Arial", 8))
                painter.setPen(QColor(*theme["text_main"]))
                painter.drawText(rect.x() + 15, rect.y() + 48, desc)
                switch_rect = QRect(rect.x() + rect.width() - 75, rect.y() + 25, 60, 30)
                painter.setBrush(QColor(*theme["accent"]) if is_en else QColor(51, 65, 85, 150))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(switch_rect, 15.0, 15.0)
                painter.setBrush(QColor(255, 255, 255))
                painter.drawEllipse(QRect(switch_rect.x() + (33 if is_en else 3), switch_rect.y() + 3, 24, 24))

        elif self.right_pane_mode == "config_list":
            painter.setPen(QColor(*theme["text_main"]))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(QRect(200, 30, 340, 30), Qt.AlignmentFlag.AlignCenter, "CONFIGS")
            
            self.config_list_rects.clear()
            if APP_SETTINGS["root_dir"] != "NO_SAVE":
                cdir = os.path.join(APP_SETTINGS["root_dir"], "configs")
                if os.path.exists(cdir):
                    files = [f[:-5] for f in os.listdir(cdir) if f.endswith(".json") and f != "session.json"]
                    if not files:
                        painter.setFont(QFont("Arial", 10))
                        painter.setPen(QColor(156, 163, 175))
                        painter.drawText(QRect(200, 100, 420, 30), Qt.AlignmentFlag.AlignCenter, lang["CFG_EMPTY"])
                    else:
                        x_start, y_start = 200, 80
                        w_item, h_item = 130, 45
                        gap = 15
                        col, row = 0, 0
                        for fname in files:
                            rect = QRect(x_start + col*(w_item+gap), y_start + row*(h_item+gap), w_item, h_item)
                            self.config_list_rects.append((rect, fname))
                            hov = (self.hovered_btn == f"cfg_{fname}")
                            painter.setBrush(QColor(*theme["accent"], 40) if hov else QColor(255, 255, 255, 12))
                            painter.setPen(QPen(QColor(*theme["accent"]), 2) if hov else QPen(QColor(*theme["border"]), 1))
                            painter.drawRoundedRect(rect, 6.0, 6.0)
                            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                            painter.setPen(QColor(255, 255, 255) if hov else QColor(*theme["accent"]))
                            painter.drawText(QRect(rect.x(), rect.y() + 10, rect.width(), 15), Qt.AlignmentFlag.AlignCenter, fname)
                            painter.setFont(QFont("Arial", 7))
                            painter.setPen(QColor(156, 163, 175))
                            painter.drawText(QRect(rect.x(), rect.y() + 25, rect.width(), 15), Qt.AlignmentFlag.AlignCenter, lang["CFG_CLICK_LOAD"])
                            col += 1
                            if col > 2: col = 0; row += 1
            else:
                painter.setFont(QFont("Arial", 10))
                painter.setPen(QColor(156, 163, 175))
                painter.drawText(QRect(200, 100, 420, 30), Qt.AlignmentFlag.AlignCenter, lang["NO_SAVE_MODE"])

        elif self.right_pane_mode == "terminal":
            painter.setPen(QColor(*theme["text_main"]))
            painter.setFont(QFont("Consolas", 20, QFont.Weight.ExtraBold))
            painter.drawText(QRect(200, 20, 340, 35), Qt.AlignmentFlag.AlignCenter, "NOTVIO")
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.setPen(QColor(*theme["accent"]))
            painter.drawText(QRect(200, 50, 340, 20), Qt.AlignmentFlag.AlignCenter, "POWERSHELL")

class TelemetryWindow(QWidget):
    def __init__(self, parent_app, stats):
        super().__init__(None)
        self.main_app = parent_app
        self.stats = stats
        
        saved_pos = WINDOW_POSITIONS["telemetry_window"]
        if saved_pos.x() != -1:
            self.setGeometry(saved_pos.x(), saved_pos.y(), 300, 120)
        else:
            self.setGeometry(520, 100, 300, 120)
            
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.window_manager = DragPinWindowHelper(self, name="STATS")
        self._is_closing = False

    def moveEvent(self, event):
        super().moveEvent(event)
        WINDOW_POSITIONS["telemetry_window"] = self.pos()

    def showEvent(self, event):
        super().showEvent(event)
        self.window_manager.resolve_hwnd_and_pin()
        apply_fade_in(self)

    def mousePressEvent(self, event):
        self.window_manager.handle_press(event)

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
        WINDOW_POSITIONS["telemetry_window"] = self.pos()
        save_current_session()
        if not self._is_closing:
            event.ignore()
            self.close_with_fade()
        else:
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[APP_SETTINGS["theme_idx"]]
        
        w = self.width()
        h = self.height()
        painter.setBrush(QColor(*theme["bg"]))
        painter.setPen(QPen(QColor(*theme["border"]), 2))
        painter.drawRoundedRect(5, 5, w - 10, h - 10, 10.0, 10.0)
        font_title = QFont("Arial", 11, QFont.Weight.Bold)

        # Окно очищено от лишних кнопок для минималистичного вида
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
        self.stats = {"cpu": 0.0, "ram": 0.0}
        
        if not APP_SETTINGS["show_player"]: self.setGeometry(-10000, -10000, 1, 1)
        else:
            if WINDOW_POSITIONS["media_window"].x() != -1: self.setGeometry(WINDOW_POSITIONS["media_window"].x(), WINDOW_POSITIONS["media_window"].y(), 400, 400)
            else: self.setGeometry(100, 100, 400, 400)
                
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.file_path = APP_SETTINGS["last_media_path"]
        self._is_closing = False

        self.container = QStackedWidget(self)
        self.gif_label = QLabel(); self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True); self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.scene = QGraphicsScene(self); self.graphics_view = QGraphicsView(self.scene, self)
        self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True); self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.graphics_view.setStyleSheet("background: transparent; border: none;"); self.graphics_view.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.video_item = QGraphicsVideoItem(); self.scene.addItem(self.video_item)
        self.container.addWidget(self.gif_label); self.container.addWidget(self.graphics_view)

        self.video_player = QMediaPlayer(); self.video_audio_output = QAudioOutput()
        self.video_player.setAudioOutput(self.video_audio_output); self.video_player.setVideoOutput(self.video_item); self.video_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.companion_audio_player = QMediaPlayer(); self.companion_audio_output = QAudioOutput()
        self.companion_audio_player.setAudioOutput(self.companion_audio_output); self.companion_audio_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.video_audio_output.setVolume(0.7); self.companion_audio_output.setVolume(0.7)
        self.gif_movie = None
        self.window_manager = DragPinWindowHelper(self, name="MEDIA")

        self.worker = TelemetryWorker()
        self.worker.stats_updated.connect(self.update_stats)
        self.worker.start()

        self.telemetry_window = TelemetryWindow(self, self.stats)
        if APP_SETTINGS["show_telemetry"]: self.telemetry_window.show()
        if self.file_path and os.path.exists(self.file_path): self.autoplay_last_media(self.file_path)

    def moveEvent(self, event):
        super().moveEvent(event)
        if APP_SETTINGS["show_player"]: WINDOW_POSITIONS["media_window"] = self.pos()

    def update_stats(self, data):
        self.stats.update(data)
        self.telemetry_window.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.window_manager.resolve_hwnd_and_pin()
        if APP_SETTINGS["show_player"]: apply_fade_in(self)

    def resizeEvent(self, event):
        if self.width() < 50 or self.height() < 50: return
        self.container.setGeometry(10, 10, self.width() - 20, self.height() - 20)
        self.graphics_view.setGeometry(self.container.rect())
        self.video_item.setSize(QSizeF(self.graphics_view.size()))
        if self.gif_movie: self.gif_movie.setScaledSize(self.container.size())

    def mousePressEvent(self, event):
        if APP_SETTINGS["show_player"]: self.window_manager.handle_press(event)

    def mouseMoveEvent(self, event):
        if APP_SETTINGS["show_player"]: self.window_manager.handle_move(event); self.update()

    def mouseReleaseEvent(self, event):
        if APP_SETTINGS["show_player"]: self.window_manager.handle_release(event); self.update()

    def mouseDoubleClickEvent(self, event):
        if APP_SETTINGS["show_player"] and event.button() == Qt.MouseButton.LeftButton: self.load_file_dialog()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.return_to_start_menu()
        elif event.key() == Qt.Key.Key_Space: self.toggle_pause()

    def toggle_pause(self):
        if not self.file_path: return
        if self.file_path.lower().endswith('.gif') and self.gif_movie:
            if self.gif_movie.state() == QMovie.MovieState.Running: self.gif_movie.setPaused(True); self.companion_audio_player.pause()
            else: self.gif_movie.setPaused(False); self.companion_audio_player.play()
        else:
            if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState: self.video_player.pause(); self.companion_audio_player.pause()
            else: self.video_player.play(); self.companion_audio_player.play()

    def return_to_start_menu(self):
        self.stop_all_playback()
        if self.worker: self.worker.stop()
        if self.telemetry_window: self.telemetry_window.close_with_fade()
        def fin():
            if self.worker: self.worker.wait()
            self.close()
            global start_menu
            start_menu = StartMenuWindow(); start_menu.show()
        if not APP_SETTINGS["show_player"]: fin()
        else: apply_fade_out(self, duration=300, on_finished_callback=fin)

    def load_file_dialog(self):
        lang = TRANSLATIONS[APP_SETTINGS["lang"]]
        path, _ = QFileDialog.getOpenFileName(self, lang["OPEN_MEDIA"], "", "Media (*.mp4 *.gif *.avi *.mov *.mkv *.mp3 *.wav)")
        if path:
            self.file_path = path; APP_SETTINGS["last_media_path"] = path; save_current_session()
            self.autoplay_last_media(path)

    def autoplay_last_media(self, path):
        self.stop_all_playback()
        comp = find_companion_audio(path)
        if path.lower().endswith('.gif'):
            self.container.setCurrentIndex(0)
            self.gif_movie = QMovie(path)
            self.gif_movie.setCacheMode(QMovie.CacheMode.CacheAll if APP_SETTINGS["priority_mode"] == "MEM" else QMovie.CacheMode.CacheNone)
            self.gif_movie.setScaledSize(self.container.size()); self.gif_label.setMovie(self.gif_movie); self.gif_movie.start()
            if comp: self.companion_audio_player.setSource(QUrl.fromLocalFile(comp)); self.companion_audio_player.play()
        else:
            self.container.setCurrentIndex(1)
            self.video_player.setSource(QUrl.fromLocalFile(path))
            if comp: self.video_audio_output.setMuted(True); self.companion_audio_player.setSource(QUrl.fromLocalFile(comp)); self.companion_audio_player.play()
            else: self.video_audio_output.setMuted(False)
            self.video_player.play()

    def stop_all_playback(self):
        self.video_player.stop(); self.video_player.setSource(QUrl())
        self.companion_audio_player.stop(); self.companion_audio_player.setSource(QUrl())
        if self.gif_movie: self.gif_movie.stop(); self.gif_label.setMovie(None); self.gif_movie.deleteLater(); self.gif_movie = None
        gc.collect()

    def paintEvent(self, event):
        if not APP_SETTINGS["show_player"]: return
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        theme = THEMES[APP_SETTINGS["theme_idx"]]; lang = TRANSLATIONS[APP_SETTINGS["lang"]]
        if not self.file_path:
            painter.setBrush(QColor(*theme["bg"])); painter.setPen(QPen(QColor(*theme["border"]), 2))
            painter.drawRoundedRect(10, 10, self.width() - 20, self.height() - 20, 10.0, 10.0)
            cx, cy = self.width() // 2, self.height() // 2
            painter.setBrush(QColor(*theme["accent"])); painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(cx - 25, cy - 35, 50, 30); painter.drawPolygon(QPoint(cx - 25, cy - 35), QPoint(cx, cy - 50), QPoint(cx + 25, cy - 35))
            painter.setPen(QColor(255, 255, 255, 240)); painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(QRect(10, cy + 15, self.width() - 20, 25), int(Qt.AlignmentFlag.AlignCenter), lang["DBL_CLICK"])
            painter.setPen(QColor(156, 163, 175, 200)); painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(QRect(10, cy + 40, self.width() - 20, 20), int(Qt.AlignmentFlag.AlignCenter), lang["R_CLICK"])
        if time.time() < self.window_manager.feedback_expiry: self.window_manager.draw_feedback_if_active(painter, self.width(), self.height(), theme)

    def closeEvent(self, event):
        WINDOW_POSITIONS["media_window"] = self.pos()
        save_current_session()
        if not self._is_closing:
            event.ignore()
            self._is_closing = True
            self.stop_all_playback()
            if self.worker: self.worker.stop()
            if self.telemetry_window: self.telemetry_window.close_with_fade()
            def fin():
                if self.worker: self.worker.wait()
                self.close()
            if not APP_SETTINGS["show_player"]: fin()
            else: apply_fade_out(self, duration=300, on_finished_callback=fin)
        else: event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if check_existing_install():
        apply_priority_mode(APP_SETTINGS["priority_mode"])
        start_menu = StartMenuWindow()
        start_menu.show()
    else:
        apply_priority_mode(APP_SETTINGS["priority_mode"])
        disk_dialog = DiskSelectionDialog()
        disk_dialog.show()
    sys.exit(app.exec())