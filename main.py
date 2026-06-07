#!/usr/bin/env python3

import sys
import traceback


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

    print("=== Sempl Activator Pro ===")
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
        print("\nЗагрузка PyQt6...")

        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        print("✅ PyQt6 загружен")
        print("✅ MainWindow загружен")

        app = QApplication(sys.argv)

        app.setApplicationName("Sempl Activator Pro")
        app.setOrganizationName("Sempl")

        window = MainWindow()
        window.show()

        print("✅ Окно создано")

        sys.exit(app.exec())

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