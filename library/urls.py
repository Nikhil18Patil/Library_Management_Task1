from django.urls import path, re_path
from .views import (
    RegisterLibrarianView,
    CreateUserView,
    BookCreateView,
    BookListView,
    BorrowRequestListView,
    ApproveBorrowRequestView,
    LoginView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register-librarian/', RegisterLibrarianView.as_view(), name='register_librarian'),
    path('login/', LoginView.as_view(), name='login'),
    path('create-user/', CreateUserView.as_view(), name='create_user'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('create-book/', BookCreateView.as_view(), name='create_book'),
    path('borrow-requests/', BorrowRequestListView.as_view(), name='borrow_requests'),
    path('approve-request/<str:borrow_id>/', ApproveBorrowRequestView.as_view(), name='approve_request'),
    
    
]
