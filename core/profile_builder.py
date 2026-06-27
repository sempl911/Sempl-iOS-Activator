"""Модуль для создания MDM профилей с установкой приложения"""
import tempfile
import uuid
import os
import plistlib
import zipfile
import base64
from pathlib import Path
from typing import Optional


class ProfileBuilder:
    
    @staticmethod
    def create_skip_profile_with_app(
        app_path: Optional[str] = None,
        bundle_id: Optional[str] = None,
        ssid: Optional[str] = None,
        password: Optional[str] = None
    ) -> str:
        """
        Создает MDM профиль с пропуском экранов настройки и установкой приложения
        
        Args:
            app_path: Путь к .app или .ipa файлу
            bundle_id: Bundle ID приложения (если не указан, будет извлечен из .app)
            ssid: Имя Wi-Fi сети (опционально)
            password: Пароль Wi-Fi (опционально)
        
        Returns:
            str: Путь к созданному профилю
        """
        # Генерируем UUID
        skip_uuid = str(uuid.uuid4())
        wifi_uuid = str(uuid.uuid4())
        app_uuid = str(uuid.uuid4())
        restrictions_uuid = str(uuid.uuid4())
        
        # Определяем Bundle ID
        if bundle_id is None and app_path:
            bundle_id = ProfileBuilder._get_bundle_id(app_path)
        
        if not bundle_id:
            bundle_id = "SemplDev.SemplChecker"  # Fallback
        
        # Начинаем формирование профиля
        profile_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <!-- 1. Пропуск экранов настройки -->
        <dict>
            <key>PayloadDescription</key>
            <string>Skips Setup Assistant screens</string>
            <key>PayloadDisplayName</key>
            <string>Setup Bypass</string>
            <key>PayloadIdentifier</key>
            <string>com.activator.bypass</string>
            <key>PayloadType</key>
            <string>com.apple.configurationprofiles.skip-setup-assistant</string>
            <key>PayloadUUID</key>
            <string>{skip_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>SkipSetupItems</key>
            <array>
                <string>AppleID</string>
                <string>Location</string>
                <string>Passcode</string>
                <string>Siri</string>
                <string>ScreenTime</string>
                <string>Diagnostics</string>
                <string>Payment</string>
                <string>Zoom</string>
                <string>Appearance</string>
                <string>RestoreCompleted</string>
                <string>SoftwareUpdate</string>
                <string>SIMSetup</string>
                <string>TermsOfAddress</string>
                <string>Watch</string>
            </array>
        </dict>
        
        <!-- 2. Установка управляемого приложения -->
        <dict>
            <key>PayloadDescription</key>
            <string>Installs managed application</string>
            <key>PayloadDisplayName</key>
            <string>SemplChecker App</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.mdm.managedapp</string>
            <key>PayloadType</key>
            <string>com.apple.mdm.managedapp</string>
            <key>PayloadUUID</key>
            <string>{app_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>AppID</key>
            <string>{bundle_id}</string>
            <key>AppName</key>
            <string>SemplChecker</string>
            <key>InstallAsManaged</key>
            <true/>
            <key>RemoveAppWhenProfileIsRemoved</key>
            <true/>
            <key>ManagementFlags</key>
            <integer>1</integer>
            <key>Signing</key>
            <dict>
                <key>AllowAdHocSigning</key>
                <true/>
                <key>AllowDevelopmentSigning</key>
                <true/>
            </dict>
        </dict>
        
        <!-- 3. Отключение ограничений для тестирования -->
        <dict>
            <key>PayloadDescription</key>
            <string>Disable restrictions for testing</string>
            <key>PayloadDisplayName</key>
            <string>Testing Mode</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.applicationaccess</string>
            <key>PayloadType</key>
            <string>com.apple.applicationaccess</string>
            <key>PayloadUUID</key>
            <string>{restrictions_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>allowAppInstallation</key>
            <true/>
            <key>allowAppRemoval</key>
            <true/>
            <key>allowCamera</key>
            <true/>
            <key>allowSiri</key>
            <true/>
            <key>allowUntrustedTLSPrompt</key>
            <true/>
            <key>allowUIConfigurationProfileInstallation</key>
            <true/>
            <key>allowPasscodeModification</key>
            <true/>
            <key>allowDeviceNameModification</key>
            <true/>
            <key>allowWallpaperModification</key>
            <true/>
        </dict>'''
        
        # 4. Добавляем Wi-Fi если указан
        if ssid and ssid.strip():
            wifi_uuid = str(uuid.uuid4())
            profile_xml += f'''
        
        <!-- 4. Wi-Fi настройки -->
        <dict>
            <key>PayloadDisplayName</key>
            <string>Wi-Fi Settings</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.wifi.managed</string>
            <key>PayloadType</key>
            <string>com.apple.wifi.managed</string>
            <key>PayloadUUID</key>
            <string>{wifi_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>SSID</key>
            <string>{ssid}</string>
            <key>EncryptionType</key>
            <string>WPA2</string>
            <key>AutoJoin</key>
            <true/>'''
            if password and password.strip():
                profile_xml += f'\n            <key>Password</key>\n            <string>{password}</string>'
            profile_xml += '\n            <key>HiddenNetwork</key>\n            <false/>\n        </dict>'
        
        # Закрываем профиль
        profile_xml += '''
    </array>
    <key>PayloadDescription</key>
    <string>Activator profile with app installation</string>
    <key>PayloadDisplayName</key>
    <string>Sempl Activator + App</string>
    <key>PayloadIdentifier</key>
    <string>com.activator.root</string>
    <key>PayloadOrganization</key>
    <string>Sempl Activator</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>''' + str(uuid.uuid4()) + '''</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>'''
        
        # Сохраняем профиль
        temp_dir = tempfile.gettempdir()
        profile_path = Path(temp_dir) / "activator_with_app.mobileconfig"
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(profile_xml)
        
        return str(profile_path)
    
    @staticmethod
    def _get_bundle_id(app_path: str) -> Optional[str]:
        """Извлекает Bundle ID из .app или .ipa"""
        if not app_path or not os.path.exists(app_path):
            return None
        
        try:
            # Если это .app папка
            if os.path.isdir(app_path) and app_path.endswith('.app'):
                info_plist = os.path.join(app_path, 'Info.plist')
                if os.path.exists(info_plist):
                    with open(info_plist, 'rb') as f:
                        plist_data = plistlib.load(f)
                    return plist_data.get('CFBundleIdentifier')
            
            # Если это .ipa файл
            elif app_path.endswith('.ipa'):
                import zipfile
                with zipfile.ZipFile(app_path, 'r') as zip_ref:
                    # Ищем Info.plist в Payload/*.app/
                    for file_info in zip_ref.filelist:
                        if 'Info.plist' in file_info.filename and 'Payload/' in file_info.filename:
                            with zip_ref.open(file_info.filename) as f:
                                plist_data = plistlib.load(f)
                            return plist_data.get('CFBundleIdentifier')
        except Exception as e:
            print(f"⚠️ Не удалось определить Bundle ID: {e}")
        
        return None
    
    @staticmethod
    def create_skip_profile(ssid: Optional[str] = None, password: Optional[str] = None) -> str:
        """Оригинальный метод для обратной совместимости"""
        return ProfileBuilder.create_skip_profile_with_app(
            app_path=None,
            bundle_id=None,
            ssid=ssid,
            password=password
        )


# Для тестирования
if __name__ == "__main__":
    # Пример использования
    app_path = "/Users/aleksejkustov/Desktop/Sempl iOS Activator/resources/apps/SemplChecker.ipa"
    
    profile_path = ProfileBuilder.create_skip_profile_with_app(
        app_path=app_path,
        bundle_id="SemplDev.SemplChecker",
        ssid="MyWiFi",
        password="123456"
    )
    
    print(f"✅ Профиль создан: {profile_path}")