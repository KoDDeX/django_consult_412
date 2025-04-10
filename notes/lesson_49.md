# Lesson 49

## Проблемы с созданием новых столбцов в существующих таблицах

При создании новых столбцов в существующих таблицах могут возникнуть проблемы, если не указать значение по умолчанию для нового столбца. Например, если вы хотите добавить новый столбец `age` в таблицу `users`, но не указали значение по умолчанию, то при выполнении запроса на добавление нового столбца может возникнуть ошибка, если в таблице уже есть данные.

Однако вы можете использовать значение по-умолчанию.

```python
services_2 = models.CharField(max_length=200, default="Что-то по-умолчанию")
```

## `Blank` и `Null`
`blank` и `null` - это два параметра, которые можно использовать при создании полей в моделях Django.
`blank` - это параметр, который указывает, может ли поле быть пустым в форме. Если `blank=True`, то поле может быть пустым в форме, если `blank=False`, то поле обязательно для заполнения.

По умолчанию `blank=False`.

`null` - это параметр, который указывает, может ли поле быть пустым в базе данных. Если `null=True`, то поле может быть пустым в базе данных, если `null=False`, то поле обязательно для заполнения.

## Общие правила использования blank и null

Когда используются вместе (blank=True, null=True)
Чаще всего их используют вместе для числовых полей и отношений, когда поле действительно должно быть опциональным:

Числовые поля (IntegerField, FloatField, DecimalField)
Поля отношений (ForeignKey, OneToOneField, ManyToManyField)
Поля даты и времени (DateField, DateTimeField)
В таких случаях blank=True позволяет форме принять пустое значение, а null=True позволяет сохранить NULL в базе данных.

### Когда используется только blank=True
Для текстовых полей (CharField, TextField) обычно используют только `blank=True`, без `null=True`. Почему? Потому что Django в случае пустого значения сохранит пустую строку (''), а не NULL. Использование и того, и другого параметра создает избыточность — два разных представления для "пустоты".

Когда используется только `null=True`
Это довольно редкий случай. Обычно применяется, когда вы хотите, чтобы поле могло иметь значение NULL в базе данных, но при этом требовалось бы заполнение в формах (например, для полей, которые заполняются автоматически).

## Управление миграциями

### Создание миграций
Для создания миграций в Django используется команда `makemigrations`. Эта команда создает файлы миграций на основе изменений в моделях. Например, если вы добавили новое поле в модель, вы можете выполнить команду:

```bash
python manage.py makemigrations
```

Для применения миграций в базе данных используется команда `migrate`. Эта команда применяет все миграции, которые еще не были применены. Например, если вы хотите применить все миграции, вы можете выполнить команду:

```bash
python manage.py migrate
```

Для возврата миграций используется команда `migrate` с указанием номера миграции. Например, если вы хотите вернуться к миграции с номером 0001, вы можете выполнить команду:

```bash
python manage.py migrate app_name 0001
```

## Создали 2 таблицы с внешним ключом OneToMany
```python
class Order(models.Model):

    # Статусы заказов
    STATUS_CHOICES = [
        ("not_approved", "Не подтвержден"),
        ("moderated", "Прошел модерацию"),
        ("spam", "Спам"),
        ("approved", "Подтвержден"),
        ("in_awaiting", "В ожидании"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    client_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="not_approved")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    master = models.ForeignKey("Master", on_delete=models.SET_NULL, null=True)
    appointment_date = models.DateTimeField(blank=True, null=True)


class Master(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="masters/")
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    experience = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
```

## Создадим записи через Django Shell-Plus
```bash
poetry run python manage.py shell_plus --print-sql
```

Из обязательных полей для мастеров у нас
- first_name
- last_name
- phone
- address
- experience


