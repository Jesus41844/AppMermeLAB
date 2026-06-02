import shutil
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "mermelab_v2.db")


def backup():
    if not os.path.exists(DB_PATH):
        print("Database file not found:", DB_PATH)
        return 1
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = f"{DB_PATH}.{ts}.bak"
    shutil.copy2(DB_PATH, dest)
    print("Backup created:", dest)
    return 0


def restore(src):
    if not os.path.exists(src):
        print("Backup file not found:", src)
        return 1
    shutil.copy2(src, DB_PATH)
    print("Database restored to:", DB_PATH)
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "backup":
        return backup()
    if cmd == "restore" and len(argv) >= 3:
        return restore(argv[2])
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
