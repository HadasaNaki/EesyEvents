import os
import shutil
import stat
import time

TARGET_DIR = r"C:\agent\_work"

def on_rm_error(func, path, exc_info):
    # Error handler for shutil.rmtree
    # If the error is due to read-only access, change the file attribute and retry
    os.chmod(path, stat.S_IWRITE)
    try:
        func(path)
        print(f"Fixed permissions and deleted: {path}")
    except Exception as e:
        print(f"Failed to delete {path}: {e}")

def cleanup():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory {TARGET_DIR} does not exist. Nothing to clean.")
        return

    print(f"Attempting to clean up {TARGET_DIR}...")
    try:
        shutil.rmtree(TARGET_DIR, onerror=on_rm_error)
        print("✅ Cleanup successful! The agent work directory has been cleared.")
    except Exception as e:
        print(f"❌ Critical error during cleanup: {e}")
        print("Please manually delete the folder: C:\\agent\\_work")

if __name__ == "__main__":
    cleanup()
