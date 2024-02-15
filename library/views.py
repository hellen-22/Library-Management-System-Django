import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import (
    AddBookForm,
    AddMemberForm,
    LendBookForm,
    LendMemberBookForm,
    PaymentForm,
    UpdateBorrowedBookForm,
    UpdateMemberForm,
)
from .models import Book, BorrowedBook, Member, Transaction

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class HomeView(View):
    """
    Home view for the library management system. Displays the Dashboard.
    get(): Returns the home page with the following context:
        - total_members: Total number of members in the library.
        - total_books: Total number of books in the library.
        - total_borrowed_books: Total number of books currently borrowed.
        - total_overdue_books: Total number of books that are overdue.
        - recently_added_books: The 4 most recently added books.
        - total_amount: Total amount of money collected from payments.
        - overdue_amount: Total amount of money that overdue books have accrued.
    """

    def get(self, request, *args, **kwargs):
        members = Member.objects.all()
        books = Book.objects.all()
        borrowed_books = BorrowedBook.objects.filter(returned=False)
        overdue_books = BorrowedBook.objects.filter(return_date__lt=timezone.now().date(), returned=False)

        total_members = members.count()
        total_books = books.count()
        total_borrowed_books = borrowed_books.count()
        total_overdue_books = overdue_books.count()

        recently_added_books = books.order_by("-created_at")[:4]

        total_amount = sum([payment.amount for payment in Transaction.objects.all()])
        overdue_amount = sum([book.fine for book in overdue_books])

        context = {
            "total_members": total_members,
            "total_books": total_books,
            "total_borrowed_books": total_borrowed_books,
            "total_overdue_books": total_overdue_books,
            "recently_added_books": recently_added_books,
            "total_amount": total_amount,
            "overdue_amount": overdue_amount,
        }

        return render(request, "index.html", context)