```python
master1 = Master(
    first_name="Алефтина",
    last_name="Арбузова",
    phone="+7 (999) 999-99-99",
    address="г. Москва, ул. Ленина, д. 1",
    experience=5,
)
master1.save()

master2 = Master.objects.create(
    first_name="Александр",
    last_name="Бородач",
    phone="+7 (999) 999-99-99",
    address="г. Москва, ул. Ленина, д. 2",
    experience=15,
)

# Создание заказа

# client_name
# phone
# master

master1 = Master.objects.get(id=1)

order = Order(
    client_name="Сергей Безруков",
    phone="+7 (999) 999-99-99",
    master=master1
)

order.save()

# Получаем мастера через заказ
order.master
order.master.first_name

# Перепишем заказ 1 на бородоча
order.master = master2
order.save()

```

## related_name="orders"

```python
master = models.ForeignKey("Master", on_delete=models.SET_NULL, null=True, related_name="orders")
```

Теперь мы можем получить все заказы мастера через `related_name`:

```python
master = Master.objects.get(id=1)
master.orders.all()
```

Как с ним работать?
RelatedManager предоставляет методы для работы с набором связанных объектов. Вот основные из них:

.all() — возвращает QuerySet со всеми связанными объектами.
.filter() — позволяет фильтровать связанные объекты.
.create() — создает новый объект, автоматически связывая его с текущим объектом.
.add() — добавляет существующий объект в связь (для ManyToMany).
.remove() — удаляет объект из связи (для ManyToMany).
.clear() — очищает связь (для ManyToMany).

Если его не делать, то придется использовать дополнительный инструмент для получения всех заказов мастера.
```python
master = Master.objects.get(id=1)
orders = Order.objects.filter(master=master)
```

Или set

order_set — это такая штука в Django, которая появляется, если ты не указал related_name в поле ForeignKey. Это имя, которое Django автоматически генерирует для обратной связи между моделями. Давай разберемся, как это работает и почему оно называется именно так.

Когда ты создаешь связь "один ко многим" (OneToMany) через ForeignKey, Django автоматически добавляет возможность обращаться к связанным объектам с другой стороны связи. Если ты не указал related_name, Django использует имя модели в нижнем регистре и добавляет к нему суффикс _set. Например, если у тебя есть модель Order, которая ссылается на модель Master, то у каждого объекта Master появится атрибут order_set, через который можно получить все связанные заказы.


# Пример
```python
master = Master.objects.get(id=1)
orders = master.order_set.all()
```

## Обновление системы таблиц

```python
class Order(models.Model):

    # Статусы заказов
    STATUS_CHOICES = [
        ("not_approved", "Не подтвержден"),
        ("moderated", "Прошел модерацию"),
        ("spam", "Спам"),
        ("approved", "Подтвержден"),
        ("in_awaiting", "В ожидании"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    client_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="not_approved")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    # Один ко многим
    master = models.ForeignKey("Master", on_delete=models.SET_NULL, null=True, related_name="orders")
    appointment_date = models.DateTimeField(blank=True, null=True)


class Master(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="masters/", blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    experience = models.PositiveIntegerField()
    # Многие ко многим
    services = models.ManyToManyField("Service", related_name="masters")
    is_active = models.BooleanField(default=True)


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Время в минутах") # help_text - это текст, который будет отображаться в админке
    is_popular = models.BooleanField(default=False)
    image = models.ImageField(upload_to="services/", blank=True, null=True)

```

Внесение записей
```python
# Создание услуги
service1 = Service.objects.create(
    name="Услуга 1",
    description="Описание услуги 1",
    price=1000,
    duration=60,
    is_popular=True,
)

service2 = Service.objects.create(
    name="Услуга 2",
    description="Описание услуги 2",
    price=2000,
    duration=120,
    is_popular=False,
)

# Добываю мастера id 1
master = Master.objects.get(id=1)

# Подключаю услуги
master.services.add(service1)
master.services.add(service2)

# Я хочу получить все услуги мастера
master.services.all()

# Все услуги которые дает мастер циклом
for service in master.services.all():
    print(service.name)
```

## Удаление связи
```python
# Удаление связи
master.services.remove(service1)
```

