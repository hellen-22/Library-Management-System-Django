from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import AddBookForm, AddMemberForm, IssueBookForm, IssueMemberBookForm, UpdateMemberForm
from .models import Book, BorrowedBook, Member


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


class IssueBookView(View):
    def get(self, request, *args, **kwargs):
        form = IssueBookForm()
        return render(request, "books/issue-book.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = IssueBookForm(request.POST)

        if form.is_valid():
            issued_book = form.save(commit=False)
            books_ids = request.POST.getlist("book")
            for book_id in books_ids:
                book = Book.objects.get(pk=book_id)

                BorrowedBook.objects.create(
                    member=issued_book.member, book=book, return_date=issued_book.return_date, fine=issued_book.fine
                )

            return redirect("issued-books")

        return render(request, "books/issue-book.html", {"form": form})


class IssueMemberBookView(View):
    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = IssueMemberBookForm()
        return render(request, "books/issue-member-book.html", {"form": form, "member": member})

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = IssueMemberBookForm(request.POST)

        if form.is_valid():
            lended_book = form.save(commit=False)
            book_ids = request.POST.getlist("book")
            for book_id in book_ids:
                book = Book.objects.get(pk=book_id)
                BorrowedBook.objects.create(
                    member=member, book=book, return_date=lended_book.return_date, fine=lended_book.fine
                )

            return redirect("issued-books")

        return render(request, "books/issue-member-book.html", {"form": form, "member": member})


class IssuedBooksListView(View):
    def get(self, request, *args, **kwargs):
        books = BorrowedBook.objects.all()
        return render(request, "books/issued-books.html", {"books": books})


class ChangeBorrowedBookStatusToReturnedView(View):
    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        book.returned = True
        book.save()
        return redirect("issued-books")
