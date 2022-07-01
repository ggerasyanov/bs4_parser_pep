# Парсер документации Python
### Как установить проект:
Клонируем репозеторий с GitHub:
```
git clone https://github.com/ggerasyanov/bs4_parser_pep.git
```
Перейти в корневую папку проекта:
```
cd .../bs4_parser_pep/
```
Создать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Обновить менеджер пакетов pip:
```
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Зайти в папку src:
```
cd src/
```
Парсер готов к работе.

### Возможности парсера:
Парсер может собирать новости по обновлениям Python, следить за последними версииями и скачивать документацию. Так же он умеет проверять статусы PEP Документов и считать их количество.

### Как запустить парсер:
```
#.../bs4_parser_pep/src
python main.py
```
Обязательные аргументы запуска:
```
whats_new # Поиск новостей
latest_versions # Проверить версию Python
download # Скачать документацию последей версии Python
pep # Проверить статусы PEP докуметов
```
Необязательные аргументы запуска: 
```
-c or --clear-cache # отчистить кеш
-o or --output # Выбрать метод вывода данных
```
У аргумента --output есть два обязательных условия вывода данных:
```
-o pretty # Вывести данные в терминал в формате таблицы
-o file # Создать файл с раширением csv
```
Получить помощь по агрументам можно командой:
```
python main.py --help
```

### Пример заупска парсера
```
python main.py whats-new --clear-cache -o pretty
python main.py latest-versions -c --output file
python main.py pep -o pretty
python main.py download
```
