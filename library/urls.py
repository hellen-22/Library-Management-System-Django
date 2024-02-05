from django.urls import path

from .views import (
    AddBookView,
    AddMemberView,
    BooksListView,
    ChangeBorrowedBookStatusView,
    DeleteBookView,
    DeleteMemberView,
    HomeView,
    IssueBookView,
    IssuedBooksListView,
    IssueMemberBookView,
    MembersListView,
    UpdateBookDetailsView,
    UpdateMemberDetailsView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add-member/", AddMemberView.as_view(), name="add-member"),
    path("members/", MembersListView.as_view(), name="members"),
    path("edit-member-details/<str:pk>/", UpdateMemberDetailsView.as_view(), name="update-member"),
    path("delete-member/<str:pk>/", DeleteMemberView.as_view(), name="delete-member"),
    path("add-book/", AddBookView.as_view(), name="add-book"),
    path("books/", BooksListView.as_view(), name="books"),
    path("edit-book-details/<str:pk>/", UpdateBookDetailsView.as_view(), name="update-book"),
    path("delete-book/<str:pk>/", DeleteBookView.as_view(), name="delete-book"),
    path("issue-book/", IssueBookView.as_view(), name="issue-book"),
    path("issue-book/<str:pk>/", IssueMemberBookView.as_view(), name="issue-member-book"),
    path("issued-books/", IssuedBooksListView.as_view(), name="issued-books"),
    path(
        "change-borrowed-book-status/<str:pk>/",
        ChangeBorrowedBookStatusView.as_view(),
        name="change-borrowed-book-status",
    ),
]
