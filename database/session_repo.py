"""
session_repo.py - Các hàm thao tác CSDL cho Session và Distraction.
Gom tất cả DB logic vào đây để UI không gọi trực tiếp vào SQLAlchemy.
"""
import json
from typing import List
from datetime import datetime
from database.db_config import get_db
from database.models import Session, StudyZone, Distraction


def create_session(subject: str, target_duration_mins: int, keywords: List[str]) -> int:
    """
    Tạo bản ghi Session mới và StudyZone liên kết.
    Trả về session_id vừa tạo.
    """
    db = get_db()
    try:
        session = Session(
            user_id=None,          # Phase hiện tại chưa có đăng nhập
            subject=subject,
            target_duration_mins=target_duration_mins,
            status="in_progress",
            started_at=datetime.now(),
        )
        db.add(session)
        db.flush()  # Lấy session.id trước khi commit

        zone = StudyZone(
            session_id=session.id,
            allowed_keywords=json.dumps(keywords, ensure_ascii=False),
        )
        db.add(zone)
        db.commit()
        return session.id
    finally:
        db.close()


def save_distraction(session_id: int, app_name: str, duration_seconds: int):
    """Ghi một sự kiện xao nhãng vào bảng distractions."""
    db = get_db()
    try:
        d = Distraction(
            session_id=session_id,
            app_name=app_name,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(),
        )
        db.add(d)
        db.commit()
    finally:
        db.close()


def close_session(session_id: int, actual_duration_secs: int, status: str):
    """
    Cập nhật Session khi phiên kết thúc (success/failed).
    Lưu thời gian thực học tính bằng GIÂY để chính xác.
    """
    db = get_db()
    try:
        session = db.get(Session, session_id)
        if session:
            session.actual_duration_secs = actual_duration_secs  # Lưu chính xác (giây)
            session.actual_duration_mins = actual_duration_secs // 60  # Làm tròn xuống (phút) - giữ tương thích
            session.status = status
            session.ended_at = datetime.now()
            db.commit()
    finally:
        db.close()


def get_distraction_stats(session_id: int) -> dict:
    """
    Trả về thống kê xao nhãng của một phiên:
    { "count": số lần, "total_seconds": tổng thời gian, "details": list }
    """
    db = get_db()
    try:
        rows = db.query(Distraction).filter(Distraction.session_id == session_id).all()
        details = [{"app": r.app_name, "seconds": r.duration_seconds} for r in rows]
        total = sum(r.duration_seconds for r in rows)
        return {"count": len(rows), "total_seconds": total, "details": details}
    finally:
        db.close()


def get_all_sessions() -> List[Session]:
    """
    Lấy tất cả phiên học, sắp xếp theo thời gian bắt đầu giảm dần (mới nhất trước).
    Hiển thị tất cả, không giới hạn số lượng.
    """
    db = get_db()
    try:
        return db.query(Session)\
                 .order_by(Session.started_at.desc())\
                 .all()
    finally:
        db.close()
