# Sempl Activator Pro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**Профессиональный инструмент для активации iPhone и пропуска экрана приветствия (Setup Assistant) без ввода Apple ID**

---

## 📖 О проекте

**Sempl Activator Pro** — это мощная утилита с графическим интерфейсом, которая позволяет полностью автоматизировать процесс активации iPhone и пропустить все экраны начальной настройки. Инструмент идеально подходит для тех, кому нужно быстро настроить несколько устройств для тестирования или диагностики.

### Основные возможности

| Функция | Описание |
|---------|----------|
| 📱 **Автоматическое определение устройства** | Мгновенное подключение и получение всей информации об iPhone |
| 🔍 **Проверка статуса iCloud Lock** | Определение, заблокировано ли устройство |
| 🚀 **Активация одним кликом** | Полностью автоматический процесс активации |
| ⏩ **Пропуск Setup Assistant** | Автоматический обход всех экранов приветствия |
| 🌐 **Автоматическое подключение к Wi-Fi** | Предварительная настройка сети на устройстве |
| 💻 **Кроссплатформенность** | Работает на macOS и Windows |

---

## 🖥️ Системные требования

| Платформа | Требования |
|-----------|------------|
| **macOS** | macOS 10.15+, Intel или Apple Silicon |
| **Windows** | Windows 10/11, 64-bit |
| **Python** | 3.11 или новее |
| **iPhone** | iOS 15.0+ (проверено до iOS 18) |

---

## 🚀 Быстрый старт

### Установка из исходников

```bash
# Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/SemplActivatorPro.git
cd SemplActivatorPro

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск
python main.py
