from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import AddBookForm, AddMemberForm, UpdateMemberForm
from .models import Book, Member


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "base.html")


@method_decorator(login_required, name="dispatch")
class AddMemberView(View):
    def get(self, request, *args, **kwargs):
        form = AddMemberForm()
        return render(request, "members/add-member.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AddMemberForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("members")

        return render(request, "members/add-member.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MembersListView(View):
    def get(self, request, *args, **kwargs):
        members = Member.objects.all()
        return render(request, "members/list-members.html", {"members": members})


@method_decorator(login_required, name="dispatch")
class UpdateMemberDetailsView(View):
    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(instance=member)
        return render(request, "members/update-member.html", {"form": form, "member": member})

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(request.POST, instance=member)

        if form.is_valid():
            form.save()
            return redirect("members")

        return render(request, "members/update-member.html", {"form": form, "member": member})


@method_decorator(login_required, name="dispatch")
class DeleteMemberView(View):
    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        member.delete()
        return redirect("members")


@method_decorator(login_required, name="dispatch")
class AddBookView(View):
    def get(self, request, *args, **kwargs):
        form = AddBookForm()
        return render(request, "books/add-book.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("books")

        return render(request, "books/add-book.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class BooksListView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        return render(request, "books/list-books.html", {"books": books})


@method_decorator(login_required, name="dispatch")
class UpdateBookDetailsView(View):
    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        form = AddBookForm(instance=book)
        return render(request, "books/update-book.html", {"form": form, "book": book})

    def post(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        form = AddBookForm(request.POST, instance=book)

        if form.is_valid():
            form.save()
            return redirect("books")

        return render(request, "books/update-book.html", {"form": form, "book": book})


@method_decorator(login_required, name="dispatch")
class DeleteBookView(View):
    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        book.delete()
        return redirect("books")
