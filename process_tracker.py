import sqlite3
import psutil
import time
import getpass
import argparse
from datetime import datetime, timedelta

DATABASE = "process_tracker.db"
CHECK_INTERVAL = 300  # seconds
DORMANT_TIMEOUT_MIN = 10


def connect_db():
    return sqlite3.connect(DATABASE)


def init_db():
    """Create required tables if they do not exist."""
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS process_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    process_name TEXT,
                    status TEXT,
                    last_checked TEXT,
                    last_active TEXT,
                    UNIQUE(username, process_name)
                )"""
        )
        conn.commit()


def add_process(name: str):
    """Register a new process name to track."""
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO processes(name) VALUES (?)", (name,))
        conn.commit()


def get_process_names(conn):
    c = conn.cursor()
    c.execute("SELECT name FROM processes")
    return [row[0] for row in c.fetchall()]


def update_status(conn, username: str, process_name: str, status: str, last_active):
    now_str = datetime.utcnow().isoformat()
    last_active_str = last_active.isoformat() if last_active else None
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO process_status(username, process_name, status, last_checked, last_active)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username, process_name) DO UPDATE SET
            status=excluded.status,
            last_checked=excluded.last_checked,
            last_active=COALESCE(excluded.last_active, process_status.last_active)
        """,
        (username, process_name, status, now_str, last_active_str),
    )
    conn.commit()


def is_process_running(name: str) -> bool:
    for proc in psutil.process_iter(["name"]):
        if proc.info.get("name", "").lower() == name.lower():
            return True
    return False


def check_processes(username: str):
    with connect_db() as conn:
        process_names = get_process_names(conn)
        for name in process_names:
            running = is_process_running(name)
            c = conn.cursor()
            c.execute(
                "SELECT last_active FROM process_status WHERE username=? AND process_name=?",
                (username, name),
            )
            row = c.fetchone()
            last_active_time = datetime.fromisoformat(row[0]) if row and row[0] else None

            if running:
                status = "running"
                last_active = datetime.utcnow()
            else:
                if last_active_time and (
                    datetime.utcnow() - last_active_time
                ) > timedelta(minutes=DORMANT_TIMEOUT_MIN):
                    status = "dormant"
                else:
                    status = "not running"
                last_active = None

            update_status(conn, username, name, status, last_active)


def list_statuses():
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT username, process_name, status, last_checked, last_active FROM process_status"
        )
        rows = c.fetchall()
        for row in rows:
            print(row)


def run_tracker():
    username = getpass.getuser()
    print(f"Process tracker started for {username}. Checking every {CHECK_INTERVAL} seconds.")
    while True:
        try:
            check_processes(username)
        except Exception as exc:
            print("Error while checking processes:", exc)
        time.sleep(CHECK_INTERVAL)


def main():
    parser = argparse.ArgumentParser(description="Background process tracker")
    parser.add_argument("--add-process", action="append", help="Process name to add to tracking table")
    parser.add_argument("--list", action="store_true", help="List stored statuses and exit")
    args = parser.parse_args()

    init_db()

    if args.add_process:
        for proc in args.add_process:
            add_process(proc)
            print(f"Added process '{proc}' to tracking table")
        return

    if args.list:
        list_statuses()
        return

    run_tracker()


if __name__ == "__main__":
    main()
