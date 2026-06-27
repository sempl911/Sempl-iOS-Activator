#!/usr/bin/env python3

import sys
import traceback
import os


def is_frozen():
    """Проверяет, запущено ли приложение как .exe"""
    return getattr(sys, "frozen", False)


def check_pymobiledevice3():
    """
    Проверяет наличие pymobiledevice3 внутри EXE,
    а не наличие внешней команды pymobiledevice3.exe
    """
    try:
        import pymobiledevice3

        print("✅ pymobiledevice3 найден")
        print("Версия:", getattr(pymobiledevice3, "__version__", "unknown"))

        try:
            print("Файл:", pymobiledevice3.__file__)
        except Exception:
            pass

        return True

    except Exception:
        print("❌ Не удалось импортировать pymobiledevice3:")
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   Sempl Activator Pro")
    print("=" * 60)
    print("Python:", sys.version)

    if is_frozen():
        print("Режим: EXE")
    else:
        print("Режим: Python")

    print()

    # Проверяем библиотеку
    if not check_pymobiledevice3():
        print("\n⚠️ pymobiledevice3 не найден внутри приложения")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

    try:
        print("\n🖥️ Загрузка PyQt6...")

        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from ui.main_window import MainWindow

        print("✅ PyQt6 загружен")
        print("✅ MainWindow загружен")

        # Включаем поддержку высокого DPI
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)

        app.setApplicationName("Sempl Activator Pro")
        app.setOrganizationName("Sempl")
        app.setApplicationVersion("2.0.0")

        window = MainWindow()
        window.show()

        print("✅ Окно создано")

        sys.exit(app.exec())

    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        print("Установите PyQt6: pip install PyQt6")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

    except Exception:
        print("\n❌ Ошибка запуска приложения:\n")
        traceback.print_exc()

        input("\nНажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n❌ Критическая ошибка:\n")
        traceback.print_exc()

        input("\nНажмите Enter для выхода...")