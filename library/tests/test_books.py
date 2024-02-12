from django.test import TestCase
from django.urls import reverse

from library.models import Book
from users.models import Librarian


class TestAddBookView(TestCase):
    def setUp(self):
        self.data = {
            "title": "Test Title",
            "author": "Test Author",
            "category": "fiction",
            "quantity": 10,
            "borrowing_fee": 1.00,
            "status": "available",
        }

        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")

    def test_login_required(self):
        response = self.client.post(reverse("add-book"), self.data)

        self.assertEqual(Book.objects.count(), 0)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add-book')}")

    def test_valid_data_creates_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-book"), self.data)

        self.assertEqual(Book.objects.count(), 1)

    def test_invalid_data_does_not_create_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-book"), {"title": "", "author": "author"})

        self.assertEqual(Book.objects.count(), 0)


class TestListBooksView(TestCase):
    def setUp(self):
        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            category="fiction",
            quantity=10,
            borrowing_fee=1.00,
            status="available",
        )
        self.book2 = Book.objects.create(
            title="Test Title 2",
            author="Test Author 2",
            category="non-fiction",
            quantity=5,
            borrowing_fee=2.00,
            status="available",
        )

    def test_login_required(self):
        response = self.client.get(reverse("books"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('books')}")

    def test_list_books(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("books"))

        self.assertContains(response, "Test Title")
        self.assertContains(response, "Test Title 2")
        self.assertEqual(Book.objects.count(), 2)


class TestUpdateBookView(TestCase):
    def setUp(self):
        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            category="fiction",
            quantity=10,
            borrowing_fee=1.00,
            status="available",
        )
        self.book2 = Book.objects.create(
            title="Test Title 2",
            author="Test Author 2",
            category="non-fiction",
            quantity=5,
            borrowing_fee=2.00,
            status="available",
        )

    def test_login_required(self):
        response = self.client.post(reverse("update-book", kwargs={"pk": self.book.pk}))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('update-book', kwargs={'pk': self.book.pk})}"
        )
        self.assertEqual(self.book.title, "Test Title")

    def test_valid_data_updates_book(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("update-book", kwargs={"pk": self.book.pk}),
            {
                "title": "Updated Title",
                "author": "Updated Author",
                "category": "non-fiction",
                "quantity": 5,
                "borrowing_fee": 2.00,
                "status": "available",
            },
        )

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")

    def test_invalid_data_does_not_update_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("update-book", kwargs={"pk": self.book.pk}), {"title": "", "author": "author"})

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Test Title")


class TestDeleteBookView(TestCase):
    def setUp(self):
        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            category="fiction",
            quantity=10,
            borrowing_fee=1.00,
            status="available",
        )
        self.book2 = Book.objects.create(
            title="Test Title 2",
            author="Test Author 2",
            category="non-fiction",
            quantity=5,
            borrowing_fee=2.00,
            status="available",
        )

    def test_login_required(self):
        response = self.client.post(reverse("delete-book", kwargs={"pk": self.book.pk}))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('delete-book', kwargs={'pk': self.book.pk})}"
        )
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_book(self):
        self.client.force_login(self.user)
        self.client.get(reverse("delete-book", kwargs={"pk": self.book.pk}))

        self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
