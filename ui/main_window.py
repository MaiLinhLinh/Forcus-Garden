from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .create_session_widget import CreateSessionWidget
from .history_widget import HistoryWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌳  Focus Garden")
        self.setMinimumSize(850, 620)
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        # Tab styling is handled by the global stylesheet in main.py
        # Only override specific tab-level settings here
        self.tabs.setDocumentMode(True)  # Cleaner tab appearance
        
        self.create_session_tab = CreateSessionWidget()
        self.history_tab = HistoryWidget()
        
        self.tabs.addTab(self.create_session_tab, "🌱  Trồng Cây")
        self.tabs.addTab(self.history_tab, "📜  Lịch Sử")
        
        self.setCentralWidget(self.tabs)
