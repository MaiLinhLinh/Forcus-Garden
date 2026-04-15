import sys
from database.db_config import init_db
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# ── Design tokens ─────────────────────────────────────────────────────
GLOBAL_STYLESHEET = """
/* ================================================================
   FOCUS GARDEN — GLOBAL DARK-NATURE THEME
   Design tokens:
     bg-base:    #1a1f2e     (dark navy)
     bg-card:    #232a3e     (dark slate)
     bg-input:   #2a3149     (input background)
     accent:     #4ade80     (fresh green)
     accent-dim: #22c55e     (medium green)
     text-1:     #e2e8f0     (primary text)
     text-2:     #94a3b8     (secondary text)
     danger:     #ef4444     (red)
     warning:    #f59e0b     (amber)
   ================================================================ */

/* ── Base reset ─────────────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QMainWindow, QDialog {
    background-color: #1a1f2e;
}

QWidget {
    color: #e2e8f0;
}

/* ── Tab Widget ─────────────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #1a1f2e;
}

QTabBar {
    background-color: #151929;
}

QTabBar::tab {
    background-color: #1e2538;
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    padding: 14px 28px;
    margin-right: 2px;
    border: none;
    border-bottom: 3px solid transparent;
}

QTabBar::tab:selected {
    background-color: #232a3e;
    color: #4ade80;
    border-bottom: 3px solid #4ade80;
}

QTabBar::tab:hover:!selected {
    background-color: #252d42;
    color: #cbd5e1;
}

/* ── Inputs ─────────────────────────────────────────────────────── */
QLineEdit, QSpinBox {
    background-color: #2a3149;
    color: #e2e8f0;
    border: 1px solid rgba(74, 222, 128, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #4ade80;
    selection-color: #1a1f2e;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #4ade80;
}

QLineEdit::placeholder {
    color: #64748b;
}

QTextEdit {
    background-color: #2a3149;
    color: #e2e8f0;
    border: 1px solid rgba(74, 222, 128, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #4ade80;
    selection-color: #1a1f2e;
}

QTextEdit:focus {
    border: 1px solid #4ade80;
}

/* ── SpinBox arrows ─────────────────────────────────────────────── */
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #323b54;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #4ade80;
}

QSpinBox::up-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid #94a3b8;
    width: 0; height: 0;
}

QSpinBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94a3b8;
    width: 0; height: 0;
}

/* ── Scrollbar ──────────────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #1e2538;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3b4560;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4ade80;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1e2538;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #3b4560;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4ade80;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ── Message Box ────────────────────────────────────────────────── */
QMessageBox {
    background-color: #232a3e;
}

QMessageBox QLabel {
    color: #e2e8f0;
    font-size: 14px;
}

QMessageBox QPushButton {
    background-color: #323b54;
    color: #e2e8f0;
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 6px;
    padding: 8px 24px;
    font-weight: 600;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #4ade80;
    color: #1a1f2e;
}

/* ── Tooltip ────────────────────────────────────────────────────── */
QToolTip {
    background-color: #2a3149;
    color: #e2e8f0;
    border: 1px solid #4ade80;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""


def main():
    print("Bắt đầu khởi tạo hệ thống bảng cơ sở dữ liệu Focus Garden...")
    init_db()
    print("=> Cơ sở dữ liệu focus_garden.sqlite đã được tạo / kết nối thành công!")
    
    app = QApplication(sys.argv)
    
    # Sử dụng style Fusion đem lại giao diện phẳng gọn nhẹ và hiện đại hơn
    app.setStyle("Fusion") 
    
    # Áp dụng global dark-nature theme
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
