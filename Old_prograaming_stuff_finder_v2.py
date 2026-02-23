import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# I made this because my Mac had too many old dev tools and random installs.
# This just shows what's on your PATH and common dev folders.
# It DOES NOT delete anything.



TOOLS = [
    "python3",
    "pip3",
    "node",
    "npm",
    "yarn",
    "pnpm",
    "java",
    "javac",
    "dotnet",
    "git",
    "brew",
    "docker"
]

# common places where programming stuff usually lives on macOS
FOLDERS = [
    "/opt/homebrew",
    "/opt/homebrew/Cellar",
    "/usr/local/Homebrew",
    "/usr/local/Cellar",

    str(Path.home() / ".nvm"),
    str(Path.home() / ".pyenv"),
    str(Path.home() / "miniconda3"),
    str(Path.home() / "anaconda3"),

    "/Library/Java/JavaVirtualMachines",

    str(Path.home() / "Library/Developer/Xcode/DerivedData"),

    str(Path.home() / "Library/Application Support/VMware Fusion"),
    str(Path.home() / "Virtual Machines.localized"),
    str(Path.home() / "Documents/UTM"),
]


def run(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        text = (p.stdout + "\n" + p.stderr).strip()
        if not text:
            return ""
        return text.splitlines()[0]
    except Exception:
        return ""


def realpath(cmd):
    p = shutil.which(cmd)
    if not p:
        return None
    try:
        return str(Path(p).resolve())
    except Exception:
        return p


def scan_tools():
    results = []

    for t in TOOLS:
        path = realpath(t)
        if not path:
            continue

        version = run([t, "--version"]) or run([t, "-version"]) or run([t, "-v"])

        results.append({
            "name": t,
            "path": path,
            "version": version
        })

    # nvm is usually not a real binary, so just detect the folder
    nvm_dir = Path.home() / ".nvm"
    if nvm_dir.exists():
        results.append({
            "name": "nvm",
            "path": str(nvm_dir),
            "version": "managed via shell"
        })

    return results


def scan_folders():
    found = []
    for f in FOLDERS:
        if os.path.exists(f):
            found.append(f)
    return found


def write_report(data):
    BASE_DIR = Path(__file__).parent.resolve()

    json_file = BASE_DIR / "dev_stuff_report.json"
    md_file = BASE_DIR / "dev_stuff_report.md"

    Path(json_file).write_text(json.dumps(data, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Dev Stuff Finder\n")
    lines.append(f"Generated: {data['generated_at']}\n")

    lines.append("## Tools found\n")
    for t in data["tools"]:
        lines.append(f"- {t['name']}")
        lines.append(f"  path: `{t['path']}`")
        if t["version"]:
            lines.append(f"  version: `{t['version']}`")

    lines.append("\n## Dev folders found\n")
    for f in data["folders"]:
        lines.append(f"- `{f}`")

    lines.append("\n## Notes\n")
    for n in data["notes"]:
        lines.append(f"- {n}")

    Path(md_file).write_text("\n".join(lines), encoding="utf-8")

    return json_file, md_file


if __name__ == "__main__":
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tools": scan_tools(),
        "folders": scan_folders(),
        "notes": [
            "This script only shows what's installed. It does not delete anything.",
            "Use brew / nvm / pyenv / conda to remove versions properly.",
            "I built this to quickly see old dev installs before cleaning my Mac."
        ]
    }

    jf, mf = write_report(report)

    print("done.")
    print(f"created {jf}")
    print(f"created {mf}")