# О проекте

Социальная сеть YaTube.

Функционал:
* Просмотр, создание, изменение и удаление записей.
* Возможность добавления, редактирования, удаления своих комментариев и просмотр чужих.
* Просмотр и создание групп.
* Подписки на пользователей.


## Запуск проекта

Необходимо клонировать репозиторий и перейти в корневую директорию проекта:

```bash
git clone git@github.com:SergoSolo/hw05_final.git
```

```
cd hw05_final
```

Создаем и активируем виртуальное окружение:

```bash
python -m venv venv
```

* Активация для Linux/MacOS

    ```bash
    source venv/bin/activate
    ```

* Активация для windows

    ```bash
    source venv/scripts/activate
    ```

Установка зависимостей: 

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

 Выполняем миграции:
 
 ```$ python3 manage.py migrate```
 
 Запускаем django сервер:
 
 ```$ python3 manage.py runserver```



Проект доступен по адресу http://127.0.0.1:8000/


##  Используемые технологии:
- Python version 3.10
- Django
- Pillow


## Автор:
> [Sergey](https://github.com/SergoSolo)
