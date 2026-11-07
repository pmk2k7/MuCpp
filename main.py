import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QApplication

from icons import get_app_icon
from ide import MuCppMainWindow, DevCppMainWindow


def apply_mucpp_theme(app: QApplication):
    """Sets a modern, clean, attractive styling for MuCpp."""
    app.setStyle("Fusion")

    # High quality modern UI font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Modern Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F8FAFC"))
    palette.setColor(QPalette.WindowText, QColor("#0F172A"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase, QColor("#F1F5F9"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1E293B"))
    palette.setColor(QPalette.ToolTipText, QColor("#F8FAFC"))
    palette.setColor(QPalette.Text, QColor("#0F172A"))
    palette.setColor(QPalette.Button, QColor("#F1F5F9"))
    palette.setColor(QPalette.ButtonText, QColor("#0F172A"))
    palette.setColor(QPalette.Highlight, QColor("#2563EB"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    # Polished modern stylesheet for toolbars, buttons, tabs, splitters
    app.setStyleSheet("""
        QMainWindow {
            background-color: #F8FAFC;
        }
        QToolBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            padding: 4px 6px;
            spacing: 3px;
        }
        QToolBar::separator {
            width: 1px;
            background-color: #CBD5E1;
            margin: 3px 6px;
        }
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 5px;
            padding: 4px 6px;
            font-size: 11px;
            font-weight: 500;
            color: #1E293B;
        }
        QToolButton:hover {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
        }
        QToolButton:pressed {
            background-color: #DBEAFE;
            border: 1px solid #93C5FD;
        }
        QToolButton:disabled {
            opacity: 0.35;
        }
        QTabBar::tab {
            background-color: #F1F5F9;
            color: #475569;
            border: 1px solid #E2E8F0;
            padding: 6px 14px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
            font-size: 11px;
        }
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #1E293B;
            border-bottom-color: #FFFFFF;
            font-weight: 600;
        }
        QTabBar::tab:hover:!selected {
            background-color: #E2E8F0;
            color: #0F172A;
        }
        QStatusBar {
            background-color: #F8FAFC;
            border-top: 1px solid #E2E8F0;
            color: #475569;
            font-size: 11px;
        }
        QSplitter::handle {
            background-color: #E2E8F0;
        }
        QSplitter::handle:hover {
            background-color: #3B82F6;
        }
        QHeaderView::section {
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 600;
            padding: 5px;
            border: 1px solid #E2E8F0;
        }
        QMenuBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            font-size: 12px;
        }
        QMenuBar::item {
            padding: 4px 8px;
            background: transparent;
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: #EFF6FF;
            color: #1E40AF;
        }
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            padding: 4px;
            border-radius: 6px;
        }
        QMenu::item {
            padding: 5px 24px 5px 28px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #2563EB;
            color: #FFFFFF;
        }
        QMenu::separator {
            height: 1px;
            background: #E2E8F0;
            margin: 4px 6px;
        }
    """)


# Backwards compatibility
apply_devcpp_theme = apply_mucpp_theme


def main():
    # Enable High DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("MuCpp")
    app.setApplicationDisplayName("MuCpp")
    app.setWindowIcon(get_app_icon())

    apply_mucpp_theme(app)

    window = MuCppMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