## ImageField
`ImageField` - это специальный тип поля в Django, который используется для хранения изображений. Он наследуется от `FileField`, но добавляет некоторые дополнительные функции, специфичные для работы с изображениями.

Для его работы необходимо установить библиотеку Pillow, которая является библиотекой для обработки изображений в Python. Она позволяет работать с различными форматами изображений, такими как JPEG, PNG, GIF и другими.

Так же необходимо добавить в настройки `settings.py`:
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

Без этого Django не сможет правильно обрабатывать загруженные изображения. `MEDIA_URL` - это URL, по которому будут доступны загруженные файлы, а `MEDIA_ROOT` - это путь на диске, где будут храниться загруженные файлы.

Что будет работать без этого а что нет?

О, это классический вопрос, который часто возникает у разработчиков, работающих с `ImageField` в Django. Давай разберемся, почему у тебя всё заработало, что будет работать без указанных настроек, а что нет, и зачем нужен этот загадочный кусок кода с `static()`.

### Почему изображение загрузилось без настроек?

Когда ты загружаешь изображение через админку Django, оно действительно может загрузиться даже без настроек `MEDIA_URL` и `MEDIA_ROOT`. Это происходит потому, что `ImageField` по умолчанию сохраняет файлы в папку, указанную в `upload_to` (или в корень проекта, если `upload_to` не задан). Django просто использует стандартный файловый менеджер операционной системы для сохранения файла.

Однако, **загрузка файла — это только половина дела**. Проблемы начинаются, когда ты пытаешься отобразить это изображение на сайте.

### Что будет работать без `MEDIA_URL` и `MEDIA_ROOT`?

1. **Загрузка изображений через админку**: Работает, потому что Django сохраняет файл в файловую систему.
2. **Сохранение пути к файлу в базе данных**: Работает, потому что `ImageField` сохраняет относительный путь к файлу.

### Что НЕ будет работать без `MEDIA_URL` и `MEDIA_ROOT`?

1. **Отображение изображений на сайте**: Django не знает, как обслуживать загруженные файлы. Без `MEDIA_URL` и `MEDIA_ROOT` сервер не сможет найти путь к файлу, чтобы отдать его браузеру.
2. **Доступ к файлам через браузер**: Если ты попытаешься открыть загруженное изображение по URL, ты получишь ошибку 404, потому что Django не настроен на обработку запросов к медиафайлам.

### Зачем нужен `if settings.DEBUG` с `static()`?

Этот кусок кода:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

нужен для того, чтобы **в режиме разработки** Django мог обслуживать медиафайлы (например, изображения). В продакшене Django **не предназначен для обработки статических и медиафайлов** — это задача веб-сервера, такого как Nginx или Apache. 

Когда `DEBUG=True`, этот код добавляет маршруты для обработки запросов к `MEDIA_URL` и связывает их с файлами в `MEDIA_ROOT`. Это позволяет тебе видеть загруженные изображения прямо в браузере, пока ты разрабатываешь проект.

### Что будет, если убрать этот код?

Если ты уберешь этот код, то:
1. В режиме разработки ты не сможешь увидеть загруженные изображения в браузере. Django не будет знать, как обрабатывать запросы к `MEDIA_URL`.
2. Админка может перестать отображать загруженные изображения, потому что она тоже использует `MEDIA_URL` для их отображения.

### Итог

- **`MEDIA_URL` и `MEDIA_ROOT`** нужны, чтобы Django знал, где хранить загруженные файлы и как их отдавать.
- **Код с `static()`** нужен только в режиме разработки, чтобы ты мог видеть загруженные файлы в браузере.
- В продакшене за обработку медиафайлов отвечает веб-сервер (например, Nginx), и этот код больше не нужен.

Так что, если ты хочешь, чтобы всё работало правильно, добавь `MEDIA_URL`, `MEDIA_ROOT` и код с `static()` в `urls.py`. А если что-то не работает, не стесняйся спрашивать — разберёмся! 😊