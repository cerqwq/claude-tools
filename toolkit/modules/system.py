"""System Awareness - Processes, files, and system info."""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


def list_processes(filter_name=None):
    """List running processes. Optionally filter by name."""
    ps = 'Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet64 | ConvertTo-Json'
    result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    try:
        procs = json.loads(result.stdout)
        if not isinstance(procs, list):
            procs = [procs]
        if filter_name:
            filter_lower = filter_name.lower()
            procs = [p for p in procs if filter_lower in p.get("ProcessName", "").lower()]
        return procs, None
    except Exception as e:
        return None, str(e)


def kill_process(pid=None, name=None):
    """Kill a process by PID or name."""
    if pid:
        ps = f"Stop-Process -Id {pid} -Force"
    elif name:
        ps = f"Stop-Process -Name '{name}' -Force"
    else:
        return False, "Need pid or name"
    result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    return result.returncode == 0, result.stderr.strip() if result.stderr else None


def system_info():
    """Get basic system info."""
    info = {}
    cmds = {
        "hostname": "hostname",
        "os": 'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
        "cpu": 'wmic cpu get Name /value',
        "ram": 'wmic memorychip get Capacity /value',
        "disk": 'wmic logicaldisk get DeviceID,Size,FreeSpace /value',
    }
    for key, cmd in cmds.items():
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        info[key] = r.stdout.strip()
    return info, None


def list_dir(path=".", max_items=100):
    """List directory contents with details."""
    try:
        entries = []
        for i, entry in enumerate(Path(path).iterdir()):
            if i >= max_items:
                break
            stat = entry.stat()
            entries.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return entries, None
    except Exception as e:
        return None, str(e)


def read_file(path, max_lines=500):
    """Read a text file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line)
        return "".join(lines), None
    except Exception as e:
        return None, str(e)


def search_files(directory, pattern, max_results=50):
    """Search for files matching a glob pattern."""
    try:
        results = []
        for p in Path(directory).rglob(pattern):
            results.append(str(p))
            if len(results) >= max_results:
                break
        return results, None
    except Exception as e:
        return None, str(e)


def run_command(cmd, timeout=30):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return {
            "stdout": result.stdout[:5000],
            "stderr": result.stderr[:2000],
            "returncode": result.returncode,
        }, None
    except subprocess.TimeoutExpired:
        return None, "Command timed out"
    except Exception as e:
        return None, str(e)


def clipboard_get():
    """Get clipboard content."""
    ps = "Get-Clipboard"
    result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    return result.stdout.strip(), None


def clipboard_set(text):
    """Set clipboard content."""
    ps = f'Set-Clipboard -Value @"{text}"@'
    subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    return True, None
