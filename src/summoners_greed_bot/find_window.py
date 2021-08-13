import numpy as np
import win32api
import win32con
import win32gui
import win32ui


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

        rect = win32gui.GetWindowRect(self.hwnd)

        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - rect[0]
        self.h = rect[3] - rect[1]

        self.un_minimize()
        # self.set_foreground()

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

        win32gui.PostMessage(self.child_hwnd, win32con.WM_MOUSEMOVE, 0, lParam)

        win32gui.PostMessage(self.child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.PostMessage(self.child_hwnd, win32con.WM_LBUTTONUP, 0, lParam)


if __name__ == '__main__':
    import cv2
    cv2.imwrite(
        'output.png',
        BlueStacksWindow()
        .take_screenshot()
    )
