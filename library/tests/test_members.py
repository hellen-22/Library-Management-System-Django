from django.test import TestCase
from django.urls import reverse

from library.models import Member
from users.models import Librarian


class TestAddMemberView(TestCase):
    def setUp(self):
        self.data = {"name": "John Doe", "email": "johndoe@gmail.com"}

        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")

    def test_login_required(self):
        response = self.client.post(reverse("add-member"), self.data)

        self.assertEqual(Member.objects.count(), 0)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add-member')}")

    def test_valid_data_creates_member(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-member"), self.data)

        self.assertEqual(Member.objects.count(), 1)

    def test_invalid_data_does_not_create_member(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add-member"), {"name": "", "email": "email"})

        self.assertEqual(Member.objects.count(), 0)

    def test_member_email_must_be_unique(self):
        self.client.force_login(self.user)
        Member.objects.create(name="John Doe", email="johndoe@gmail.com")
        response = self.client.post(reverse("add-member"), self.data)

        assert response.context["form"].errors["email"] == ["A member with that email already exists."]


class TestUpdateMemberDetailsView(TestCase):
    def setUp(self):
        self.member = Member.objects.create(name="John Doe", email="johndoe@gmail.com")
        self.member2 = Member.objects.create(name="Jane Doe", email="janedoe@gmail.com")
        self.data = {"name": "Jane Doe", "email": "update@gmail.com"}

        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")

    def test_login_required(self):
        self.client.get(reverse("update-member", kwargs={"pk": self.member.pk}), self.data)
        self.member.refresh_from_db()

        self.assertEqual(self.member.name, "John Doe")

    def test_valid_data_updates_member(self):
        self.client.force_login(self.user)
        self.client.post(reverse("update-member", kwargs={"pk": self.member.pk}), self.data)

        self.member.refresh_from_db()
        self.assertEqual(self.member.name, "Jane Doe")

    def test_invalid_data_does_not_update_member(self):
        self.client.force_login(self.user)
        self.client.post(reverse("update-member", kwargs={"pk": self.member.pk}), {"name": "", "email": "email"})

        self.member.refresh_from_db()
        self.assertEqual(self.member.name, "John Doe")

    def test_member_email_must_not_be_duplicate(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("update-member", kwargs={"pk": self.member.pk}), {"name": "Jane Doe", "email": self.member2.email}
        )

        assert response.context["form"].errors["email"] == ["A member with that email already exists."]


class TestDeleteMemberView(TestCase):
    def setUp(self):
        self.member = Member.objects.create(name="John Doe", email="johndoe@gmail.com")
        self.member2 = Member.objects.create(name="Jane Doe", email="janedoe@gmail.com")

        self.user = Librarian.objects.create_user(email="test@gmail.com", password="password")

    def test_login_required(self):
        self.client.get(reverse("delete-member", kwargs={"pk": self.member.pk}))

        self.assertEqual(Member.objects.count(), 2)
        self.assertTrue(Member.objects.filter(pk=self.member.pk).exists())

    def test_member_does_not_exist_after_deletion(self):
        self.client.force_login(self.user)
        self.client.get(reverse("delete-member", kwargs={"pk": self.member.pk}))

        self.assertEqual(Member.objects.count(), 1)
        self.assertFalse(Member.objects.filter(pk=self.member.pk).exists())
