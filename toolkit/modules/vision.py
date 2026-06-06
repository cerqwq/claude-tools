"""Screen Vision - Screenshot capture and OCR text extraction."""

import subprocess
import tempfile
import os
from pathlib import Path

try:
    import pyautogui
    from PIL import Image
    HAS_SCREENSHOT = True
except ImportError:
    HAS_SCREENSHOT = False


def screenshot(region=None, save_path=None):
    """Take a screenshot. region=(x, y, w, h) or None for full screen."""
    if not HAS_SCREENSHOT:
        return None, "pyautogui/Pillow not installed"

    img = pyautogui.screenshot(region=region)
    if save_path:
        img.save(save_path)
    return img, None


def ocr_image(image_path, lang="eng+chi_sim"):
    """OCR an image file using Tesseract or Windows built-in OCR."""
    # Try Tesseract first
    try:
        import pytesseract
        img = Image.open(image_path) if isinstance(image_path, str) else image_path
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip(), None
    except Exception:
        pass

    # Fallback: Windows built-in OCR via PowerShell
    return _windows_ocr(image_path)


def _windows_ocr(image_path):
    """Use Windows 10/11 built-in OCR (no extra install needed)."""
    abs_path = os.path.abspath(image_path).replace("\\", "\\\\")
    ps_script = f'''
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $null = [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime]

    $stream = [System.IO.File]::OpenRead("{abs_path}")
    $bitmap = [Windows.Graphics.Imaging.SoftwareBitmap]::CreateFromStreamAsync(
        [Windows.Storage.Streams.IRandomAccessStream]::FromStream($stream)
    ).GetAwaiter().GetResult()

    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    $result = $engine.RecognizeAsync($bitmap).GetAwaiter().GetResult()
    $result.Text
    '''
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), None
        return None, f"Windows OCR failed: {result.stderr[:200]}"
    except Exception as e:
        return None, str(e)


def see_screen(region=None):
    """Take screenshot and OCR it in one call. Returns (text, error)."""
    img, err = screenshot(region=region)
    if err:
        return None, err

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        tmp_path = f.name

    try:
        text, err = ocr_image(tmp_path)
        return text, err
    finally:
        os.unlink(tmp_path)


def find_on_screen(template_path, confidence=0.8):
    """Find a template image on screen. Returns (x, y) center or None."""
    try:
        loc = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if loc:
            center = pyautogui.center(loc)
            return (center.x, center.y), None
        return None, "Template not found on screen"
    except Exception as e:
        return None, str(e)
