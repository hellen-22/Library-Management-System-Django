from django.urls import path

from .views import AddMemberView, DeleteMemberView, HomeView, MembersListView, UpdateMemberDetailsView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add-member/", AddMemberView.as_view(), name="add-member"),
    path("members/", MembersListView.as_view(), name="members"),
    path("edit-member-details/<str:pk>/", UpdateMemberDetailsView.as_view(), name="update-member"),
    path("delete-member/<str:pk>/", DeleteMemberView.as_view(), name="delete-member"),
]
