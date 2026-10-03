"""A click-through, always-on-top red target dot for Windows."""

import ctypes
from ctypes import wintypes


DOT_SIZE = 6
RED = (255, 30, 30)
OFFSET_X = 0
OFFSET_Y = 0

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_ssize_t

WS_POPUP = 0x80000000
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
SW_SHOW = 5
LWA_COLORKEY = 0x00000001
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)


@WNDPROC
def window_proc(hwnd, message, wparam, lparam):
    if message == 0x000F:  # WM_PAINT
        ps = ctypes.create_string_buffer(72)
        hdc = user32.BeginPaint(hwnd, ps)
        # Black is the colour key (fully transparent); the red circle remains visible.
        brush = gdi32.CreateSolidBrush(RED[0] | (RED[1] << 8) | (RED[2] << 16))
        old_brush = gdi32.SelectObject(hdc, brush)
        gdi32.Ellipse(hdc, 0, 0, DOT_SIZE, DOT_SIZE)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.DeleteObject(brush)
        user32.EndPaint(hwnd, ps)
        return 0
    if message == 0x0002:  # WM_DESTROY
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, message, wparam, lparam)


def main() -> None:
    instance = ctypes.windll.kernel32.GetModuleHandleW(None)
    class_name = "ScreenTargetWindow"
    wnd_class = WNDCLASSW(0, ctypes.cast(window_proc, ctypes.c_void_p), 0, 0, instance, None, None, None, None, class_name)
    if not user32.RegisterClassW(ctypes.byref(wnd_class)):
        raise ctypes.WinError()

    x = (user32.GetSystemMetrics(0) - DOT_SIZE) // 2 + OFFSET_X
    y = (user32.GetSystemMetrics(1) - DOT_SIZE) // 2 + OFFSET_Y
    hwnd = user32.CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST,
        class_name,
        None,
        WS_POPUP,
        x,
        y,
        DOT_SIZE,
        DOT_SIZE,
        None,
        None,
        instance,
        None,
    )
    if not hwnd:
        raise ctypes.WinError()
    user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, LWA_COLORKEY)
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
    user32.ShowWindow(hwnd, SW_SHOW)
    user32.UpdateWindow(hwnd)

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


if __name__ == "__main__":
    main()
