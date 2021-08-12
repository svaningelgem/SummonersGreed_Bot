import time

import numpy as np
import win32api
import win32con
import win32gui
import win32ui


class Window:
    def __init__(self, hwnd: int):
        self.hwnd = hwnd

        rect = win32gui.GetWindowRect(hwnd)
        # rect2 = win32gui.GetClientRect(hwnd)

        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - rect[0]
        self.h = rect[3] - rect[1]

    def set_foreground(self) -> None:
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self.hwnd)

    def un_minimize(self) -> None:
        """If the window is minimized, restore it."""
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

    def take_screenshot(self) -> np.ndarray:
        hDC = win32gui.GetWindowDC(self.hwnd)
        myDC = win32ui.CreateDCFromHandle(hDC)
        newDC = myDC.CreateCompatibleDC()

        myBitMap = win32ui.CreateBitmap()
        myBitMap.CreateCompatibleBitmap(myDC, self.w, self.h)

        newDC.SelectObject(myBitMap)

        newDC.BitBlt((0, 0), (self.w, self.h), myDC, (0, 0), win32con.SRCCOPY)

        myBitMap.Paint(newDC)
        # windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

        signedIntsArray = myBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        win32gui.DeleteObject(myBitMap.GetHandle())

        myDC.DeleteDC()
        newDC.DeleteDC()

        win32gui.ReleaseDC(self.hwnd, hDC)

        return img

    def click(self, x, y):
        lParam = win32api.MAKELONG(int(x), int(y))

        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)

        time.sleep(0.05)


def find_window_with_title(title: str) -> Window:
    win = Window(hwnd=win32gui.FindWindow(None, title))
    win.un_minimize()
    # win.set_foreground()
    return win


if __name__ == '__main__':
    import cv2
    cv2.imwrite(
        'output.png',
        find_window_with_title('BlueStacks')
        .take_screenshot()
    )
