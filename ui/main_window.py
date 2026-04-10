from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .create_session_widget import CreateSessionWidget
from .history_widget import HistoryWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus Garden - Dashboard")
        self.setMinimumSize(600, 450)
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 14px;
                padding: 10px 20px;
            }
        """)
        
        self.create_session_tab = CreateSessionWidget()
        self.history_tab = HistoryWidget()
        
        self.tabs.addTab(self.create_session_tab, "Trồng Cây")
        self.tabs.addTab(self.history_tab, "Lịch Sử Của Bạn")
        
        self.setCentralWidget(self.tabs)
