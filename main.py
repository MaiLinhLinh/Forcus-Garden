import sys
from database.db_config import init_db
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    print("Bắt đầu khởi tạo hệ thống bảng cơ sở dữ liệu Focus Garden...")
    init_db()
    print("=> Cơ sở dữ liệu focus_garden.sqlite đã được tạo / kết nối thành công!")
    
    app = QApplication(sys.argv)
    
    # Sử dụng style Fusion đem lại giao diện phẳng gọn nhẹ và hiện đại hơn
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
