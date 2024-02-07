from django.contrib import admin

from .models import Book, BorrowedBook, Member, Transaction

admin.site.register(Book)
admin.site.register(BorrowedBook)
admin.site.register(Member)
admin.site.register(Transaction)
