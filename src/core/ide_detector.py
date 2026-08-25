"""
IDE Detector - Detects installed IDEs across platforms.

Supports VS Code, JetBrains IDEs (PyCharm, IntelliJ, WebStorm, etc.),
Sublime Text, Atom, and Notepad++ on macOS, Windows, and Linux.
"""

import os
import subprocess
import platform
try:
    import psutil
except ImportError:
    psutil = None
from typing import Dict, List, Optional


class IDEDetector:
    """Detect and manage different IDEs across platforms."""

    def __init__(self):
        self.ides: Dict[str, Dict] = self.detect_ides()

    def detect_ides(self) -> Dict[str, Dict]:
        """Detect all installed IDEs on the system."""
        ides = {}
        system = platform.system()

        # VS Code
        vscode_paths = [
            "code",
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            "C:/Program Files/Microsoft VS Code/Code.exe",
            f"C:/Users/{os.getenv('USERNAME', '')}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        ]
        for path in vscode_paths:
            if self._check_command_exists(path):
                ides["vscode"] = {
                    "name": "Visual Studio Code",
                    "command": path,
                    "type": "vscode",
                }
                break

        # JetBrains IDEs
        jetbrains_ides = [
            ("pycharm", "PyCharm"),
            ("intellij", "IntelliJ IDEA"),
            ("webstorm", "WebStorm"),
            ("phpstorm", "PhpStorm"),
            ("goland", "GoLand"),
            ("clion", "CLion"),
            ("rider", "Rider"),
            ("rubymine", "RubyMine"),
            ("datagrip", "DataGrip"),
        ]

        if system == "Darwin":  # macOS
            for ide_id, ide_name in jetbrains_ides:
                app_path = f"/Applications/{ide_name}.app"
                if os.path.exists(app_path):
                    ides[ide_id] = {
                        "name": ide_name,
                        "command": app_path,
                        "type": "jetbrains",
                        "launcher": f"/usr/local/bin/{ide_id}",
                    }
        elif system == "Windows":
            for ide_id, ide_name in jetbrains_ides:
                path = f"C:/Program Files/JetBrains\{ide_name}"
                if os.path.exists(path):
                    ides[ide_id] = {
                        "name": ide_name,
                        "command": path,
                        "type": "jetbrains",
                    }

        # Sublime Text
        sublime_paths = [
            "subl",
            "/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl",
            "C:/Program Files/Sublime Text 3/sublime_text.exe",
        ]
        for path in sublime_paths:
            if self._check_command_exists(path):
                ides["sublime"] = {
                    "name": "Sublime Text",
                    "command": path,
                    "type": "sublime",
                }
                break

        # Atom
        if self._check_command_exists("atom"):
            ides["atom"] = {
                "name": "Atom",
                "command": "atom",
                "type": "atom",
            }

        # Notepad++ (Windows only)
        if system == "Windows":
            notepad_path = "C:/Program Files/Notepad++/notepad++.exe"
            if os.path.exists(notepad_path):
                ides["notepadpp"] = {
                    "name": "Notepad++",
                    "command": notepad_path,
                    "type": "notepadpp",
                }

        return ides

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH or at the given path."""
        try:
            if os.path.exists(command):
                return True

            cmd = ["which", command] if platform.system() != "Windows" else ["where", command]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def detect_active_ide(self) -> Optional[str]:
        """Detect which IDE is currently active/focused."""
        system = platform.system()

        if system == "Darwin":
            return self._detect_active_ide_macos()
        elif system == "Windows":
            return self._detect_active_ide_windows()
        elif system == "Linux":
            return self._detect_active_ide_linux()

        return None

    def _detect_active_ide_macos(self) -> Optional[str]:
        """Detect active IDE on macOS using AppleScript."""
        try:
            script = (
                'tell application "System Events" to get name of first '
                "application process whose frontmost is true"
            )
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True,
            )
            app_name = result.stdout.strip()

            ide_mapping = {
                "Visual Studio Code": "vscode",
                "PyCharm": "pycharm",
                "IntelliJ IDEA": "intellij",
                "WebStorm": "webstorm",
                "PhpStorm": "phpstorm",
                "GoLand": "goland",
                "CLion": "clion",
                "Sublime Text": "sublime",
                "Atom": "atom",
            }

            return ide_mapping.get(app_name)
        except Exception:
            return None

    def _detect_active_ide_windows(self) -> Optional[str]:
        """Detect active IDE on Windows."""
        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()

            ide_mapping = {
                "code.exe": "vscode",
                "pycharm64.exe": "pycharm",
                "idea64.exe": "intellij",
                "webstorm64.exe": "webstorm",
                "phpstorm64.exe": "phpstorm",
                "goland64.exe": "goland",
                "clion64.exe": "clion",
                "sublime_text.exe": "sublime",
                "atom.exe": "atom",
                "notepad++.exe": "notepadpp",
            }

            return ide_mapping.get(process_name)
        except Exception:
            return None

    def _detect_active_ide_linux(self) -> Optional[str]:
        """Detect active IDE on Linux using xdotool."""
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True, text=True,
            )
            window_title = result.stdout.strip().lower()

            if "visual studio code" in window_title or "code" in window_title:
                return "vscode"
            elif "pycharm" in window_title:
                return "pycharm"
            elif "intellij" in window_title:
                return "intellij"
            elif "sublime" in window_title:
                return "sublime"
            elif "atom" in window_title:
                return "atom"

            return None
        except Exception:
            return None

    def get_ide_info(self, ide_id: str) -> Optional[Dict]:
        """Get IDE information by ID."""
        return self.ides.get(ide_id)

    def list_available_ides(self) -> List[Dict]:
        """List all detected IDEs."""
        return [
            {"id": ide_id, "name": info["name"], "type": info["type"]}
            for ide_id, info in self.ides.items()
        ]
