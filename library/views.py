from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import (
    AddBookForm,
    AddMemberForm,
    IssueBookForm,
    IssueMemberBookForm,
    PaymentForm,
    UpdateBorrowedBookForm,
    UpdateMemberForm,
)
from .models import Book, BorrowedBook, Member, Transaction

@method_decorator(login_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
class IssueBookView(View):
    def get(self, request, *args, **kwargs):
        form = IssueBookForm()
        payment_form = PaymentForm()

        return render(request, "books/issue-book.html", {"form": form, "payment_form": payment_form})

    def post(self, request, *args, **kwargs):
        form = IssueBookForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid() and payment_form.is_valid():
            issued_book = form.save(commit=False)
            payment_method = payment_form.cleaned_data["payment_method"]
            books_ids = request.POST.getlist("book")
            amount = 0
            for book_id in books_ids:
                book = Book.objects.get(pk=book_id)
                BorrowedBook.objects.create(
                    member=issued_book.member, book=book, return_date=issued_book.return_date, fine=issued_book.fine
                )
                amount += book.borrowing_fee

            Transaction.objects.create(member=issued_book.member, amount=amount, payment_method=payment_method)

            return redirect("issued-books")

        return render(request, "books/issue-book.html", {"form": form, "payment_form": payment_form})


@method_decorator(login_required, name="dispatch")
class IssueMemberBookView(View):
    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = IssueMemberBookForm()
        payment_form = PaymentForm()
        return render(
            request, "books/issue-member-book.html", {"form": form, "payment_form": payment_form, "member": member}
        )

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = IssueMemberBookForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid() and payment_form.is_valid():
            if member.amount_due > 500:
                form.add_error(None, "Member has exceeded the borrowing limit.")
            else:
                lended_book = form.save(commit=False)
                payment_method = payment_form.cleaned_data["payment_method"]
                book_ids = request.POST.getlist("book")
                amount = 0
                for book_id in book_ids:
                    book = Book.objects.get(pk=book_id)
                    BorrowedBook.objects.create(
                        member=member, book=book, return_date=lended_book.return_date, fine=lended_book.fine
                    )

                    amount += book.borrowing_fee

                Transaction.objects.create(member=member, amount=amount, payment_method=payment_method)

                return redirect("issued-books")

        return render(
            request, "books/issue-member-book.html", {"form": form, "payment_form": payment_form, "member": member}
        )


@method_decorator(login_required, name="dispatch")
class IssuedBooksListView(View):
    def get(self, request, *args, **kwargs):
        books = BorrowedBook.objects.all()
        return render(request, "books/issued-books.html", {"books": books})


@method_decorator(login_required, name="dispatch")
class UpdateBorrowedBookView(View):
    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        form = UpdateBorrowedBookForm(instance=book)
        return render(request, "books/update-borrowed-book.html", {"form": form, "book": book})

    def post(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        form = UpdateBorrowedBookForm(request.POST, instance=book)

        if form.is_valid():
            form.save()
            return redirect("issued-books")

        return render(request, "books/update-borrowed-book.html", {"form": form, "book": book})


@method_decorator(login_required, name="dispatch")
class DeleteBorrowedBookView(View):
    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        book.delete()
        return redirect("issued-books")


@method_decorator(login_required, name="dispatch")
class ReturnBookView(View):
    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        if book.return_date < timezone.now().date():
            return redirect("return-book-fine", pk=book.pk)

        else:
            book.returned = True
            book.save()
            return redirect("issued-books")


@method_decorator(login_required, name="dispatch")
class ReturnBookFineView(View):
    def get(self, request, *args, **kwargs):
        form = PaymentForm()
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        return render(request, "books/return-book-fine.html", {"book": book, "form": form})

    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST)
        book = BorrowedBook.objects.get(pk=kwargs["pk"])

        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            fine = book.fine

            book.returned = True
            book.save()

            Transaction.objects.create(member=book.member, amount=fine, payment_method=payment_method)

            return redirect("issued-books")

        return render(request, "books/return-book-fine.html", {"book": book, "form": form})

@method_decorator(login_required, name="dispatch")
class ListPaymentsView(View):
    def get(self, request, *args, **kwargs):
        payments = Transaction.objects.all()
        return render(request, "payments/list-payments.html", {"payments": payments})

@method_decorator(login_required, name="dispatch")
class DeletePaymentView(View):
    def get(self, request, *args, **kwargs):
        payment = Transaction.objects.get(pk=kwargs["pk"])
        payment.delete()
        return redirect("payments")
