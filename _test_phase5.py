from database.db_config import init_db
from database.session_repo import create_session, save_distraction, close_session, get_distraction_stats

init_db()
sid = create_session("Test Mon", 25, ["chrome", "vscode"])
print(f"Session created: id={sid}")
save_distraction(sid, "Spotify", 45)
save_distraction(sid, "Facebook", 120)
close_session(sid, 20, "failed")
stats = get_distraction_stats(sid)
print(f"Stats: {stats}")
print("OK: Phase 5 DB logic verified")
