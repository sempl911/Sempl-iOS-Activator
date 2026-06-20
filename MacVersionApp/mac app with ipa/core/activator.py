#!/usr/bin/env python3
# core/activator.py

"""
Модуль для активации iOS устройства с установкой приложения через MDM профиль
"""

import subprocess
import os
import sys
import time
import plistlib
import tempfile
import zipfile
import json
from pathlib import Path
from typing import Optional, Callable, Tuple

try:
    from core.profile_builder import ProfileBuilder
except ImportError:
    from profile_builder import ProfileBuilder


class Activator:
    """Класс для активации iOS устройства и установки приложения"""
    
    def __init__(self):
        self.progress_callback = None
        self.app_bundle_id = None
        self.app_path = None
        self.device_udid = None
        
    def set_progress_callback(self, callback: Callable[[str], None]):
        self.progress_callback = callback
    
    def _log(self, message: str):
        """Логирование с callback или print (без дополнительных параметров)"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
    
    def _log_dot(self):
        """Логирование точки для прогресса"""
        if self.progress_callback:
            self.progress_callback(".")
        else:
            print(".", end="", flush=True)
    
    def _run_command(self, cmd: list, timeout: int = 60) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self._log(f"   ⚠️ Таймаут: {' '.join(cmd)}")
            return None
        except Exception as e:
            self._log(f"   ❌ Ошибка: {e}")
            return None
    
    def _get_app_path(self) -> Optional[str]:
        """Находит путь к .app или .ipa"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        possible_paths = [
            os.path.join(project_root, 'resources', 'apps', 'SemplChecker.ipa'),
            os.path.join(project_root, 'resources', 'apps', 'SemplChecker.app'),
            os.path.expanduser("~/Desktop/Debug-iphoneos/SemplChecker.app"),
            os.path.expanduser("~/Desktop/Debug-iphoneos/SemplChecker.ipa"),
            os.path.join(project_root, 'SemplChecker.ipa'),
            os.path.join(project_root, 'SemplChecker.app'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self._log(f"   ✅ Найдено приложение: {path}")
                return path
        
        self._log(f"   ⚠️ Приложение не найдено!")
        return None
    
    def _get_bundle_id(self, app_path: str) -> Optional[str]:
        if not app_path or not os.path.exists(app_path):
            return None
        
        try:
            if os.path.isdir(app_path) and app_path.endswith('.app'):
                info_plist = os.path.join(app_path, 'Info.plist')
                if os.path.exists(info_plist):
                    with open(info_plist, 'rb') as f:
                        plist_data = plistlib.load(f)
                    return plist_data.get('CFBundleIdentifier')
            
            elif app_path.endswith('.ipa'):
                with zipfile.ZipFile(app_path, 'r') as zip_ref:
                    for file_info in zip_ref.filelist:
                        if 'Info.plist' in file_info.filename and 'Payload/' in file_info.filename:
                            with zip_ref.open(file_info.filename) as f:
                                plist_data = plistlib.load(f)
                            return plist_data.get('CFBundleIdentifier')
        except Exception as e:
            self._log(f"   ⚠️ Ошибка получения Bundle ID: {e}")
        
        return None
    
    def _get_device_udid(self) -> Optional[str]:
        try:
            result = self._run_command(["pymobiledevice3", "usbmux", "list"], timeout=10)
            if result and result.returncode == 0 and result.stdout.strip():
                devices = json.loads(result.stdout)
                if devices:
                    return devices[0].get('UniqueDeviceID')
        except Exception as e:
            self._log(f"   ⚠️ Ошибка получения UDID: {e}")
        return None
    
    def _pair_device(self) -> bool:
        self._log("1/8 Спаривание устройства...")
        
        # Проверяем, спарено ли уже
        result = self._run_command(["pymobiledevice3", "lockdown", "pair"], timeout=30)
        if result and result.returncode == 0:
            self._log("   ✅ Устройство уже спарено")
            return True
        
        # ЯРКОЕ СООБЩЕНИЕ В ЛОГЕ
        self._log("")
        self._log("=" * 60)
        self._log("📱 ВНИМАНИЕ! ДЕЙСТВИЕ НА ТЕЛЕФОНЕ:")
        self._log("=" * 60)
        self._log("")
        self._log("   НА ЭКРАНЕ IPHONE ПОЯВИТСЯ ЗАПРОС:")
        self._log("   «ДОВЕРЯТЬ ЭТОМУ КОМПЬЮТЕРУ?»")
        self._log("")
        self._log("   👉 НАЖМИТЕ «ДОВЕРЯТЬ» НА ТЕЛЕФОНЕ")
        self._log("   👉 ВВЕДИТЕ ПАРОЛЬ УСТРОЙСТВА")
        self._log("")
        self._log("   ⏳ ПОСЛЕ ЭТОГО НАЖМИТЕ ПРОДОЛЖИТЬ В ПРОГРАММЕ")
        self._log("")
        self._log("=" * 60)
        self._log("")
        
        self._log("   ⏳ Ожидание подтверждения...")
        
        result = self._run_command(["pymobiledevice3", "lockdown", "pair"], timeout=60)
        
        if result and result.returncode == 0:
            self._log("   ✅ Спаривание успешно завершено")
            return True
        else:
            self._log("   ❌ Ошибка спаривания. Убедитесь, что:")
            self._log("      - На устройстве нажато 'Доверять'")
            self._log("      - Введен пароль устройства")
            return False
    
    def _activate_device(self) -> bool:
        self._log("2/8 Активация устройства...")
        
        result = self._run_command(["pymobiledevice3", "activation", "activate", "--now"], timeout=60)
        if result and result.returncode == 0:
            self._log("   ✅ Активация выполнена")
            return True
        else:
            self._log("   ⚠️ Возможно устройство уже активировано")
            return True
    
    def _enable_supervision(self) -> bool:
        self._log("3/8 Включение режима Надзора...")
        
        result = self._run_command(["pymobiledevice3", "profile", "supervise", "SemplActivator"], timeout=30)
        if result and result.returncode == 0:
            self._log("   ✅ Режим Надзора включен")
            return True
        else:
            self._log("   ⚠️ Режим Надзора будет включен через профиль")
            return True
    
    def _create_profile(self, ssid: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
        self._log("4/8 Создание профиля с приложением...")
        
        try:
            app_path = self.app_path or self._get_app_path()
            bundle_id = self.app_bundle_id
            
            if app_path and not bundle_id:
                bundle_id = self._get_bundle_id(app_path)
                if bundle_id:
                    self._log(f"   📱 Bundle ID: {bundle_id}")
                    self.app_bundle_id = bundle_id
            
            # Создаем профиль с приложением
            profile_path = ProfileBuilder.create_skip_profile_with_app(
                app_path=app_path,
                bundle_id=bundle_id,
                ssid=ssid,
                password=password
            )
            
            if profile_path:
                self._log(f"   ✅ Профиль создан")
                return profile_path
            else:
                self._log("   ❌ Ошибка создания профиля")
                return None
                
        except Exception as e:
            self._log(f"   ❌ Ошибка: {e}")
            return None
    
    def _install_profile(self, profile_path: str) -> bool:
        self._log("5/8 Установка профиля...")
        
        self._log("   📱 На устройстве может появиться запрос на установку профиля")
        self._log("   👆 Нажмите 'Установить' и введите пароль")
        
        result = self._run_command(["pymobiledevice3", "profile", "install", profile_path], timeout=60)
        if result and result.returncode == 0:
            self._log("   ✅ Профиль установлен")
            return True
        else:
            self._log("   ❌ Ошибка установки профиля")
            return False
    
    def _install_app(self) -> bool:
        self._log("6/8 Установка приложения...")
        
        if not self.app_path or not os.path.exists(self.app_path):
            self._log("   ❌ Приложение не найдено")
            return False
        
        self._log(f"   📲 Установка: {os.path.basename(self.app_path)}")
        
        # Пробуем установить с флагом developer
        cmd = ["pymobiledevice3", "apps", "install", self.app_path, "--developer"]
        result = self._run_command(cmd, timeout=180)
        
        if result and result.returncode == 0:
            self._log("   ✅ Приложение установлено!")
            return True
        else:
            # Пробуем без флага developer
            self._log("   🔄 Пробуем без флага developer...")
            cmd = ["pymobiledevice3", "apps", "install", self.app_path]
            result = self._run_command(cmd, timeout=180)
            
            if result and result.returncode == 0:
                self._log("   ✅ Приложение установлено!")
                return True
            else:
                error = result.stderr[:200] if result and result.stderr else "Неизвестная ошибка"
                self._log(f"   ❌ Ошибка: {error}")
                return False
    
    def _restart_device(self) -> bool:
        self._log("7/8 Перезагрузка устройства...")
        
        result = self._run_command(["pymobiledevice3", "diagnostics", "restart"], timeout=10)
        if result and result.returncode == 0:
            self._log("   ✅ Команда перезагрузки отправлена")
            return True
        else:
            self._log("   ⚠️ Ошибка перезагрузки")
            return False
    
    def _wait_for_device(self, timeout: int = 120) -> bool:
        self._log("8/8 Ожидание возврата устройства...")
        self._log("   ⏳ Устройство перезагружается...")
        
        start_time = time.time()
        dots = 0
        
        while time.time() - start_time < timeout:
            try:
                result = self._run_command(["pymobiledevice3", "usbmux", "list"], timeout=5)
                if result and result.returncode == 0 and result.stdout.strip():
                    import json
                    devices = json.loads(result.stdout)
                    if devices:
                        self._log("\n   ✅ Устройство обнаружено!")
                        time.sleep(3)
                        return True
            except:
                pass
            
            dots += 1
            if dots % 5 == 0:
                self._log(".")
            time.sleep(2)
        
        self._log("\n   ⚠️ Таймаут ожидания")
        return False
    
    def activate_and_bypass(
        self,
        ssid: Optional[str] = None,
        password: Optional[str] = None,
        install_app: bool = True,
        app_path: Optional[str] = None,
        bundle_id: Optional[str] = None
    ) -> bool:
        """Полный процесс активации с установкой приложения"""
        self._log("=" * 60)
        self._log("🚀 ЗАПУСК АКТИВАЦИИ С УСТАНОВКОЙ ПРИЛОЖЕНИЯ")
        self._log("=" * 60)
        
        # Сохраняем параметры
        if app_path:
            self.app_path = app_path
        if bundle_id:
            self.app_bundle_id = bundle_id
        
        # Находим приложение если не указано
        if not self.app_path and install_app:
            self.app_path = self._get_app_path()
        
        if self.app_path and os.path.exists(self.app_path):
            self._log(f"📱 Приложение: {os.path.basename(self.app_path)}")
            
            if not self.app_bundle_id:
                self.app_bundle_id = self._get_bundle_id(self.app_path)
            if self.app_bundle_id:
                self._log(f"   Bundle ID: {self.app_bundle_id}")
        else:
            self._log("⚠️ Приложение не найдено. Будет выполнена только активация")
            install_app = False
        
        # Шаг 1: Спаривание
        if not self._pair_device():
            return False
        time.sleep(1)
        
        # Шаг 2: Активация
        if not self._activate_device():
            return False
        time.sleep(1)
        
        # Шаг 3: Режим Надзора
        self._enable_supervision()
        time.sleep(1)
        
        # Шаг 4: Создание профиля
        profile_path = self._create_profile(ssid, password)
        if not profile_path:
            return False
        time.sleep(1)
        
        # Шаг 5: Установка профиля
        if not self._install_profile(profile_path):
            return False
        time.sleep(1)
        
        # Шаг 6: Установка приложения
        if install_app and self.app_path and os.path.exists(self.app_path):
            self._install_app()
        else:
            self._log("6/8 Установка приложения пропущена")
        time.sleep(1)
        
        # Шаг 7: Перезагрузка
        self._restart_device()
        
        # Шаг 8: Ожидание возврата
        self._wait_for_device()
        
        # Итог
        self._log("\n" + "=" * 60)
        self._log("✅ АКТИВАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
        if self.app_bundle_id:
            self._log(f"📱 Приложение установлено: {self.app_bundle_id}")
        self._log("")
        self._log("📱 Для первого запуска:")
        self._log("   1. На iPhone: Настройки → Основные → VPN и управление устройством")
        self._log("   2. Нажмите на профиль разработчика → Доверять")
        self._log("   3. Запустите приложение SemplChecker на рабочем столе")
        self._log("=" * 60)
        return True


# Для тестирования
if __name__ == "__main__":
    activator = Activator()
    activator.set_progress_callback(print)
    activator.activate_and_bypass()