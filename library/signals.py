from django.db.models.signals import pre_save
from django.dispatch import receiver

from library.models import BorrowedBook


@receiver(pre_save, sender=BorrowedBook)
def update_book_quantity_on_borrowing(sender, instance, **kwargs):
    if instance.book.quantity > 1:
        instance.book.status = "available"
    else:
        instance.book.status = "not-available"
