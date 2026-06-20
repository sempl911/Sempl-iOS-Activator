# ui/main_window.py

import threading
import subprocess
import os
import json
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QGridLayout, QMessageBox, QProgressBar,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer


class UpdateSignals(QObject):
    device_info = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    activation_complete = pyqtSignal(bool, str)
    progress_update = pyqtSignal(int, str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_manager = None
        self.activator = None
        self.signals = UpdateSignals()
        self.is_activating = False
        self.device_ready = False
        self.last_connected = False
        self.app_bundle_id = "SemplDev.SemplChecker"
        self.progress_max = 7
        
        # Путь к .ipa внутри программы
        self.ipa_path = self._get_ipa_path()
        
        self.setup_ui()
        self.setup_signals()
        self.init_backend()
        self.start_device_monitoring()
        
        # Автоматическая проверка устройства при запуске
        QTimer.singleShot(1000, self.check_device_status)
    
    def _get_ipa_path(self) -> str:
        """Находит путь к .ipa внутри ресурсов"""
        import sys
        import os
        
        # Если запущено как exe/app
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            ipa_path = os.path.join(base_path, 'resources', 'apps', 'SemplChecker.ipa')
            if os.path.exists(ipa_path):
                return ipa_path
        
        # В режиме разработки
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ipa_path = os.path.join(project_root, 'resources', 'apps', 'SemplChecker.ipa')
        if os.path.exists(ipa_path):
            return ipa_path
        
        return None
    
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
        self.signals.progress_update.connect(self.update_progress)
    
    def setup_ui(self):
        self.setWindowTitle("Sempl Activator Pro")
        self.setMinimumSize(600, 700)
        self.setFixedSize(650, 750)
        
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
                padding: 10px 20px; 
                border-radius: 4px; 
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:disabled { background-color: #3c3c3c; color: #6c6c6c; }
            QPushButton#btn_activate {
                background-color: #4CAF50;
                font-size: 16px;
                padding: 12px 24px;
            }
            QPushButton#btn_activate:hover { background-color: #45a049; }
            QPushButton#btn_activate:disabled { background-color: #3c3c3c; color: #6c6c6c; }
            QTextEdit { 
                background-color: #252526; 
                color: #4ec9b0; 
                border: 1px solid #3c3c3c; 
                border-radius: 4px; 
                font-family: monospace;
                font-size: 11px;
            }
            QProgressBar { 
                border: 1px solid #3c3c3c; 
                border-radius: 4px; 
                text-align: center; 
                color: #cccccc;
                background-color: #252526;
            }
            QProgressBar::chunk { background-color: #0078d4; border-radius: 4px; }
            QFrame#status_frame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title = QLabel("Sempl Activator Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin: 10px;")
        layout.addWidget(title)
        
        # Статусная панель
        status_frame = QFrame()
        status_frame.setObjectName("status_frame")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_icon = QLabel("🔴")
        self.status_icon.setStyleSheet("font-size: 18px;")
        self.status_text = QLabel("Ожидание подключения iPhone...")
        self.status_text.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.status_detail = QLabel("")
        self.status_detail.setStyleSheet("font-size: 11px; color: #888888;")
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        status_layout.addWidget(self.status_detail)
        layout.addWidget(status_frame)
        
        # Группа информации об устройстве
        info_group = QGroupBox("📱 Информация об устройстве")
        info_layout = QGridLayout()
        info_layout.setSpacing(6)
        
        self.lbl_model = QLabel("Модель: —")
        self.lbl_ios = QLabel("iOS версия: —")
        self.lbl_serial = QLabel("Серийный номер: —")
        self.lbl_imei = QLabel("IMEI: —")  # 👈 НОВОЕ ПОЛЕ
        self.lbl_activation = QLabel("Статус: —")
        
        info_layout.addWidget(self.lbl_model, 0, 0)
        info_layout.addWidget(self.lbl_ios, 0, 1)
        info_layout.addWidget(self.lbl_serial, 1, 0)
        info_layout.addWidget(self.lbl_imei, 1, 1)  # 👈 НОВОЕ ПОЛЕ
        info_layout.addWidget(self.lbl_activation, 2, 0, 1, 2)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Группа активации (только кнопка)
        activation_group = QGroupBox("🚀 Активация")
        activation_layout = QVBoxLayout()
        activation_layout.setSpacing(10)
        
        self.btn_activate = QPushButton("▶️ СТАРТ АКТИВАЦИИ")
        self.btn_activate.setObjectName("btn_activate")
        self.btn_activate.setMinimumHeight(50)
        self.btn_activate.setEnabled(False)
        self.btn_activate.clicked.connect(self.start_activation)
        
        activation_layout.addWidget(self.btn_activate)
        
        # Прогресс
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(25)
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        self.progress_label.setVisible(False)
        
        activation_layout.addWidget(self.progress)
        activation_layout.addWidget(self.progress_label)
        
        activation_group.setLayout(activation_layout)
        layout.addWidget(activation_group)
        
        # Лог
        log_group = QGroupBox("📋 Лог операций")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        
        clear_btn = QPushButton("🗑️ Очистить лог")
        clear_btn.setMaximumWidth(120)
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
    
    def update_progress(self, step: int, message: str):
        self.progress.setValue(int((step / self.progress_max) * 100))
        self.progress_label.setText(f"Шаг {step}/{self.progress_max}: {message}")
    
    def start_device_monitoring(self):
        def monitor():
            import time
            while True:
                if self.device_manager:
                    try:
                        connected = self.device_manager.is_device_connected()
                        
                        if connected != self.last_connected:
                            self.last_connected = connected
                            if not connected:
                                self.signals.device_info.emit({"connected": False})
                        
                        if connected and not self.is_activating:
                            info = self.device_manager.get_device_info()
                            if info:
                                self.signals.device_info.emit(info)
                    except:
                        pass
                time.sleep(2)
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_device_info(self, info):
        if info.get("connected"):
            self.status_text.setText("✅ Устройство подключено")
            self.status_icon.setText("🟢")
            self.status_detail.setText(f"{info.get('device_name', 'iPhone')}")
            
            self.lbl_model.setText(f"Модель: {info.get('model', '—')}")
            self.lbl_ios.setText(f"iOS версия: {info.get('ios_version', '—')}")
            self.lbl_serial.setText(f"Серийный номер: {info.get('serial', '—')}")
            
            # 👇 НОВОЕ: отображение IMEI
            imei = info.get('imei', '—')
            if imei and imei != '—':
                self.lbl_imei.setText(f"IMEI: {imei}")
                self.lbl_imei.setStyleSheet("color: #4ec9b0;")
            else:
                self.lbl_imei.setText("IMEI: —")
                self.lbl_imei.setStyleSheet("color: #888888;")
            
            activation = info.get('activation_state', 'Unknown')
            if activation == "Activated":
                self.lbl_activation.setText("Статус: ✅ Активирован")
                self.lbl_activation.setStyleSheet("color: #4ec9b0;")
                self.device_ready = True
            else:
                self.lbl_activation.setText("Статус: ⚠️ Не активирован")
                self.lbl_activation.setStyleSheet("color: #dcdcaa;")
                self.device_ready = False
            
            self.btn_activate.setEnabled(True)
        else:
            self.device_ready = False
            self.status_text.setText("🔌 Устройство отключено")
            self.status_icon.setText("🔴")
            self.status_detail.setText("Подключите iPhone")
            
            self.lbl_model.setText("Модель: —")
            self.lbl_ios.setText("iOS версия: —")
            self.lbl_serial.setText("Серийный номер: —")
            self.lbl_imei.setText("IMEI: —")  # 👈 Очищаем при отключении
            self.lbl_imei.setStyleSheet("")
            self.lbl_activation.setText("Статус: —")
            self.lbl_activation.setStyleSheet("")
            
            self.btn_activate.setEnabled(False)
    
    def check_device_status(self):
        """Проверка статуса устройства"""
        if self.device_manager:
            info = self.device_manager.get_device_info()
            if info and info.get("connected"):
                self.update_device_info(info)
    
    def start_activation(self):
        if not self.device_manager.is_device_connected():
            QMessageBox.warning(self, "Ошибка", "iPhone не подключен!")
            return
        
        if not self.ipa_path or not os.path.exists(self.ipa_path):
            self.append_log("❌ Приложение не найдено в ресурсах!")
            QMessageBox.critical(self, "Ошибка", "Файл приложения не найден!\nОжидается: resources/apps/SemplChecker.ipa")
            return
        
        self.is_activating = True
        self.btn_activate.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_label.setVisible(True)
        
        self.append_log("🚀 Запуск активации с установкой приложения...")
        self.append_log(f"📱 Приложение: {os.path.basename(self.ipa_path)}")
        
        def run():
            try:
                success = self.activator.activate_and_bypass(
                    ssid=None,
                    password=None,
                    install_app=True,
                    app_path=self.ipa_path,
                    bundle_id=self.app_bundle_id
                )
                self.signals.activation_complete.emit(success, "✅ Активация завершена!" if success else "❌ Ошибка активации")
            except Exception as e:
                self.signals.log_message.emit(f"❌ Критическая ошибка: {e}")
                self.signals.activation_complete.emit(False, f"❌ Ошибка: {e}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def on_activation_progress(self, msg):
        self.signals.log_message.emit(msg)
        
        # Обновляем прогресс на основе сообщения
        if "1/" in msg:
            self.signals.progress_update.emit(1, "Спаривание")
        elif "2/" in msg:
            self.signals.progress_update.emit(2, "Активация")
        elif "3/" in msg:
            self.signals.progress_update.emit(3, "Режим Надзора")
        elif "4/" in msg:
            self.signals.progress_update.emit(4, "Создание профиля")
        elif "5/" in msg:
            self.signals.progress_update.emit(5, "Установка профиля")
        elif "6/" in msg:
            self.signals.progress_update.emit(6, "Установка приложения")
        elif "7/" in msg:
            self.signals.progress_update.emit(7, "Перезагрузка")
    
    def append_log(self, msg):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_activation_complete(self, success, msg):
        self.is_activating = False
        self.progress.setVisible(False)
        self.progress_label.setVisible(False)
        self.btn_activate.setEnabled(True)
        
        if success:
            self.status_text.setText("✅ Активация завершена!")
            self.status_icon.setText("🟢")
            self.device_ready = True
            self.append_log("")
            self.append_log("📱 Инструкция для первого запуска:")
            self.append_log("   На iPhone: Настройки → Основные → VPN и управление устройством")
            self.append_log("   Нажмите на профиль разработчика → Доверять")
            self.append_log("   Затем запустите приложение SemplChecker на рабочем столе")
        else:
            self.status_text.setText("❌ Ошибка активации")
            self.status_icon.setText("🔴")
        
        QMessageBox.information(self, "Результат", msg)