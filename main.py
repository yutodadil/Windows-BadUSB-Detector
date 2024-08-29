import ctypes
import threading
import time
from typing import Callable
import keyboard
import os

# 定数
KEYS_THRESHOLD = 15  # 文字数のしきい値
TIME_FRAME = 0.45    # 秒数のしきい値
BLOCK_INPUT = 2      # WindowsのBlockInput関数の引数

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()

class BadUSBDetector:
    def __init__(self):
        self.start_time: float = time.time()
        self.key_count: int = 0
        self.detected: bool = False
        self.lock: threading.Lock = threading.Lock()

    def reset(self) -> None:
        """カウンターとタイマーをリセットする"""
        self.start_time = time.time()
        self.key_count = 0

    def on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        """キーボードイベントのハンドラ"""
        with self.lock:
            if self.detected:
                return

            current_time = time.time()
            self.key_count += 1

            if (current_time - self.start_time) > TIME_FRAME:
                self.reset()

            if self.key_count >= KEYS_THRESHOLD:
                self.detect_badusb()

    def detect_badusb(self) -> None:
        """BadUSBを検出し、対応を行う"""
        print("BadUSB detected! Disabling keyboard...")
        self.detected = True
        self.disable_keyboard()

    def disable_keyboard(self) -> None:
        """キーボードを無効化する"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            if not user32.BlockInput(True):
                raise ctypes.WinError(ctypes.get_last_error())
        except Exception as e:
            print(f"Failed to disable keyboard: {e}")

    def start(self) -> None:
        """検出を開始する"""
        keyboard.hook(self.on_key_event)
        print("BadUSB Detector is running...")

def main() -> None:
    """メイン関数"""
    detector = BadUSBDetector()
    detector.start()
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("Detector stopped by user.")
    finally:
        keyboard.unhook_all()

if __name__ == "__main__":
    main()
