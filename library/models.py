from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from users.models import AbstractBaseModel

STATUS_CHOICES = (
    ("available", "Available"),
    ("not-available", "Not-Available"),
)

CATEGORY_CHOICES = (
    ("fiction", "Fiction"),
    ("non-fiction", "Non-Fiction"),
    ("biography", "Biography"),
    ("history", "History"),
    ("science", "Science"),
    ("poetry", "Poetry"),
    ("drama", "Drama"),
    ("religion", "Religion"),
    ("children", "Children"),
    ("other", "Other"),
)

PAYMENT_METHOD_CHOICES = (
    ("cash", "Cash"),
    ("mpesa", "Mpesa"),
    ("card", "Card"),
)


class Member(AbstractBaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00), MaxValueValidator(500.00)]
    )

    def __str__(self):
        return f"{self.name}"

    def calculate_amount_due(self):
        borrowed_books = self.borrowed_books.all()
        amount = 0
        for book in borrowed_books:
            if book.return_date < timezone.now().date() and not book.returned:
                amount += book.fine

        return amount


class Book(AbstractBaseModel):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    borrowing_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(1.00)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"{self.title} by {self.author}"


class BorrowedBook(AbstractBaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="borrowed_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowed_books")
    return_date = models.DateField()
    returned = models.BooleanField(default=False)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])

    def __str__(self):
        return f"{self.member.name} borrowed {self.book.title} on {self.created_at}"


class Transaction(AbstractBaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"{self.member.name} paid {self.amount} via {self.payment_method}"
