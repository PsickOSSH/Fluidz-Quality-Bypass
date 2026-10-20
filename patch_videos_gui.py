# ==============================================================================
# Fluidz Quality Bypass
# ==============================================================================

import sys
import os
import subprocess
import ctypes

if sys.platform == 'win32':
    myappid = 'fluidz.quality.bypass'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QStatusBar, QToolBar,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu, QAbstractItemView,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QDesktopServices, QFont, QIcon
from PyQt5.QtCore import Qt, QUrl, QSize, QThreadPool, QRunnable, pyqtSignal, QObject, QSettings

from pathlib import Path


def outil_video(nom):
    return str(Path(__file__).resolve().parent / nom)


def resource_path(nom):
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nom)


icon_path = resource_path('icon.ico')
FFMPEG_EXE = outil_video("ffmpeg.exe")
FFPROBE_EXE = outil_video("ffprobe.exe")

# ------------------------------------------------------------------------------
# 1. GLOBAL STYLES — light theme, dark theme, valorant theme
# ------------------------------------------------------------------------------
LIGHT_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #f5f6f8;
}
QWidget {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #1f2430;
}
QFrame#sidePanel {
    background-color: #ffffff;
    border-right: 1px solid #e2e5eb;
}
QFrame#headerBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e5eb;
}
QLabel#appTitle { font-size: 16px; font-weight: 600; color: #12141a; }
QLabel#appSubtitle { font-size: 11px; color: #7a7f8c; }
QLabel#sectionLabel {
    font-size: 11px; font-weight: 600; color: #7a7f8c;
    letter-spacing: 0.5px; text-transform: uppercase;
}
QLabel#hintLabel { color: #9aa0ab; font-size: 11px; }

QPushButton#primaryBtn {
    background-color: #1f2430; color: #ffffff; font-weight: 600;
    font-size: 13px; border-radius: 4px; padding: 10px 16px; border: none;
}
QPushButton#primaryBtn:hover { background-color: #33394a; }
QPushButton#primaryBtn:pressed { background-color: #12141a; }
QPushButton#primaryBtn:disabled { background-color: #c7cad1; color: #f0f1f3; }

QPushButton#secondaryBtn {
    background-color: #ffffff; color: #1f2430; font-weight: 500;
    border: 1px solid #d3d7de; border-radius: 4px; padding: 7px 14px;
}
QPushButton#secondaryBtn:hover { background-color: #eef0f3; }
QPushButton#secondaryBtn:disabled { color: #b3b7c0; border-color: #e2e5eb; }

