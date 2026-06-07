# build_win.py

import os
import shutil
import PyInstaller.__main__

try:
    from PyInstaller.utils.hooks import collect_submodules
except ImportError:
    print("Установи PyInstaller:")
    print("pip install pyinstaller")
    exit(1)

# ---------------------------------------------------
# Очистка старых сборок
# ---------------------------------------------------

for folder in ["build", "dist"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)

spec_file = "SemplActivatorPro.spec"
if os.path.exists(spec_file):
    os.remove(spec_file)

# ---------------------------------------------------
# Собираем все модули pymobiledevice3
# ---------------------------------------------------

print("🔍 Поиск модулей pymobiledevice3...")

hidden_imports = collect_submodules("pymobiledevice3")

# Дополнительные библиотеки
extra_imports = [
    "PyQt6",
    "ipsw_parser",
    "zeroconf",
    "pyimg4",
    "apple_compress",
    "readchar",
    "requests",
    "typer",
    "click",
]

for module in extra_imports:
    if module not in hidden_imports:
        hidden_imports.append(module)

print(f"📦 Найдено модулей: {len(hidden_imports)}")

# ---------------------------------------------------
# Формируем параметры PyInstaller
# ---------------------------------------------------

args = [
    "main.py",
    "--onefile",
    "--console",
    "--clean",
    "--noconfirm",
    "--name=SemplActivatorPro",
]

# Папки проекта
if os.path.exists("core"):
    args.append(f"--add-data=core{os.pathsep}core")

if os.path.exists("ui"):
    args.append(f"--add-data=ui{os.pathsep}ui")

# Скрытые импорты
for module in hidden_imports:
    args.append(f"--hidden-import={module}")

# ---------------------------------------------------
# Сборка
# ---------------------------------------------------

print("\n🚀 Запуск сборки...")

PyInstaller.__main__.run(args)

print("\n✅ Готово!")
print("📂 Файл находится в dist/SemplActivatorPro.exe")