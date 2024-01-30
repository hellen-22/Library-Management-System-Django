from django.contrib import admin

from .models import Book, BorrowedBook, Member

admin.site.register(Book)
admin.site.register(BorrowedBook)
admin.site.register(Member)
