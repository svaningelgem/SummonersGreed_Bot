import ctypes
import time

import numpy as np
import win32api
import win32con
import win32gui
import win32ui

from summoners_greed_bot.detectors import Rect


class BlueStacksWindow:
    def _setup_hwnds(self):
        # 1. Find main window. I assume only 1 instance.
        self.hwnd = win32gui.FindWindow(None, "BlueStacks")

        # 2. Find a child with class BlueStacksApp
        def child_found_callback(child_hwnd, save_in):
            if win32gui.GetClassName(child_hwnd) != "plrNativeInputWindowClass":
                return

            save_in.append(child_hwnd)

        child_windows = []
        win32gui.EnumChildWindows(self.hwnd, child_found_callback, child_windows)
        if len(child_windows) != 1:
            raise ValueError("We need exactly 1 sub-window for this to work!")

        self.child_hwnd = child_windows[0]

    def __init__(self):
        self._setup_hwnds()

        def _get_rect(hwnd):
            l, t, b, r = win32gui.GetWindowRect(hwnd)
            return Rect(l, t, b - l, r - t)

        self.rect_main = _get_rect(self.hwnd)
        self.rect_child = _get_rect(self.child_hwnd)

        self.un_minimize()
        # self.set_foreground()

    def set_foreground(self) -> None:
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self.hwnd)

    def un_minimize(self) -> None:
        """If the window is minimized, restore it."""
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

    def take_screenshot(self, use_index: int = 2, use_parent: bool = False) -> np.ndarray:
        hwnd = self.hwnd if use_parent else self.child_hwnd
        rect = self.rect_main if use_parent else self.rect_child

        hDC = win32gui.GetWindowDC(hwnd)
        myDC = win32ui.CreateDCFromHandle(hDC)
        newDC = myDC.CreateCompatibleDC()

        myBitMap = win32ui.CreateBitmap()
        myBitMap.CreateCompatibleBitmap(myDC, rect.w, rect.h)

        newDC.SelectObject(myBitMap)
        # newDC.BitBlt((0, 0), (rect.w, rect.h), myDC, (0, 0), win32con.SRCCOPY)
        # myBitMap.Paint(newDC)
        ctypes.windll.user32.PrintWindow(hwnd, newDC.GetSafeHdc(), use_index)

        signedIntsArray = myBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (rect.h, rect.w, 4)

        win32gui.DeleteObject(myBitMap.GetHandle())

        myDC.DeleteDC()
        newDC.DeleteDC()

        win32gui.ReleaseDC(self.hwnd, hDC)

        return img

    def click(self, x, y):
        lParam = win32api.MAKELONG(int(x), int(y))

        win32gui.PostMessage(self.child_hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
        time.sleep(0.1)

        win32gui.PostMessage(self.child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.1)

        win32gui.PostMessage(self.child_hwnd, win32con.WM_LBUTTONUP, 0, lParam)


if __name__ == '__main__':
    import cv2
    cv2.imwrite(
        'debug_output.png',
        BlueStacksWindow()
        .take_screenshot()
    )
