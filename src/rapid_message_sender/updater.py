import os
import sys
import json
import logging
import tempfile
import subprocess
import urllib.request
import urllib.error
import tomllib
from importlib.metadata import version, PackageNotFoundError
from typing import Optional, Dict, Any, Tuple
from PySide6.QtCore import QThread, Signal, QObject

logger = logging.getLogger(__name__)


def get_app_version() -> str:
    """Dynamically extracts the application version from pyproject.toml or installed package metadata."""
    # 1. Try reading directly from pyproject.toml when running from source
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        toml_path = os.path.join(root_dir, "pyproject.toml")
        if os.path.exists(toml_path):
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
                ver = data.get("project", {}).get("version")
                if ver:
                    return f"v{ver}" if not str(ver).startswith("v") else str(ver)
    except Exception as e:
        logger.debug(f"Could not read version from pyproject.toml: {e}")

    # 2. Fallback to package metadata
    try:
        ver = version("rapid-message-sender")
        return f"v{ver}" if not str(ver).startswith("v") else str(ver)
    except PackageNotFoundError:
        pass

    # 3. Default fallback
    return "v1.0.0"


CURRENT_VERSION = get_app_version()
GITHUB_REPO = "showayebDev/Rapid_Message_Sender"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Converts version strings like 'v1.0.0' or '1.0.1' into comparable integer tuples."""
    clean_str = version_str.lstrip("vV").strip()
    parts = []
    for part in clean_str.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            break
    return tuple(parts) if parts else (0, 0, 0)


class UpdateCheckWorker(QThread):
    """Background worker thread to query GitHub Releases API without blocking UI."""
    update_available = Signal(dict)       # Emits release info dict if update is found
    no_update_found = Signal(str)         # Emits current version message if up to date
    check_failed = Signal(str)            # Emits error string on failure

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def run(self):
        try:
            req = urllib.request.Request(
                API_URL,
                headers={
                    "User-Agent": "Rapid-Message-Sender-Updater",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    self.check_failed.emit(f"HTTP Error {response.status}")
                    return
                data = json.loads(response.read().decode("utf-8"))

            latest_tag = data.get("tag_name", "")
            if not latest_tag:
                self.check_failed.emit("No release tags found on GitHub.")
                return

            latest_ver = parse_version(latest_tag)
            curr_ver = parse_version(CURRENT_VERSION)

            if latest_ver > curr_ver:
                # Find binary asset (.exe or zipped package)
                assets = data.get("assets", [])
                exe_url = None
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if name.endswith(".exe"):
                        exe_url = asset.get("browser_download_url")
                        break

                release_info = {
                    "tag_name": latest_tag,
                    "name": data.get("name") or latest_tag,
                    "body": data.get("body", "No release notes provided."),
                    "download_url": exe_url,
                    "html_url": data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                }
                self.update_available.emit(release_info)
            else:
                self.no_update_found.emit(CURRENT_VERSION)

        except urllib.error.URLError as e:
            logger.warning(f"Network error checking for updates: {e}")
            self.check_failed.emit("Could not connect to GitHub servers. Please check your internet connection.")
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}", exc_info=True)
            self.check_failed.emit(str(e))


class DownloadUpdateWorker(QThread):
    """Background worker thread to download the latest executable binary."""
    progress_updated = Signal(int, int)   # downloaded_bytes, total_bytes
    download_finished = Signal(str)       # path to downloaded file
    download_failed = Signal(str)         # error message

    def __init__(self, download_url: str, save_path: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.download_url = download_url
        self.save_path = save_path

    def run(self):
        try:
            req = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": "Rapid-Message-Sender-Updater"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024

                with open(self.save_path, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress_updated.emit(downloaded, total_size)

            self.download_finished.emit(self.save_path)
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            self.download_failed.emit(str(e))


def apply_update_and_restart(new_exe_path: str):
    """
    Spawns a detached Windows batch script that waits for current app to exit,
    overwrites/replaces current running EXE (or installs new binary), deletes old version,
    and restarts the updated executable.
    """
    current_exe = os.path.abspath(sys.executable)
    is_frozen = getattr(sys, "frozen", False)

    if not is_frozen:
        # Running from Python source code
        logger.info("Running from source code. Updated file downloaded to: " + new_exe_path)
        # Simply launch the new EXE
        subprocess.Popen([new_exe_path], shell=True)
        sys.exit(0)

    # Windows batch script to replace running EXE cleanly after process termination
    bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
copy /y "{new_exe_path}" "{current_exe}"
del "{new_exe_path}"
start "" "{current_exe}"
del "%~f0"
"""
    bat_path = os.path.join(tempfile.gettempdir(), "rapid_sender_updater.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    # Execute batch script detached in background
    subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    sys.exit(0)
