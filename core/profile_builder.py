"""Модуль для создания MDM профилей"""
import tempfile
import uuid
from pathlib import Path
from typing import Optional

class ProfileBuilder:
    @staticmethod
    def create_skip_profile(ssid: Optional[str] = None, password: Optional[str] = None) -> str:
        profile_uuid = str(uuid.uuid4())
        wifi_uuid = str(uuid.uuid4())
        profile_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
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
            <string>{profile_uuid}</string>
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
        </dict>'''
        if ssid and ssid.strip():
            profile_xml += f'''
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
        profile_xml += '''
    </array>
    <key>PayloadDescription</key>
    <string>Automatically skips Setup Assistant screens</string>
    <key>PayloadDisplayName</key>
    <string>Activator Bypass Profile</string>
    <key>PayloadIdentifier</key>
    <string>com.activator.root</string>
    <key>PayloadOrganization</key>
    <string>Activator</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>root-uuid</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>'''
        temp_dir = tempfile.gettempdir()
        profile_path = Path(temp_dir) / "activator_bypass.mobileconfig"
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(profile_xml)
        return str(profile_path)
