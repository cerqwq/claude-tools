"""GUI Automation - Mouse, keyboard, and window control."""

import time

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

import subprocess


def click(x, y, button="left", clicks=1):
    """Click at coordinates."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.click(x, y, button=button, clicks=clicks)
    return True, None


def type_text(text, interval=0.02):
    """Type text via keyboard."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.typewrite(text, interval=interval)
    return True, None


def press(key):
    """Press a single key (enter, tab, esc, etc)."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.press(key)
    return True, None


def hotkey(*keys):
    """Press key combo like hotkey('ctrl', 'c')."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.hotkey(*keys)
    return True, None


def scroll(amount, x=None, y=None):
    """Scroll mouse wheel. Positive=up, negative=down."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.scroll(amount, x=x, y=y)
    return True, None


def drag(x1, y1, x2, y2, duration=0.5):
    """Drag from (x1,y1) to (x2,y2)."""
    if not HAS_GUI:
        return False, "pyautogui not installed"
    pyautogui.moveTo(x1, y1)
    pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
    return True, None


def get_mouse_pos():
    """Get current mouse position."""
    if not HAS_GUI:
        return None, "pyautogui not installed"
    pos = pyautogui.position()
    return (pos.x, pos.y), None


def get_screen_size():
    """Get screen resolution."""
    if not HAS_GUI:
        return None, "pyautogui not installed"
    size = pyautogui.size()
    return (size.width, size.height), None


# Window management via PowerShell
def list_windows():
    """List visible windows with titles."""
    ps = 'Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object Id, MainWindowTitle | ConvertTo-Json'
    result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    return result.stdout, None


def focus_window(title_substring):
    """Focus a window by partial title match."""
    ps = f'''
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32 {{
            [DllImport("user32.dll")]
            public static extern bool SetForegroundWindow(IntPtr hWnd);
        }}
"@
    $p = Get-Process | Where-Object {{$_.MainWindowTitle -like "*{title_substring}*"}} | Select-Object -First 1
    if ($p) {{ [Win32]::SetForegroundWindow($p.MainWindowHandle); "OK" }} else {{ "NOT_FOUND" }}
    '''
    result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
    return result.stdout.strip(), None


def open_app(path_or_name):
    """Launch an application."""
    try:
        subprocess.Popen(path_or_name, shell=True)
        return True, None
    except Exception as e:
        return False, str(e)
