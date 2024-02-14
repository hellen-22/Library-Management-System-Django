from django.test import TestCase
from django.urls import reverse

from library.models import Book, BorrowedBook, Member
from users.models import Librarian


class TestLendBookView(TestCase):
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
        self.data = {
            "book": self.book.pk,
            "member": self.member.pk,
            "return_date": "2024-12-12",
            "fine": 0.00,
            "payment_method": "cash",
        }

    def test_login_required(self):
        response = self.client.post(reverse("lend-book"), self.data)

        self.assertEqual(BorrowedBook.objects.count(), 1)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('lend-book')}")

    def test_valid_data_creates_borrowed_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("lend-book"), self.data)

        self.assertEqual(BorrowedBook.objects.count(), 2)

    def test_invalid_data_does_not_create_borrowed_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("lend-book"), {"book": "", "member": "", "return_date": "", "fine": ""})

        self.assertEqual(BorrowedBook.objects.count(), 1)

    def test_book_quantity_decreases(self):
        self.client.force_login(self.user)
        self.client.post(reverse("lend-book"), self.data)

        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 9)


class TestLendIndividualMemberView(TestCase):
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

        self.data = {"book": self.book.id, "return_date": "2024-12-12", "fine": 0.00, "payment_method": "cash"}

    def test_login_required(self):
        response = self.client.post(reverse("lend-member-book", kwargs={"pk": self.member.pk}), self.data)

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('lend-member-book', kwargs={'pk': self.member.pk})}"
        )

    def test_lend_book(self):
        self.client.force_login(self.user)
        self.client.post(reverse("lend-member-book", kwargs={"pk": self.member.pk}), self.data)

        self.book.refresh_from_db()
        self.assertEqual(BorrowedBook.objects.count(), 1)
        self.assertEqual(self.book.quantity, 9)

    def test_invalid_data_does_not_lend_book(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("lend-member-book", kwargs={"pk": self.member.pk}), {"book": "", "return_date": "", "fine": ""}
        )

        self.book.refresh_from_db()
        self.assertEqual(BorrowedBook.objects.count(), 0)
        self.assertEqual(self.book.quantity, 10)


class TestLentBooksView(TestCase):
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
        self.borrowed_book2 = BorrowedBook.objects.create(member=self.member, book=self.book, return_date="2021-12-12")

    def test_login_required(self):
        response = self.client.get(reverse("lent-books"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('lent-books')}")

    def test_list_lent_books(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("lent-books"))

        self.assertContains(response, "Test Title")
        self.assertEqual(BorrowedBook.objects.count(), 2)


class TestUpdateLentBookView(TestCase):
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

    def test_login_required(self):
        response = self.client.post(reverse("edit-borrowed-book", kwargs={"pk": self.borrowed_book.pk}))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('edit-borrowed-book', kwargs={'pk': self.borrowed_book.pk})}"
        )

    def test_valid_data_updates_borrowed_book(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("edit-borrowed-book", kwargs={"pk": self.borrowed_book.pk}),
            {"return_date": "2024-12-12", "fine": 0.00},
        )

        self.borrowed_book.refresh_from_db()
        self.assertEqual(self.borrowed_book.return_date.strftime("%Y-%m-%d"), "2024-12-12")

    def test_invalid_data_does_not_update_borrowed_book(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("edit-borrowed-book", kwargs={"pk": self.borrowed_book.pk}), {"return_date": "", "fine": ""}
        )

        self.borrowed_book.refresh_from_db()
        self.assertEqual(self.borrowed_book.return_date.strftime("%Y-%m-%d"), "2021-12-12")


class TestDeleteLentBookView(TestCase):
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

    def test_login_required(self):
        response = self.client.get(reverse("delete-borrowed-book", kwargs={"pk": self.borrowed_book.pk}))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('delete-borrowed-book', kwargs={'pk': self.borrowed_book.pk})}",
        )
        self.assertEqual(BorrowedBook.objects.count(), 1)

    def test_delete_borrowed_book(self):
        self.client.force_login(self.user)
        self.client.get(reverse("delete-borrowed-book", kwargs={"pk": self.borrowed_book.pk}))

        self.book.refresh_from_db()
        self.assertEqual(BorrowedBook.objects.count(), 0)
        self.assertEqual(self.book.quantity, 11)
