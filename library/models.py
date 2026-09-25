from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone


class Gender(models.TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'
    OTHER = 'other', 'Другой'
    UNSPECIFIED = 'unspecified', 'Не указан'


class Author(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    birth_date = models.DateField('Дата рождения')
    profile = models.URLField('Ссылка на профиль', null=True, blank=True)
    deleted = models.BooleanField('Удалён ли автор', default=False, help_text='Если флажок выключен — автор активен. Включите, чтобы пометить автора как недоступного; запись и книги сохранятся.')
    rating = models.IntegerField('Рейтинг автора', default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name[:1]}.'


class Category(models.Model):
    name = models.CharField('Название', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Library(models.Model):
    name = models.CharField('Название', max_length=100)
    location = models.CharField('Локация', max_length=200)
    site = models.URLField('Сайт', null=True, blank=True)

    class Meta:
        verbose_name = 'Библиотека'
        verbose_name_plural = 'Библиотеки'

    def __str__(self):
        return f'{self.name} ({self.location})'


class Member(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Админ'
        STAFF = 'staff', 'Сотрудник'
        READER = 'reader', 'Читатель'

    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Электронная почта', unique=True)
    gender = models.CharField('Гендер', max_length=50, choices=Gender.choices)
    birth_date = models.DateField('Дата рождения')
    age = models.IntegerField('Возраст', validators=[MinValueValidator(6), MaxValueValidator(120)])
    role = models.CharField('Роль', max_length=20, choices=Role.choices)
    active = models.BooleanField('Активный', default=True)
    libraries = models.ManyToManyField(Library, related_name='members', verbose_name='Библиотеки')

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'


class Book(models.Model):
    class Genre(models.TextChoices):
        FICTION = 'Fiction', 'Fiction'
        NON_FICTION = 'Non-Fiction', 'Non-Fiction'
        SCIENCE_FICTION = 'Science Fiction', 'Science Fiction'
        FANTASY = 'Fantasy', 'Fantasy'
        MYSTERY = 'Mystery', 'Mystery'
        BIOGRAPHY = 'Biography', 'Biography'

    title = models.CharField('Название', max_length=100)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL, related_name='books', verbose_name='Автор')
    publishing_date = models.DateField('Дата публикации')
    summary = models.TextField('Краткое описание', blank=True)
    genre = models.CharField('Жанр', max_length=50, choices=Genre.choices)
    page_count = models.PositiveIntegerField('Количество страниц', null=True, blank=True, validators=[MaxValueValidator(10000)])
    publisher = models.ForeignKey(Member, null=True, blank=True, on_delete=models.CASCADE, related_name='published_books', limit_choices_to={'role': Member.Role.STAFF}, verbose_name='Публикующий сотрудник')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='books', verbose_name='Категория')
    libraries = models.ManyToManyField(Library, related_name='books', verbose_name='Библиотеки')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    @property
    def rating(self):
        average = self.reviews.aggregate(value=Avg('rating'))['value']
        return round(average, 2) if average is not None else 0

    def __str__(self):
        return self.title


class Posts(models.Model):
    title = models.CharField('Заголовок', max_length=255, unique_for_date='created_at')
    body = models.TextField('Текст')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    moderated = models.BooleanField('Промодерировано', default=False)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='posts', verbose_name='Библиотека')
    created_at = models.DateField('Дата создания')
    updated_at = models.DateField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        constraints = [models.UniqueConstraint(fields=['title', 'created_at'], name='unique_post_title_per_day')]

    def __str__(self):
        return f'{self.title} ({self.created_at})'


class Borrow(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrows', verbose_name='Участник')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows', verbose_name='Книга')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='borrows', verbose_name='Библиотека')
    borrow_date = models.DateField('Дата выдачи')
    return_date = models.DateField('Срок возврата')
    returned = models.BooleanField('Возвращена', default=False)

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'

    def is_overdue(self):
        return not self.returned and self.return_date < timezone.localdate()

    def __str__(self):
        return f'{self.book} → {self.member}, до {self.return_date}'


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='Книга')
    reviewer = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reviews', verbose_name='Обзорщик')
    rating = models.FloatField('Рейтинг', validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField('Отзыв')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.book}: {self.rating}/5 — {self.reviewer}'


class AuthorDetail(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='details', verbose_name='Автор')
    biography = models.TextField('Биография')
    birth_city = models.CharField('Город рождения', max_length=50, blank=True)
    gender = models.CharField('Гендер', max_length=50, choices=Gender.choices)

    class Meta:
        verbose_name = 'Биография автора'
        verbose_name_plural = 'Биографии авторов'

    def __str__(self):
        return f'Биография: {self.author}'


class Event(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    date = models.DateTimeField('Дата и время')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='events', verbose_name='Библиотека')
    books = models.ManyToManyField(Book, related_name='events', verbose_name='Обсуждаемые книги')

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f'{self.title} ({self.date})'


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants', verbose_name='Событие')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='event_participations', verbose_name='Участник')
    registration_date = models.DateField('Дата регистрации', default=timezone.localdate)

    class Meta:
        verbose_name = 'Регистрация на событие'
        verbose_name_plural = 'Регистрации на события'
        constraints = [models.UniqueConstraint(fields=['event', 'member'], name='unique_event_member')]

    def __str__(self):
        return f'{self.member} → {self.event}'
