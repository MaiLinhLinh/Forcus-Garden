#!/usr/bin/env python3
"""
Test script to verify distraction tracking data flow.
This script simulates the complete workflow to help debug the discrepancy.
"""

from database.db_config import get_db
from database.models import Distraction, Session
from database.session_repo import (
    create_session,
    save_distraction,
    get_distraction_stats,
    close_session
)

def test_distraction_flow():
    """Test the complete distraction tracking flow."""
    print("=" * 80)
    print("DISTRACTION TRACKING DEBUG TEST")
    print("=" * 80)

    # 1. Create a test session
    print("\n[TEST] Creating test session...")
    session_id = create_session("Test Subject", 25, ["vscode", "chrome"])
    print(f"[TEST] Session created with ID: {session_id}")

    # 2. Simulate saving multiple distractions
    print("\n[TEST] Simulating distraction recordings...")
    test_distractions = [
        ("Discord", 12),
        ("YouTube", 8),
        ("Facebook", 15),
        ("Discord", 10),  # Second Discord entry
        ("Zalo", 6),
    ]

    for idx, (app, duration) in enumerate(test_distractions, 1):
        print(f"[TEST] Saving distraction {idx}: {app} ({duration}s)")
        save_distraction(session_id, app, duration)

    # 3. Query the database directly
    print("\n[TEST] Querying database directly...")
    db = get_db()
    try:
        all_distractions = db.query(Distraction).filter(
            Distraction.session_id == session_id
        ).all()

        print(f"[TEST] Total records in DB: {len(all_distractions)}")
        for d in all_distractions:
            print(f"[TEST]   - ID={d.id}, App='{d.app_name}', Duration={d.duration_seconds}s")
    finally:
        db.close()

    # 4. Get stats using the function
    print("\n[TEST] Getting stats via get_distraction_stats()...")
    stats = get_distraction_stats(session_id)

    print(f"[TEST] Stats result:")
    print(f"[TEST]   - count: {stats['count']}")
    print(f"[TEST]   - total_seconds: {stats['total_seconds']}")
    print(f"[TEST]   - details length: {len(stats['details'])}")

    print(f"\n[TEST] Details list:")
    for idx, detail in enumerate(stats['details'], 1):
        print(f"[TEST]   {idx}. App='{detail['app']}', Seconds={detail['seconds']}")

    # 5. Verify calculations
    print("\n[TEST] Verification:")
    expected_count = len(test_distractions)
    expected_total = sum(duration for _, duration in test_distractions)

    print(f"[TEST] Expected count: {expected_count}, Actual: {stats['count']}")
    print(f"[TEST] Expected total: {expected_total}, Actual: {stats['total_seconds']}")

    if stats['count'] == expected_count:
        print("[TEST] [OK] COUNT MATCHES")
    else:
        print(f"[TEST] [ERROR] COUNT MISMATCH: Expected {expected_count}, got {stats['count']}")

    if stats['total_seconds'] == expected_total:
        print("[TEST] [OK] TOTAL SECONDS MATCH")
    else:
        print(f"[TEST] [ERROR] TOTAL SECONDS MISMATCH: Expected {expected_total}, got {stats['total_seconds']}")

    if len(stats['details']) == expected_count:
        print("[TEST] [OK] DETAILS LENGTH MATCHES")
    else:
        print(f"[TEST] [ERROR] DETAILS LENGTH MISMATCH: Expected {expected_count}, got {len(stats['details'])}")

    # 6. Clean up
    print("\n[TEST] Cleaning up test data...")
    db = get_db()
    try:
        # Delete test session (cascade will delete distractions)
        session = db.get(Session, session_id)
        if session:
            db.delete(session)
            db.commit()
            print(f"[TEST] Test session deleted")
    finally:
        db.close()

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_distraction_flow()
