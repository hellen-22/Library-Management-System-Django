from django.test import TestCase
from django.urls import reverse

from library.models import Book, BorrowedBook, Member
from users.models import Librarian


class TestReturnBookView(TestCase):
    def setUp(self):
        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")
        self.member = Member.objects.create(name="John Doe", email="member@gmail.com")
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            category="fiction",
            quantity=10,
            borrowing_fee=1.00,
            status="available",
        )
        self.borrowed_book = BorrowedBook.objects.create(member=self.member, book=self.book, return_date="2021-12-12")
        self.borrowed_book2 = BorrowedBook.objects.create(member=self.member, book=self.book, return_date="2024-12-12")

    def test_login_required(self):
        response = self.client.get(reverse("return-book", kwargs={"pk": self.borrowed_book2.pk}))

        self.assertEqual(self.borrowed_book2.returned, False)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('return-book', kwargs={'pk': self.borrowed_book2.pk})}"
        )

    def test_return_book(self):
        self.client.force_login(self.user)
        self.client.get(reverse("return-book", kwargs={"pk": self.borrowed_book2.pk}))

        self.borrowed_book2.refresh_from_db()
        self.book.refresh_from_db()

        self.assertEqual(self.borrowed_book2.returned, True)
        self.assertEqual(self.book.quantity, 11)

    def test_if_book_is_overdue_redirects_to_pay_fine(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("return-book", kwargs={"pk": self.borrowed_book.pk}))

        self.assertRedirects(response, reverse("return-book-fine", kwargs={"pk": self.borrowed_book.pk}))
        self.assertEqual(self.borrowed_book.returned, False)
        self.assertEqual(self.book.quantity, 10)


class TestReturnBookOnFineView(TestCase):
    def setUp(self):
        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")
        self.member = Member.objects.create(name="John Doe", email="member@gmail.com")
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            category="fiction",
            quantity=10,
            borrowing_fee=1.00,
            status="available",
        )
        self.borrowed_book = BorrowedBook.objects.create(member=self.member, book=self.book, return_date="2021-12-12")
        self.data = {"payment_method": "cash"}

    def test_login_required(self):
        response = self.client.post(reverse("return-book-fine", kwargs={"pk": self.borrowed_book.pk}), self.data)

        self.assertEqual(self.borrowed_book.returned, False)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('return-book-fine', kwargs={'pk': self.borrowed_book.pk})}"
        )

    def test_return_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("return-book-fine", kwargs={"pk": self.borrowed_book.pk}), self.data)

        self.borrowed_book.refresh_from_db()
        self.book.refresh_from_db()

        self.assertEqual(self.borrowed_book.returned, True)
        self.assertEqual(self.book.quantity, 11)
