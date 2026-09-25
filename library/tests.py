from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import (Author, AuthorDetail, Book, Borrow, Category, Event,
                     EventParticipant, Gender, Library, Member, Posts, Review)


class LibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name='Лев', last_name='Толстой', birth_date=date(1828, 9, 9))
        cls.library = Library.objects.create(name='Центральная', location='Москва')
        cls.member = Member.objects.create(first_name='Иван', last_name='Иванов', email='ivan@example.com', gender=Gender.MALE, birth_date=date(2000, 1, 1), age=26, role=Member.Role.STAFF)
        cls.book = Book.objects.create(title='Война и мир', author=cls.author, publishing_date=date(1869, 1, 1), genre=Book.Genre.FICTION)

    def test_author_delete_preserves_book(self):
        self.author.delete()
        self.book.refresh_from_db()
        self.assertIsNone(self.book.author)

    def test_optional_fields_and_defaults(self):
        self.author.full_clean()
        self.book.full_clean()
        self.library.full_clean()
        self.assertFalse(self.author.deleted)
        self.assertEqual(self.author.rating, 1)
        self.assertTrue(self.member.active)
        detail = AuthorDetail(author=self.author, biography='Биография', gender=Gender.MALE)
        detail.full_clean()
        self.assertEqual(str(self.author), 'Лев Т.')

    def test_validation_bounds(self):
        for obj, field, values in [(self.author, 'rating', [0, 11]), (self.member, 'age', [5, 121]), (self.book, 'page_count', [-1, 10001])]:
            for value in values:
                with self.subTest(field=field, value=value):
                    setattr(obj, field, value)
                    with self.assertRaises(ValidationError):
                        obj.full_clean()
        for value in [0.9, 5.1]:
            with self.assertRaises(ValidationError):
                Review(book=self.book, reviewer=self.member, rating=value, description='Отзыв').full_clean()

    def test_rating_average(self):
        self.assertEqual(self.book.rating, 0)
        for rating in [3.5, 4, 5]:
            Review.objects.create(book=self.book, reviewer=self.member, rating=rating, description='Отзыв')
        self.assertEqual(self.book.rating, 4.17)

    def test_relationships(self):
        self.book.libraries.add(self.library)
        self.member.libraries.add(self.library)
        self.assertIn(self.book, self.library.books.all())
        self.assertIn(self.member, self.library.members.all())
        category = Category.objects.create(name='Классика')
        self.book.category = category
        self.book.save()
        self.assertIn(self.book, category.books.all())
        category.delete()
        self.book.refresh_from_db()
        self.assertIsNone(self.book.category)

    def test_borrow_overdue(self):
        today = timezone.localdate()
        borrow = Borrow(member=self.member, book=self.book, library=self.library, borrow_date=today - timedelta(days=7), return_date=today - timedelta(days=1))
        self.assertTrue(borrow.is_overdue())
        borrow.returned = True
        self.assertFalse(borrow.is_overdue())
        borrow.returned = False
        for offset in [0, 1]:
            borrow.return_date = today + timedelta(days=offset)
            self.assertFalse(borrow.is_overdue())

    def test_post_unique_per_day(self):
        data = dict(title='Новости', body='Текст', author=self.member, library=self.library, created_at=date(2026, 9, 25))
        post = Posts.objects.create(**data)
        self.assertFalse(post.moderated)
        self.assertEqual(post.updated_at, timezone.localdate())
        with self.assertRaises(ValidationError):
            Posts(**data).full_clean()
        data['created_at'] += timedelta(days=1)
        Posts(**data).full_clean()

    def test_events(self):
        event = Event.objects.create(title='Обсуждение', description='Книжный клуб', date=timezone.now(), library=self.library)
        event.books.add(self.book)
        participant = EventParticipant.objects.create(event=event, member=self.member)
        self.assertEqual(participant.registration_date, timezone.localdate())
        self.assertIn(event, self.book.events.all())
        self.assertIn(participant, self.member.event_participations.all())
        self.assertIsNotNone(event.date.hour)
        with self.assertRaises(ValidationError):
            EventParticipant(event=event, member=self.member).full_clean()

    def test_unique_category_and_email(self):
        Category.objects.create(name='Классика')
        with self.assertRaises(ValidationError):
            Category(name='Классика').full_clean()
        self.member.pk = None
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def test_admin_pages(self):
        user = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'test-password')
        self.client.force_login(user)
        for model in [Author, AuthorDetail, Book, Borrow, Category, Event, EventParticipant, Library, Member, Posts, Review]:
            for action in ['changelist', 'add']:
                with self.subTest(model=model.__name__, action=action):
                    self.assertEqual(self.client.get(reverse(f'admin:library_{model._meta.model_name}_{action}')).status_code, 200)
