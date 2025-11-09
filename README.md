# Enquiry-Automation-Service
## Описание
Сервис предназначен для формирования справок формата xlsx, docx и pdf из заранее подготовленного шаблона того же формата с вкраплением синтаксиса **СТОРОННИХ БИБЛИОТЕК**, работает на **Python=3.12.3** с использованием openpyxl и spire.doc(*trial*),
### Установка пакетов
```bash
pip install --upgrade pip
pip install poetry
```
Далее в корне проекта(enquiry-automation-service)
```bash
poetry install
```
### Запуск в терминале (из папки проекта(enquiry-automation-service))
Написав в терминале, открытом в папке проекта(enquiry-automation-service)
```bash
poetry env activate
poetry run py .\src\main.py
```