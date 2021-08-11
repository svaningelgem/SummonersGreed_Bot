import win32con
import win32gui


class Window:
    def __init__(self, hwnd: int):
        self.hwnd = hwnd

        rect = win32gui.GetWindowRect(hwnd)

        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - rect[0]
        self.h = rect[3] - rect[1]

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self.hwnd)

    def un_minimize(self):
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)


def find_window_with_title(title):
    win = Window(hwnd=win32gui.FindWindow(None, title))
    win.un_minimize()
    win.set_foreground()
    return win


if __name__ == '__main__':
    print(
        find_window_with_title('BlueStacks')
    )