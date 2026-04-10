import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Lấy đường dẫn gốc của dự án thay vì thư mục database để đặt file focus_garden.sqlite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'focus_garden.sqlite')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Tạo tất cả bảng nếu chưa tồn tại."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Trả về một session database. Người gọi chịu trách nhiệm đóng session."""
    return SessionLocal()
