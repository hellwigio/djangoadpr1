# Django: библиотека

## Запуск

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте http://127.0.0.1:8000/admin/ и войдите с созданными учётными данными.
Корневой адрес перенаправляет в админку. Для локального запуска используется DEBUG;
для другого окружения задайте `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` и
`DJANGO_ALLOWED_HOSTS` (имена хостов через запятую). Часовой пояс проекта — UTC.

## Команды Taskfile

Для коротких команд установите [Task (go-task)](https://taskfile.dev/docs/installation)
версии 3 и `uv`. Это отдельная утилита, она не устанавливается из `requirements.txt`.
Taskfile рассчитан на Linux/macOS. Команды выполняйте из папки проекта;
активировать виртуальное окружение не нужно — используется `.venv/bin/python`.

Первый запуск:

```bash
task setup       # создать .venv, установить зависимости через uv pip, применить миграции
task superuser   # интерактивно создать администратора
task run         # запустить сервер на http://127.0.0.1:8000
```

Повторный запуск — `task run`. Для остановки сервера нажмите `Ctrl+C`.
Список команд показывает `task` или `task --list`.

| Команда | Действие |
| --- | --- |
| `task venv` | Создать окружение, только если его ещё нет |
| `task install` | Создать окружение при необходимости и установить зависимости |
| `task setup` | Установить зависимости и применить миграции |
| `task run` | Запустить сервер разработки |
| `task makemigrations` | Создать миграции после изменения моделей |
| `task migrate` | Применить миграции |
| `task superuser` | Создать администратора |
| `task shell` | Открыть интерактивную Django shell |
| `task check` | Проверить Django и наличие изменений моделей без миграций |
| `task test` | Запустить тесты |
| `task verify` | Последовательно выполнить проверки и тесты |
| `task manage -- …` | Выполнить произвольную команду `manage.py` |

Дополнительные аргументы передаются после `--`:

```bash
task run -- 127.0.0.1:8001
task test -- library --verbosity 2
task makemigrations -- library
task manage -- showmigrations
```

После изменения моделей выполните `task makemigrations`, затем `task migrate`.
Перед сохранением изменений запускайте `task verify`.

## Проверки

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Тесты проверяют удаление автора без потери книг, необязательные поля и значения по умолчанию,
границы числовых полей, средний рейтинг, обратные связи, просрочку,
уникальность постов, категорий и почты, регистрацию на события и страницы всех моделей в админке.
