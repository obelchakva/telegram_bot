# MASSSTART telegram bot

## Описание программы

- main.py - основной файл, который отвечает за функциональность бота
- test_manager.py - вспомогательный файл, который создает базу данных для хранения задач и выступает мостом между этой базой данных и основным файлом программы\
- tests.db - база данных, хранящая информацию о задачах
- fix_database - файл разработчика для решения проблем с базой данных (необязателен для работы программы)
- requirements.txt - необходимое окружение для работы программы

## Запуск

### Ubuntu/Linux
```
# Обновление пакетов
sudo apt update

# Установка Python3 и pip
sudo apt install python3 python3-pip python3-venv -y

# Проверка установки
python3 --version
pip3 --version

# Переход в папку с ботом
cd /путь/к/папке/с/ботом

# Создание виртуального окружения
python3 -m venv bot_env

# Активация виртуального окружения
source bot_env/bin/activate

# Проверка - в начале строки должно быть (bot_env)

# Обновление pip
pip install --upgrade pip

# Установка зависимостей из requirements.txt
pip install -r requirements.txt

# Запуск основного файла
python3 main.py
```

### Windows
```
python --version
pip --version

# Переход в папку с ботом
cd C:\путь\к\папке\с\ботом

# Создание виртуального окружения
python -m venv bot_env

# Активация виртуального окружения
bot_env\Scripts\activate.bat

# Обновление pip
python -m pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Запуск основного файла
python main.py
```

### macOS
```
# Установка Homebrew (если нет)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Python
brew install python

# Проверка установки
python3 --version
pip3 --version

# Переход в папку с ботом
cd /путь/к/папке/с/ботом

# Создание виртуального окружения
python3 -m venv bot_env

# Активация виртуального окружения
source bot_env/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Запуск основного файла
python3 main.py
```
