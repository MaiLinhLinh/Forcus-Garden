"""
Kiểm tra tất cả sessions trong DB
"""
import sys
sys.path.insert(0, 'Code_base')

from database.db_config import get_db
from database.models import Session

print("=" * 80)
print("TẤT CẢ SESSIONS TRONG DATABASE")
print("=" * 80)

db = get_db()
try:
    sessions = db.query(Session).order_by(Session.started_at.desc()).all()

    if not sessions:
        print("Chưa có session nào trong DB.")
    else:
        print(f"Tổng: {len(sessions)} session(s)\n")

        for s in sessions:
            status_icon = "✅" if s.status == "success" else "❌"
            date_str = s.started_at.strftime("%d/%m/%Y %H:%M:%S")

            print(f"ID: {s.id}")
            print(f"  Ngày: {date_str}")
            print(f"  Môn: {s.subject}")
            print(f"  Mục tiêu: {s.target_duration_mins} phút")
            print(f"  Thực tế: {s.actual_duration_mins} phút")
            print(f"  Trạng thái: {s.status} {status_icon}")
            print(f"  Status match: {'✓' if (s.status == 'success' and s.actual_duration_mins >= s.target_duration_mins) or (s.status == 'failed' and s.actual_duration_mins < s.target_duration_mins) else '✗ KHÔNG KHỚP!'}")
            print("-" * 80)

finally:
    db.close()
