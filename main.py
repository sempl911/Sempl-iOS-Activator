#!/usr/bin/env python3
import sys
import subprocess

def check_pymobiledevice3():
    try:
        subprocess.run(["pymobiledevice3", "usbmux", "list"], capture_output=True, timeout=5)
        return True
    except FileNotFoundError:
        return False

if not check_pymobiledevice3():
    print("⚠️ pymobiledevice3 не найден!")
    print("\nУстановите командой: pip install pymobiledevice3")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
app.setApplicationName("Sempl Activator Pro")
app.setOrganizationName("Sempl")
window = MainWindow()
window.show()
sys.exit(app.exec())
