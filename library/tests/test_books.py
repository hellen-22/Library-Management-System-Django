from django.test import TestCase
from django.urls import reverse

from library.models import Book
from users.models import Librarian

class TestCreateBook(TestCase):
    def setUp(self):
        self.data = {"title": "Test Book", "author": "John Doe", "category": "fiction", "quantity": 8}

        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")

    def test_login_required(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-book"), self.data)

        self.assertEqual(Book.objects.count(), 0)

    def test_login_required(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-book"), self.data)

        self.assertEqual(Book.objects.count(), 0)
