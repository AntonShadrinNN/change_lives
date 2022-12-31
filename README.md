# Парсер 100points

***⚠️ Используйте 100points_threads.py! ⚠️***



## Необходимые библиотеки: 
* bs4
* requests
* lxml
* fake-useragent

## Основные настройки:

#### Статические переменные:
* **LINK** - адрес для авторизации 100points
* **INPUT_LIVES** - относительный путь к файлу с именами учеников и количеством жизней в журнале
* **CONSOLE_OUT** - вывод промежуточной информации на экран (по умолчанию *False*)

#### Оформление файла с именами учеников и количеством жизней в журнале:
* Имена как на сайте
* Имя/Фамилия отделяются от жизней табуляцией (см. **example.txt**)
* Если имени нет на сайте - вызывается ***AttributeError***

## Как использовать:
* Ввести *email* и *password* в консоль
* В случае ошибки в написании удалить файл **session.json**
* Ввести parse при включенном **CONSOLE_OUT**, чтобы посмотреть сколько жизней у каждого ученика на сайте
* Ввести change для изменения жизней в соответствии с файлом **INPUT_LIVES**