@method_decorator(login_required, name="dispatch")
class AddMemberView(View):
    """
    Add Member view for the library management system.
    get(): Returns the add member page with the AddMemberForm.
    post(): Validates the form and saves the new member to the database.
    """

    def get(self, request, *args, **kwargs):
        form = AddMemberForm()
        return render(request, "members/add-member.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AddMemberForm(request.POST)

        if form.is_valid():
            form.save()
            logger.info("New member added successfully.")
            return redirect("members")

        logger.error(f"Error occurred while adding member: {form.errors}")

        return render(request, "members/add-member.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MembersListView(View):
    """
    Members List view for the library management system.
    get(): Returns the list of members in the library.
    post(): Returns the list of members in the library based on the search query.
    """

    def get(self, request, *args, **kwargs):
        members = Member.objects.all()
        return render(request, "members/list-members.html", {"members": members})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        members = Member.objects.filter(name__icontains=query)
        return render(request, "members/list-members.html", {"members": members})


@method_decorator(login_required, name="dispatch")
class UpdateMemberDetailsView(View):
    """
    Update Member details view for the library management system.
    get(): Returns the update member page with the UpdateMemberForm.
    post(): Validates the form and updates the member details in the database.
    """

    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(instance=member)
        return render(request, "members/update-member.html", {"form": form, "member": member})

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(request.POST, instance=member)

        if form.is_valid():
            form.save()
            logger.info("Member details updated successfully.")
            return redirect("members")

        logger.error(f"Error occurred while updating member: {form.errors}")

        return render(request, "members/update-member.html", {"form": form, "member": member})


@method_decorator(login_required, name="dispatch")
class DeleteMemberView(View):
    """
    Delete Member view for the library management system.
    get(): Deletes the member from the database.
    """

    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        member.delete()
        logger.info("Member deleted successfully.")
        return redirect("members")


@method_decorator(login_required, name="dispatch")
class AddBookView(View):
    """
    Add Book view for the library management system.
    get(): Returns the add book page with the AddBookForm.
    post(): Validates the form and saves the new book to the database.
    """

    def get(self, request, *args, **kwargs):
        form = AddBookForm()
        return render(request, "books/add-book.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)
            if book.quantity == 0:
                book.status = "not-available"
            else:
                book.status = "available"
            book.save()

            logger.info("New book added successfully.")
            return redirect("books")

        logger.error(f"Error occurred while adding book: {form.errors}")

        return render(request, "books/add-book.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class BooksListView(View):
    """
    Books List view for the library management system.
    get(): Returns the list of books in the library.
    post(): Returns the list of books in the library based on the search query.
    """

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        return render(request, "books/list-books.html", {"books": books})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
        return render(request, "books/list-books.html", {"books": books})


@method_decorator(login_required, name="dispatch")
class UpdateBookDetailsView(View):
    """
    Update Book details view for the library management system.
    get(): Returns the update book page with the AddBookForm.
    post(): Validates the form and updates the book details in the database.
    """

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        form = AddBookForm(instance=book)
        return render(request, "books/update-book.html", {"form": form, "book": book})

    def post(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        form = AddBookForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save(commit=False)
            if book.quantity == 0:
                book.status = "not-available"
            else:
                book.status = "available"
            book.save()

            logger.info("Book details updated successfully.")
            return redirect("books")

        logger.error(f"Error occurred while updating book: {form.errors}")

        return render(request, "books/update-book.html", {"form": form, "book": book})


@method_decorator(login_required, name="dispatch")
class DeleteBookView(View):
    """
    Delete Book view for the library management system.
    get(): Deletes the book from the database.
    """

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        book.delete()
        logger.info("Book deleted successfully.")
        return redirect("books")


@method_decorator(login_required, name="dispatch")
class LendBookView(View):
    """
    Lend Book view for the library management system.
    get(): Returns the lent book page with the LendBookForm and PaymentForm.
    post(): Validates the form and lends the book to the member.
            Several Books can be lent to the member at once.
            if the member has exceeded the borrowing limit, an error message is displayed.
            BorrowedBook and Transaction objects are created and the book quantity is updated.
    """

    def get(self, request, *args, **kwargs):
        form = LendBookForm()
        payment_form = PaymentForm()

        return render(request, "books/lend-book.html", {"form": form, "payment_form": payment_form})

    def post(self, request, *args, **kwargs):
        form = LendBookForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid() and payment_form.is_valid():
            lent_book = form.save(commit=False)
            if lent_book.member.amount_due > 500:
                form.add_error(None, "Member has exceeded the borrowing limit.")
                logger.error("Member has exceeded the borrowing limit.")
            else:
                payment_method = payment_form.cleaned_data["payment_method"]
                books_ids = request.POST.getlist("book")
                amount = 0
                for book_id in books_ids:
                    book = Book.objects.get(pk=book_id)
                    BorrowedBook.objects.create(
                        member=lent_book.member,
                        book=book,
                        return_date=lent_book.return_date,
                        fine=lent_book.fine,
                    )
                    logger.info("Book lent successfully.")

                    book.quantity -= 1
                    book.save()
                    logger.info("Book Quantity updated successfully.")

                    amount += book.borrowing_fee

                Transaction.objects.create(member=lent_book.member, amount=amount, payment_method=payment_method)
                logger.info("Payment made successfully.")

                return redirect("lent-books")

        logger.error(f"Error occurred while issuing book: {form.errors}")

        return render(request, "books/lend-book.html", {"form": form, "payment_form": payment_form})


@method_decorator(login_required, name="dispatch")
class LendMemberBookView(View):
    """
    Lend Member Book view for the library management system.
    Lending a book to a specific member selected from the list of members.
    get(): Returns the lend member book page with the LendMemberBookForm and PaymentForm.
    post(): Validates the form and lends the book to the member.
            Several Books can be lent to the member at once.
            if the member has exceeded the borrowing limit, an error message is displayed.
            BorrowedBook and Transaction objects are created and the book quantity is updated.

    """

    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = LendMemberBookForm()
        payment_form = PaymentForm()
        return render(
            request, "books/lend-member-book.html", {"form": form, "payment_form": payment_form, "member": member}
        )

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = LendMemberBookForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid() and payment_form.is_valid():
            if member.amount_due > 500:
                form.add_error(None, "Member has exceeded the borrowing limit.")
                logger.error("Member has exceeded the borrowing limit.")
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
                    logger.info("Book lent successfully.")

                    book.quantity -= 1
                    book.save()
                    logger.info("Book Quantity updated successfully.")

                    amount += book.borrowing_fee

                Transaction.objects.create(member=member, amount=amount, payment_method=payment_method)
                logger.info("Payment made successfully.")

                return redirect("lent-books")

        logger.error(f"Error occurred while issuing book: {form.errors}")

        return render(
            request, "books/lend-member-book.html", {"form": form, "payment_form": payment_form, "member": member}
        )


@method_decorator(login_required, name="dispatch")
class LentBooksListView(View):
    """
    Lent Books List view for the library management system.
    get(): Returns the list of books that have been lent to members.
    post(): Returns the list of books that have been lent to members based on the search query.
    """

    def get(self, request, *args, **kwargs):
        books = BorrowedBook.objects.select_related("member", "book")
        return render(request, "books/lent-books.html", {"books": books})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        books = BorrowedBook.objects.filter(
            Q(book__title__icontains=query) | Q(book__author__icontains=query)
        ).select_related("member", "book")
        return render(request, "books/lent-books.html", {"books": books})


@method_decorator(login_required, name="dispatch")
class UpdateBorrowedBookView(View):
    """
    Update Borrowed Book view for the library management system. Updates Details of a borrowed book.
    get(): Returns the update borrowed book page with the UpdateBorrowedBookForm.
    post(): Validates the form and updates the borrowed book details in the database.
    """

    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        form = UpdateBorrowedBookForm(instance=book)
        return render(request, "books/update-borrowed-book.html", {"form": form, "book": book})

    def post(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        form = UpdateBorrowedBookForm(request.POST, instance=book)

        if form.is_valid():
            form.save()
            logger.info("Borrowed book details updated successfully.")
            return redirect("lent-books")
        logger.error(f"Error occurred while updating borrowed book: {form.errors}")

        return render(request, "books/update-borrowed-book.html", {"form": form, "book": book})


@method_decorator(login_required, name="dispatch")
class DeleteBorrowedBookView(View):
    """
    Delete Borrowed Book view for the library management system.
    get(): Deletes the borrowed book from the database.
    """

    def get(self, request, *args, **kwargs):
        borrowed_book = BorrowedBook.objects.get(pk=kwargs["pk"])

        book = borrowed_book.book
        book.quantity += 1
        book.save()
        logger.info("Book Quantity updated successfully.")

        borrowed_book.delete()

        logger.info("Borrowed book deleted successfully.")
        return redirect("lent-books")


@method_decorator(login_required, name="dispatch")
class ReturnBookView(View):
    """
    Return Book view for the library management system. Works on a button click.
    get(): Returns the return book page with the PaymentForm.
           if the book is overdue, the user is redirected to the return-book-fine page.
           if the book is not overdue, the book status and the book quantity is updated.
    """

    def get(self, request, *args, **kwargs):
        borrowed_book = BorrowedBook.objects.get(pk=kwargs["pk"])
        if borrowed_book.return_date < timezone.now().date():
            return redirect("return-book-fine", pk=borrowed_book.pk)

        else:
            borrowed_book.returned = True
            borrowed_book.save()
            logger.info("Book returned successfully.")

            book = borrowed_book.book
            book.quantity += 1
            book.save()
            logger.info("Book Quantity updated successfully.")

            return redirect("lent-books")


@method_decorator(login_required, name="dispatch")
class ReturnBookFineView(View):
    """
    Return Book Fine view for the library management system. The page asks for the fine payment for overdue books.
    get(): Returns the return book fine page with the PaymentForm.
    post(): Validates the form and updates the borrowed book status and the book quantity in the database.
            Transaction object is created
    """

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
            logger.info("Book returned successfully.")

            book.book.quantity += 1
            book.book.save()
            logger.info("Book Quantity updated successfully.")

            Transaction.objects.create(member=book.member, amount=fine, payment_method=payment_method)

            return redirect("lent-books")
        logger.error(f"Error occurred while returning book: {form.errors}")

        return render(request, "books/return-book-fine.html", {"book": book, "form": form})


@method_decorator(login_required, name="dispatch")
class ListPaymentsView(View):
    """
    List Payment View for the library management system.
    get(): Returns a list of payments made.
    post(): Returns a list of payments made by a member based on the search query.
    """

    def get(self, request, *args, **kwargs):
        payments = Transaction.objects.select_related("member")
        return render(request, "payments/list-payments.html", {"payments": payments})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        payments = Transaction.objects.filter(member__name__icontains=query).select_related("member")
        return render(request, "payments/list-payments.html", {"payments": payments})


@method_decorator(login_required, name="dispatch")
class DeletePaymentView(View):
    """
    Delete Payment view for the library management system.
    get(): Deletes the payment from the database.
    """

    def get(self, request, *args, **kwargs):
        payment = Transaction.objects.get(pk=kwargs["pk"])
        payment.delete()
        logger.info("Payment deleted successfully.")
        return redirect("payments")


class OverdueBooksView(View):
    """
    Overdue Books view for the library management system.
    get(): Returns a list of overdue books.
    post(): Returns a list of overdue books based on the search query.
    """

    def get(self, request, *args, **kwargs):
        overdue_books = BorrowedBook.objects.filter(
            return_date__lt=timezone.now().date(), returned=False
        ).select_related("member", "book")
        return render(request, "books/overdue-books.html", {"books": overdue_books})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        overdue_books = BorrowedBook.objects.filter(
            Q(book__title__icontains=query) | Q(book__author__icontains=query),
            return_date__lt=timezone.now().date(),
            returned=False,
        ).select_related("member", "book")
        return render(request, "books/overdue-books.html", {"books": overdue_books})
