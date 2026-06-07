"""Модуль для активации и обхода Setup Assistant"""
import subprocess
from typing import Optional, Callable
from core.profile_builder import ProfileBuilder

class Activator:
    def __init__(self):
        self.progress_callback = None
    
    def set_progress_callback(self, callback: Callable[[str], None]):
        self.progress_callback = callback
    
    def _log(self, message: str):
        if self.progress_callback:
            self.progress_callback(message)
        print(message)
    
    def activate_and_bypass(self, ssid: Optional[str] = None, password: Optional[str] = None) -> bool:
        try:
            self._log("1/6 Спаривание устройства...")
            subprocess.run(["pymobiledevice3", "lockdown", "pair"], capture_output=True, timeout=30)
            self._log("2/6 Активация устройства...")
            subprocess.run(["pymobiledevice3", "activation", "activate", "--now"], capture_output=True, timeout=60)
            self._log("3/6 Перевод в режим Надзора...")
            subprocess.run(["pymobiledevice3", "profile", "supervise", "Activator"], capture_output=True, timeout=30)
            self._log("4/6 Создание профиля пропуска...")
            profile_path = ProfileBuilder.create_skip_profile(ssid, password)
            self._log(f"   ✅ Профиль: {profile_path}")
            self._log("5/6 Установка профиля...")
            subprocess.run(["pymobiledevice3", "profile", "install", profile_path], capture_output=True, timeout=30)
            self._log("6/6 Перезагрузка устройства...")
            subprocess.run(["pymobiledevice3", "diagnostics", "restart"], capture_output=True, timeout=10)
            self._log("\n✅ Активация завершена! Устройство перезагрузится на рабочий стол.")
            return True
        except Exception as e:
            self._log(f"\n❌ Ошибка: {e}")
            return False