QLineEdit {
    background-color: #ffffff; color: #1f2430;
    border: 1px solid #d3d7de; border-radius: 4px; padding: 6px 10px;
}
QLineEdit:focus { border: 1px solid #1f2430; }
QLineEdit:read-only { background-color: #f0f1f3; color: #5b606b; }

QTableWidget {
    background-color: #ffffff; alternate-background-color: #fafbfc;
    border: 1px solid #e2e5eb; border-radius: 4px; gridline-color: #eceef1;
    color: #1f2430; selection-background-color: #e7eaf0; selection-color: #1f2430;
}
QHeaderView::section {
    background-color: #f5f6f8; color: #5b606b; font-weight: 600;
    font-size: 11px; padding: 8px; border: none; border-bottom: 1px solid #e2e5eb;
}
QStatusBar { background-color: #ffffff; color: #5b606b; border-top: 1px solid #e2e5eb; }
QProgressBar {
    border: 1px solid #d3d7de; border-radius: 3px; text-align: center;
    background: #f0f1f3; color: #1f2430; font-size: 11px;
}
QProgressBar::chunk { background-color: #1f2430; border-radius: 2px; }

QMenu { background-color: #ffffff; border: 1px solid #e2e5eb; color: #1f2430; }
QMenu::item:selected { background-color: #eef0f3; }

QToolBar { background-color: #ffffff; border-bottom: 1px solid #e2e5eb; spacing: 4px; padding: 4px; }
QMenuBar { background-color: #ffffff; border-bottom: 1px solid #e2e5eb; color: #1f2430; }
QMenuBar::item:selected { background-color: #eef0f3; }
"""

DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #14151a;
}
QWidget {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #e4e6eb;
}
QFrame#sidePanel {
    background-color: #1b1c22;
    border-right: 1px solid #2a2c34;
}
QFrame#headerBar {
    background-color: #1b1c22;
    border-bottom: 1px solid #2a2c34;
}
QLabel#appTitle { font-size: 16px; font-weight: 600; color: #f5f6f8; }
QLabel#appSubtitle { font-size: 11px; color: #8b8f9c; }
QLabel#sectionLabel {
    font-size: 11px; font-weight: 600; color: #8b8f9c;
    letter-spacing: 0.5px; text-transform: uppercase;
}
QLabel#hintLabel { color: #6b6f7c; font-size: 11px; }

QPushButton#primaryBtn {
    background-color: #e4e6eb; color: #14151a; font-weight: 600;
    font-size: 13px; border-radius: 4px; padding: 10px 16px; border: none;
}
QPushButton#primaryBtn:hover { background-color: #ffffff; }
QPushButton#primaryBtn:pressed { background-color: #c7cad1; }
QPushButton#primaryBtn:disabled { background-color: #3a3c46; color: #6b6f7c; }

QPushButton#secondaryBtn {
    background-color: #1f2027; color: #e4e6eb; font-weight: 500;
    border: 1px solid #33353f; border-radius: 4px; padding: 7px 14px;
}
QPushButton#secondaryBtn:hover { background-color: #292b34; }
QPushButton#secondaryBtn:disabled { color: #5a5d68; border-color: #2a2c34; }

QLineEdit {
    background-color: #1f2027; color: #e4e6eb;
    border: 1px solid #33353f; border-radius: 4px; padding: 6px 10px;
}
QLineEdit:focus { border: 1px solid #8b8f9c; }
QLineEdit:read-only { background-color: #191a20; color: #8b8f9c; }

QTableWidget {
    background-color: #1b1c22; alternate-background-color: #1f2027;
    border: 1px solid #2a2c34; border-radius: 4px; gridline-color: #2a2c34;
    color: #e4e6eb; selection-background-color: #33353f; selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #14151a; color: #8b8f9c; font-weight: 600;
    font-size: 11px; padding: 8px; border: none; border-bottom: 1px solid #2a2c34;
}
QStatusBar { background-color: #1b1c22; color: #8b8f9c; border-top: 1px solid #2a2c34; }
QProgressBar {
    border: 1px solid #33353f; border-radius: 3px; text-align: center;
    background: #191a20; color: #e4e6eb; font-size: 11px;
}
QProgressBar::chunk { background-color: #e4e6eb; border-radius: 2px; }

QMenu { background-color: #1b1c22; border: 1px solid #2a2c34; color: #e4e6eb; }
QMenu::item:selected { background-color: #292b34; }

QToolBar { background-color: #1b1c22; border-bottom: 1px solid #2a2c34; spacing: 4px; padding: 4px; }
QMenuBar { background-color: #1b1c22; border-bottom: 1px solid #2a2c34; color: #e4e6eb; }
QMenuBar::item:selected { background-color: #292b34; }
"""

# Theme inspired by VALORANT's official brand palette:
# signature red #FF4655, ink navy #0F1923, off-white #ECE8E1 (Riot brand kit).
VALORANT_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #0F1923;
}
QWidget {
    font-family: 'Din Condensed', 'Segoe UI Semibold', 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #ECE8E1;
}
QFrame#sidePanel {
    background-color: #14202C;
    border-right: 1px solid #FF4655;
}
QFrame#headerBar {
    background-color: #14202C;
    border-bottom: 2px solid #FF4655;
}
QLabel#appTitle { font-size: 17px; font-weight: 700; color: #ECE8E1; letter-spacing: 1px; text-transform: uppercase; }
QLabel#appSubtitle { font-size: 11px; color: #FF4655; font-weight: 600; letter-spacing: 0.5px; }
QLabel#sectionLabel {
    font-size: 11px; font-weight: 700; color: #FF4655;
    letter-spacing: 1px; text-transform: uppercase;
}
QLabel#hintLabel { color: #6B7A88; font-size: 11px; }

QPushButton#primaryBtn {
    background-color: #FF4655; color: #0F1923; font-weight: 700;
    font-size: 13px; border-radius: 0px; padding: 10px 16px; border: none;
    text-transform: uppercase; letter-spacing: 0.5px;
}
QPushButton#primaryBtn:hover { background-color: #FF6673; }
QPushButton#primaryBtn:pressed { background-color: #C93544; }
QPushButton#primaryBtn:disabled { background-color: #3A2B2E; color: #6B7A88; }

QPushButton#secondaryBtn {
    background-color: #14202C; color: #ECE8E1; font-weight: 600;
    border: 1px solid #FF4655; border-radius: 0px; padding: 7px 14px;
    text-transform: uppercase; letter-spacing: 0.5px;
}
QPushButton#secondaryBtn:hover { background-color: #1F2E3B; }
QPushButton#secondaryBtn:disabled { color: #4B5966; border-color: #3A4652; }

QLineEdit {
    background-color: #14202C; color: #ECE8E1;
    border: 1px solid #2A3945; border-radius: 0px; padding: 6px 10px;
}
QLineEdit:focus { border: 1px solid #FF4655; }
QLineEdit:read-only { background-color: #0F1923; color: #6B7A88; }

QTableWidget {
    background-color: #14202C; alternate-background-color: #182634;
    border: 1px solid #2A3945; border-radius: 0px; gridline-color: #2A3945;
    color: #ECE8E1; selection-background-color: #FF4655; selection-color: #0F1923;
}
QHeaderView::section {
    background-color: #0F1923; color: #FF4655; font-weight: 700;
    font-size: 11px; padding: 8px; border: none; border-bottom: 2px solid #FF4655;
    text-transform: uppercase; letter-spacing: 0.5px;
}
QStatusBar { background-color: #14202C; color: #ECE8E1; border-top: 1px solid #FF4655; }
QProgressBar {
    border: 1px solid #2A3945; border-radius: 0px; text-align: center;
    background: #0F1923; color: #ECE8E1; font-size: 11px;
}
QProgressBar::chunk { background-color: #FF4655; border-radius: 0px; }

QMenu { background-color: #14202C; border: 1px solid #FF4655; color: #ECE8E1; }
QMenu::item:selected { background-color: #FF4655; color: #0F1923; }

QToolBar { background-color: #14202C; border-bottom: 1px solid #FF4655; spacing: 4px; padding: 4px; }
QMenuBar { background-color: #14202C; border-bottom: 1px solid #FF4655; color: #ECE8E1; }
QMenuBar::item:selected { background-color: #FF4655; color: #0F1923; }
"""

THEMES = {'dark': DARK_THEME_QSS, 'light': LIGHT_THEME_QSS, 'valorant': VALORANT_THEME_QSS}
THEME_ORDER = ['dark', 'light', 'valorant']
THEME_LABELS = {'dark': 'Dark mode', 'light': 'Light mode', 'valorant': 'Valorant mode'}

ORG_NAME = 'Fluidz'
APP_NAME = 'QualityBypass'
SETTINGS_THEME_KEY = 'appearance/theme'


def detect_system_theme():
    """
    Best-effort detection of the OS light/dark preference.
    Falls back to 'dark' if nothing can be determined.
    Only ever returns 'light' or 'dark' — the OS has no concept of the
    custom 'valorant' theme, that one only ever comes from a saved
    user preference.
    """
    # Windows: read the "AppsUseLightTheme" registry flag.
    if sys.platform == 'win32':
        try:
            import winreg
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return 'light' if value == 1 else 'dark'
        except Exception:
            pass

    # macOS: check the AppleInterfaceStyle default.
    if sys.platform == 'darwin':
        try:
            res = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return 'dark' if 'Dark' in res.stdout else 'light'
        except Exception:
            pass

    # Linux / fallback: estimate from the default palette's window lightness.
    try:
        app = QApplication.instance()
        if app is not None:
            bg = app.palette().window().color()
            luminance = 0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()
            return 'light' if luminance > 128 else 'dark'
    except Exception:
        pass

    return 'dark'


# ------------------------------------------------------------------------------
# 2. Background FFmpeg processing
# ------------------------------------------------------------------------------
class WorkerSignals(QObject):
    finished = pyqtSignal(int, bool, str)


class PatchWorker(QRunnable):
    def __init__(self, row, inp, scale, ffmpeg_path, out):
        super().__init__()
        self.row = row
        self.inp = inp
        self.scale = scale
        self.ffmpeg_path = ffmpeg_path
        self.out = out
        self.signals = WorkerSignals()

    def run(self):
        cmd = [self.ffmpeg_path, '-y']
        if self.scale is not None and str(self.scale).strip():
            cmd.extend(['-itsscale', str(self.scale)])
        cmd.extend(['-i', self.inp, '-c:v', 'copy', '-c:a', 'copy', self.out])

        try:
            res = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.signals.finished.emit(self.row, True, res.stderr)
        except subprocess.CalledProcessError as e:
            self.signals.finished.emit(self.row, False, e.stderr)


# ------------------------------------------------------------------------------
# 3. SETTINGS WINDOW
# ------------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None, ffmpeg_path=None, ffprobe_path=None, manual_scale=''):
        super().__init__(parent)
        self.setWindowTitle('Preferences')
        self.resize(460, 190)
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.ffmpeg_input = QLineEdit(ffmpeg_path or FFMPEG_EXE)
        btn_ff = QPushButton('Browse')
        btn_ff.setObjectName('secondaryBtn')
        btn_ff.clicked.connect(self.browse_ffmpeg)
        h1 = QHBoxLayout()
        h1.addWidget(self.ffmpeg_input)
        h1.addWidget(btn_ff)
        layout.addRow('FFmpeg executable', h1)

        self.ffprobe_input = QLineEdit(ffprobe_path or FFPROBE_EXE)
        btn_fp = QPushButton('Browse')
        btn_fp.setObjectName('secondaryBtn')
        btn_fp.clicked.connect(self.browse_ffprobe)
        h2 = QHBoxLayout()
        h2.addWidget(self.ffprobe_input)
        h2.addWidget(btn_fp)
        layout.addRow('FFprobe executable', h2)

        self.manual_input = QLineEdit(manual_scale)
        self.manual_input.setPlaceholderText('Auto (leave blank)')
        layout.addRow('Manual itsscale', self.manual_input)

        h3 = QHBoxLayout()
        ok = QPushButton('Save')
        ok.setObjectName('primaryBtn')
        cancel = QPushButton('Cancel')
        cancel.setObjectName('secondaryBtn')
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        h3.addStretch()
        h3.addWidget(cancel)
        h3.addWidget(ok)
        layout.addRow(h3)

    def browse_ffmpeg(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Locate ffmpeg', '', 'Executable (*.exe);;All Files (*)')
        if p:
            self.ffmpeg_input.setText(p)

    def browse_ffprobe(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Locate ffprobe', '', 'Executable (*.exe);;All Files (*)')
        if p:
            self.ffprobe_input.setText(p)


# ------------------------------------------------------------------------------
# 4. MAIN WINDOW
# ------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fluidz Quality Bypass')
        self.setWindowIcon(QIcon(icon_path))
        self.resize(1080, 620)
        self.setMinimumSize(860, 520)

        self.ffmpeg_path = FFMPEG_EXE
        self.ffprobe_path = FFPROBE_EXE
        self.output_dir = os.getcwd()
        self.manual_scale = ''
        self.threadpool = QThreadPool()
        self.output_files = {}

        # Persistent settings store (registry on Windows, plist on macOS,
        # ini file on Linux — handled transparently by QSettings).
        self.settings = QSettings(ORG_NAME, APP_NAME)

        saved_theme = self.settings.value(SETTINGS_THEME_KEY, None)
        if saved_theme in THEMES:
            self.current_theme = saved_theme
        else:
            # No saved preference yet: align with the OS light/dark setting.
            self.current_theme = detect_system_theme()

        self._create_actions()
        self._create_menus()
        self._create_central()
        self._create_statusbar()
        self.setAcceptDrops(True)

        self.apply_theme(self.current_theme, persist=False)

    # ---------------- Actions / Menus ----------------
    def _create_actions(self):
        self.action_remove = QAction('Remove selected', self)
        self.action_remove.setShortcut('Del')
        self.action_remove.triggered.connect(self.remove_selected)

        self.action_clear = QAction('Clear list', self)
        self.action_clear.triggered.connect(self.clear_all)

        self.action_settings = QAction('Preferences…', self)
        self.action_settings.triggered.connect(self.open_settings)

        self.action_toggle_theme = QAction('Cycle theme (dark / light / valorant)', self)
        self.action_toggle_theme.setShortcut('Ctrl+T')
        self.action_toggle_theme.triggered.connect(self.toggle_theme)

        self.action_about = QAction('About', self)
        self.action_about.triggered.connect(self.show_about)

        self.action_exit = QAction('Quit', self)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.triggered.connect(self.close)

    def _create_menus(self):
        mb = self.menuBar()
        fm = mb.addMenu('File')
        fm.addAction(self.action_remove)
        fm.addAction(self.action_clear)
        fm.addSeparator()
        fm.addAction(self.action_exit)

        em = mb.addMenu('Edit')
        em.addAction(self.action_settings)

        vm = mb.addMenu('View')
        vm.addAction(self.action_toggle_theme)

        mb.addMenu('Help').addAction(self.action_about)

    # ---------------- Central layout ----------------
    def _create_central(self):
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header.setObjectName('headerBar')
        header.setFixedHeight(56)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 8, 24, 8)
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel('Fluidz Quality Bypass')
        title.setObjectName('appTitle')
        subtitle = QLabel('Frame-rate correction batch tool')
        subtitle.setObjectName('appSubtitle')
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        hl.addLayout(title_box)
        hl.addStretch()

        self.btn_theme = QPushButton('Light mode')
        self.btn_theme.setObjectName('secondaryBtn')
        self.btn_theme.clicked.connect(self.toggle_theme)
        hl.addWidget(self.btn_theme)

        btn_settings = QPushButton('Preferences')
        btn_settings.setObjectName('secondaryBtn')
        btn_settings.clicked.connect(self.open_settings)
        hl.addWidget(btn_settings)
        outer.addWidget(header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        side = QFrame()
        side.setObjectName('sidePanel')
        side.setFixedWidth(260)
        sv = QVBoxLayout(side)
        sv.setContentsMargins(20, 24, 20, 24)
        sv.setSpacing(10)

        lbl_source = QLabel('SOURCE')
        lbl_source.setObjectName('sectionLabel')
        sv.addWidget(lbl_source)

        self.btn_add = QPushButton('Add videos…')
        self.btn_add.setObjectName('primaryBtn')
        self.btn_add.setFixedHeight(42)
        self.btn_add.clicked.connect(self.add_videos)
        sv.addWidget(self.btn_add)

        drop_hint = QLabel('Or drag and drop files here')
        drop_hint.setObjectName('hintLabel')
        drop_hint.setWordWrap(True)
        sv.addWidget(drop_hint)

        sv.addSpacing(16)
        lbl_dest = QLabel('DESTINATION')
        lbl_dest.setObjectName('sectionLabel')
        sv.addWidget(lbl_dest)

        self.output_display = QLineEdit(self.output_dir)
        self.output_display.setReadOnly(True)
        sv.addWidget(self.output_display)

        btn_out = QPushButton('Change folder')
        btn_out.setObjectName('secondaryBtn')
        btn_out.clicked.connect(self.choose_export_folder)
        sv.addWidget(btn_out)

        sv.addStretch()

        self.btn_patch = QPushButton('Patch now')
        self.btn_patch.setObjectName('primaryBtn')
        self.btn_patch.setFixedHeight(46)
        self.btn_patch.setEnabled(False)
        self.btn_patch.clicked.connect(self.patch_all)
        sv.addWidget(self.btn_patch)

        body.addWidget(side)

        main_area = QWidget()
        mv = QVBoxLayout(main_area)
        mv.setContentsMargins(24, 24, 24, 24)
        mv.setSpacing(12)

        row_top = QHBoxLayout()
        lbl_queue = QLabel('QUEUE')
        lbl_queue.setObjectName('sectionLabel')
        row_top.addWidget(lbl_queue)
        row_top.addStretch()
        btn_remove = QPushButton('Remove')
        btn_remove.setObjectName('secondaryBtn')
        btn_remove.clicked.connect(self.remove_selected)
        btn_clear = QPushButton('Clear all')
        btn_clear.setObjectName('secondaryBtn')
        btn_clear.clicked.connect(self.clear_all)
        row_top.addWidget(btn_remove)
        row_top.addWidget(btn_clear)
        mv.addLayout(row_top)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['File', 'FPS', 'Status'])
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(lambda r, c: self.open_patched(r))
        mv.addWidget(self.table)

        body.addWidget(main_area)
        outer.addLayout(body)

        self.setCentralWidget(root)

    def _create_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.overall_progress = QProgressBar()
        self.overall_progress.setFixedHeight(16)
        self.overall_progress.setFixedWidth(200)
        self.overall_progress.setVisible(False)
        sb.addPermanentWidget(self.overall_progress)

    # ---------------- Theme management ----------------
    def apply_theme(self, name, persist=True):
        self.current_theme = name
        app = QApplication.instance()
        app.setStyleSheet(THEMES[name])
        if hasattr(self, 'btn_theme'):
            next_name = THEME_ORDER[(THEME_ORDER.index(name) + 1) % len(THEME_ORDER)]
            self.btn_theme.setText(THEME_LABELS[next_name])

        if persist:
            self.settings.setValue(SETTINGS_THEME_KEY, name)
            self.settings.sync()

    def toggle_theme(self):
        idx = THEME_ORDER.index(self.current_theme)
        new_theme = THEME_ORDER[(idx + 1) % len(THEME_ORDER)]
        self.apply_theme(new_theme)

    # ----------------- Business logic -----------------
    def choose_export_folder(self):
        f = QFileDialog.getExistingDirectory(self, 'Select export folder', self.output_dir)
        if f:
            self.output_dir = f
            self.output_display.setText(f)

    def add_videos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 'Select videos', '', 'Video Files (*.mp4 *.mov *.mkv *.avi)'
        )
        for f in files:
            self._add_row(f)
        self._update_actions()

    def _add_row(self, p):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(p))

        fps = self.probe_fps(p)
        fps_text = f"{fps:.2f}" if fps is not None else "Unknown"
        self.table.setItem(r, 1, QTableWidgetItem(fps_text))
        self.table.setItem(r, 2, QTableWidgetItem('Ready'))

    def remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)
        self._update_actions()

    def clear_all(self):
        self.table.setRowCount(0)
        self.output_files.clear()
        self._update_actions()

    def patch_all(self):
        rows = self.table.rowCount()
        if rows == 0:
            return

        self.overall_progress.setMaximum(rows)
        self.overall_progress.setValue(0)
        self.overall_progress.setVisible(True)

        for i in range(rows):
            inp = self.table.item(i, 0).text()
            base, ext = os.path.splitext(os.path.basename(inp))

            scale = None
            if self.manual_scale.strip():
                try:
                    scale = float(self.manual_scale)
                except ValueError:
                    scale = None
            else:
                try:
                    fps = float(self.table.item(i, 1).text())
                    if abs(fps - 60) < 0.5:
                        scale = 2
                    elif abs(fps - 90) < 1:
                        scale = 3
                    elif fps > 90:
                        scale = 4
                    else:
                        scale = 1
                except (ValueError, AttributeError):
                    scale = 1

            prefix = f'{base}_patched'
            out = os.path.join(self.output_dir, prefix + ext)
            cnt = 1
            while os.path.exists(out):
                out = os.path.join(self.output_dir, f'{prefix}_{cnt}{ext}')
                cnt += 1

            self.output_files[i] = out
            self.table.setItem(i, 2, QTableWidgetItem('Queued'))

            worker = PatchWorker(i, inp, scale, self.ffmpeg_path, out)
            worker.signals.finished.connect(self._on_done)
            self.threadpool.start(worker)

        self.btn_patch.setEnabled(False)

    def show_context_menu(self, pos):
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return
        m = QMenu()
        m.addAction('Open video', lambda: self.open_patched(idx.row()))
        m.addAction(self.action_remove)
        m.exec_(self.table.viewport().mapToGlobal(pos))

    def open_settings(self):
        dlg = SettingsDialog(self, self.ffmpeg_path, self.ffprobe_path, self.manual_scale)
        if dlg.exec_() == QDialog.Accepted:
            self.ffmpeg_path = dlg.ffmpeg_input.text()
            self.ffprobe_path = dlg.ffprobe_input.text()
            self.manual_scale = dlg.manual_input.text()

    def show_about(self):
        QMessageBox.about(self, 'About', 'Fluidz Quality Bypass\\nVersion 2.0.0')

    def open_patched(self, row):
        p = self.output_files.get(row)
        if not p or not os.path.exists(p):
            p = self.table.item(row, 0).text()
        if p and os.path.exists(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        valid_exts = ('.mp4', '.mov', '.mkv', '.avi')
        for u in e.mimeData().urls():
            if u.isLocalFile():
                path = u.toLocalFile()
                if path.lower().endswith(valid_exts):
                    self._add_row(path)
        self._update_actions()

    def probe_fps(self, path):
        try:
            res = subprocess.run([
                FFPROBE_EXE, '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            rate = res.stdout.strip()
            if '/' in rate:
                n, d = rate.split('/')
                return float(n) / float(d)
            return float(rate)
        except Exception:
            return None

    def _on_done(self, row, ok, log):
        status = 'Done' if ok else 'Failed'
        self.table.setItem(row, 2, QTableWidgetItem(status))
        if not ok:
            QMessageBox.critical(self, 'Error', f'Failed on row {row}:\\n{log}')

        val = self.overall_progress.value() + 1
        self.overall_progress.setValue(val)
        if val >= self.overall_progress.maximum():
            self.overall_progress.setVisible(False)
            self.statusBar().showMessage('All conversions completed', 4000)

        self._update_actions()

    def _update_actions(self):
        has = self.table.rowCount() > 0
        self.btn_add.setEnabled(True)
        self.btn_patch.setEnabled(has)
        self.action_remove.setEnabled(has)
        self.action_clear.setEnabled(has)


# ------------------------------------------------------------------------------
# 5. ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)

    icon = QIcon(icon_path)
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)

    app.processEvents()
    window.show()

    sys.exit(app.exec_())
