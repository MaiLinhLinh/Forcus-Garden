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
    print(f"[DEBUG] ===== save_distraction =====")
    print(f"[DEBUG] session_id={session_id}, app_name='{app_name}', duration={duration_seconds}s")

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
        print(f"[DEBUG] Distraction saved successfully to DB")
        print(f"[DEBUG] ===== END save_distraction =====")
    except Exception as e:
        print(f"[DEBUG] ERROR saving distraction: {e}")
        raise
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

        # DEBUG: Log all distractions found in database
        print(f"[DEBUG] ===== get_distraction_stats for session_id={session_id} =====")
        print(f"[DEBUG] Total distractions found in DB: {len(rows)}")

        details = []
        for r in rows:
            detail = {"app": r.app_name, "seconds": r.duration_seconds}
            details.append(detail)
            print(f"[DEBUG]   - App: '{r.app_name}', Duration: {r.duration_seconds}s, Timestamp: {r.timestamp}")

        total = sum(r.duration_seconds for r in rows)
        result = {"count": len(rows), "total_seconds": total, "details": details}

        # VALIDATION: Check for data consistency
        details_sum = sum(d['seconds'] for d in details)
        print(f"[DEBUG] Summary: count={result['count']}, total_seconds={result['total_seconds']}")
        print(f"[DEBUG] Details list length: {len(result['details'])}")
        print(f"[DEBUG] Sum of detail seconds: {details_sum}")

        # Data integrity checks
        if result['count'] != len(result['details']):
            print(f"[ERROR] DATA INTEGRITY: count={result['count']} != details length={len(result['details'])}!")
        if result['total_seconds'] != details_sum:
            print(f"[ERROR] DATA INTEGRITY: total_seconds={result['total_seconds']} != sum of details={details_sum}!")

        print(f"[DEBUG] ===== END get_distraction_stats =====")

        return result
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
