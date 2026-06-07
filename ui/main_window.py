import threading
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QGridLayout, QLineEdit, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class UpdateSignals(QObject):
    device_info = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    activation_complete = pyqtSignal(bool, str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_manager = None
        self.activator = None
        self.signals = UpdateSignals()
        self.is_activating = False
        self.setup_ui()
        self.setup_signals()
        self.init_backend()
        self.start_device_monitoring()
    
    def init_backend(self):
        from core.device_manager import DeviceManager
        from core.activator import Activator
        self.device_manager = DeviceManager()
        self.activator = Activator()
        self.activator.set_progress_callback(self.on_activation_progress)
    
    def setup_signals(self):
        self.signals.device_info.connect(self.update_device_info)
        self.signals.log_message.connect(self.append_log)
        self.signals.activation_complete.connect(self.on_activation_complete)
    
    def setup_ui(self):
        self.setWindowTitle("Sempl Activator Pro")
        self.setMinimumSize(650, 550)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #cccccc; }
            QGroupBox { 
                color: #ffffff;
                border: 1px solid #3c3c3c; 
                border-radius: 6px; 
                margin-top: 12px; 
                font-weight: bold;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 12px; 
                padding: 0 6px;
            }
            QPushButton { 
                background-color: #0078d4; 
                color: white; 
                border: none; 
                padding: 8px 20px; 
                border-radius: 4px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #106ebe; 
            }
            QPushButton:disabled { 
                background-color: #3c3c3c; 
                color: #6c6c6c;
            }
            QTextEdit { 
                background-color: #252526; 
                color: #4ec9b0; 
                border: 1px solid #3c3c3c; 
                border-radius: 4px; 
                font-family: monospace;
                font-size: 11px;
            }
            QLineEdit { 
                background-color: #3c3c3c; 
                color: #cccccc; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 6px;
            }
            QLineEdit:focus { 
                border: 1px solid #0078d4; 
            }
            QProgressBar { 
                border: 1px solid #3c3c3c; 
                border-radius: 4px; 
                text-align: center; 
                color: #cccccc;
                background-color: #252526;
            }
            QProgressBar::chunk { 
                background-color: #0078d4; 
                border-radius: 4px;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        title = QLabel("Sempl Activator Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff; margin: 8px;")
        layout.addWidget(title)
        
        info_group = QGroupBox("📱 Информация об устройстве")
        info_layout = QGridLayout()
        self.lbl_status = QLabel("Статус: 🔌 Ожидание подключения...")
        self.lbl_serial = QLabel("Серийный номер: —")
        self.lbl_imei = QLabel("IMEI: —")
        self.lbl_model = QLabel("Модель: —")
        self.lbl_ios = QLabel("iOS версия: —")
        self.lbl_icloud = QLabel("iCloud Lock: —")
        info_layout.addWidget(self.lbl_status, 0, 0, 1, 2)
        info_layout.addWidget(self.lbl_serial, 1, 0)
        info_layout.addWidget(self.lbl_imei, 1, 1)
        info_layout.addWidget(self.lbl_model, 2, 0)
        info_layout.addWidget(self.lbl_ios, 2, 1)
        info_layout.addWidget(self.lbl_icloud, 3, 0, 1, 2)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        wifi_group = QGroupBox("🌐 Wi-Fi (опционально)")
        wifi_layout = QGridLayout()
        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setPlaceholderText("Имя сети (SSID)")
        self.wifi_password = QLineEdit()
        self.wifi_password.setPlaceholderText("Пароль")
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        wifi_layout.addWidget(QLabel("SSID:"), 0, 0)
        wifi_layout.addWidget(self.wifi_ssid, 0, 1)
        wifi_layout.addWidget(QLabel("Пароль:"), 1, 0)
        wifi_layout.addWidget(self.wifi_password, 1, 1)
        wifi_group.setLayout(wifi_layout)
        layout.addWidget(wifi_group)
        
        self.btn_activate = QPushButton("🚀 Активировать и пропустить настройку")
        self.btn_activate.setEnabled(False)
        self.btn_activate.clicked.connect(self.start_activation)
        layout.addWidget(self.btn_activate)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        log_group = QGroupBox("📋 Лог операций")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
    
    def start_device_monitoring(self):
        def monitor():
            import time
            while True:
                if self.device_manager:
                    try:
                        connected = self.device_manager.is_device_connected()
                        if connected and not self.is_activating:
                            info = self.device_manager.get_device_info()
                            if info:
                                self.signals.device_info.emit(info)
                        elif not connected:
                            self.signals.device_info.emit({"connected": False})
                    except:
                        pass
                time.sleep(2)
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_device_info(self, info):
        if info.get("connected"):
            self.lbl_status.setText("Статус: ✅ Устройство подключено")
            self.lbl_serial.setText(f"Серийный номер: {info.get('serial', '—')}")
            self.lbl_imei.setText(f"IMEI: {info.get('imei', '—')}")
            self.lbl_model.setText(f"Модель: {info.get('model', '—')}")
            self.lbl_ios.setText(f"iOS версия: {info.get('ios_version', '—')}")
            icloud = info.get('icloud_lock', 'UNKNOWN')
            if icloud == 'NO':
                self.lbl_icloud.setText("iCloud Lock: ✅ НЕТ (чисто)")
                self.lbl_icloud.setStyleSheet("color: #4ec9b0;")
            elif icloud == 'YES':
                self.lbl_icloud.setText("iCloud Lock: ❌ ЕСТЬ (заблокирован)")
                self.lbl_icloud.setStyleSheet("color: #f14c4c;")
            else:
                self.lbl_icloud.setText("iCloud Lock: ⚠️ Неизвестно")
                self.lbl_icloud.setStyleSheet("color: #dcdcaa;")
            self.btn_activate.setEnabled(True)
        else:
            self.lbl_status.setText("Статус: 🔌 Ожидание подключения...")
            self.btn_activate.setEnabled(False)
    
    def start_activation(self):
        self.is_activating = True
        self.btn_activate.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        ssid = self.wifi_ssid.text().strip()
        password = self.wifi_password.text().strip()
        
        def run():
            success = self.activator.activate_and_bypass(ssid, password)
            self.signals.activation_complete.emit(success, "Устройство активировано! После перезагрузки вы попадете на рабочий стол." if success else "Ошибка активации")
        
        threading.Thread(target=run, daemon=True).start()
    
    def on_activation_progress(self, msg):
        self.signals.log_message.emit(msg)
    
    def append_log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def on_activation_complete(self, success, msg):
        self.is_activating = False
        self.progress.setVisible(False)
        self.btn_activate.setEnabled(True)
        (QMessageBox.information if success else QMessageBox.critical)(self, "Sempl Activator Pro", msg)
