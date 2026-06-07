"""Модуль для работы с подключенным iPhone"""
import subprocess
import json
from typing import Optional, Dict

class DeviceManager:
    def __init__(self):
        self.device_info = {}
    
    def get_device_info(self) -> Optional[Dict]:
        try:
            result = subprocess.run(
                ["pymobiledevice3", "lockdown", "info"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return None
            data = json.loads(result.stdout)
            nvram = data.get("NonVolatileRAM", {})
            fm_lock = str(nvram.get("fm-activation-locked", ""))
            info = {
                "serial": data.get("SerialNumber"),
                "imei": data.get("InternationalMobileEquipmentIdentity"),
                "model": data.get("ProductType"),
                "ios_version": data.get("ProductVersion"),
                "device_name": data.get("DeviceName"),
                "activation_state": data.get("ActivationState"),
                "connected": True,
                "icloud_lock": "NO" if ("NO" in fm_lock or "4e4f" in fm_lock.lower()) else "YES" if ("YES" in fm_lock or "594553" in fm_lock) else "UNKNOWN"
            }
            self.device_info = info
            return info
        except:
            return None
    
    def is_device_connected(self) -> bool:
        try:
            result = subprocess.run(
                ["pymobiledevice3", "usbmux", "list"],
                capture_output=True, text=True, timeout=5
            )
            return "Lockdown" in result.stdout or "iPhone" in result.stdout
        except:
            return False
