#!/usr/bin/env python3
# test_activation.py - полный тест активации

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.activator import Activator


def main():
    print("=" * 60)
    print("🧪 ТЕСТ АКТИВАЦИИ С УСТАНОВКОЙ ПРИЛОЖЕНИЯ")
    print("=" * 60)
    print()
    
    print("📋 Инструкция:")
    print("1. iPhone должен быть сброшен до заводских настроек")
    print("2. iPhone должен быть подключен к Mac USB-кабелем")
    print("3. На iPhone должен гореть экран 'Привет' (Hello)")
    print()
    
    input("Нажмите Enter, когда iPhone готов...")
    
    # Создаем активатор
    activator = Activator()
    activator.set_progress_callback(print)
    
    # Запускаем активацию
    print("\n🚀 Запуск активации...")
    print("=" * 60)
    
    success = activator.activate_and_bypass(
        ssid=None,      # укажите SSID если нужен Wi-Fi
        password=None,  # укажите пароль если нужен Wi-Fi
        install_app=True
    )
    
    print("\n" + "=" * 60)
    if success:
        print("✅ АКТИВАЦИЯ УСПЕШНА!")
        print("📱 На рабочем столе iPhone должна появиться иконка SemplChecker")
    else:
        print("❌ АКТИВАЦИЯ НЕ УДАЛАСЬ")
        print("   Проверьте логи выше для выявления ошибки")
    print("=" * 60)

if __name__ == "__main__":
    main()
