from django.urls import path, re_path
from .views import (
    RegisterLibrarianView,
    CreateUserView,
    BookListView,
    BorrowRequestListView,
    ApproveBorrowRequestView,
    LoginView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register-librarian/', RegisterLibrarianView.as_view(), name='register_librarian'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/create-user/', CreateUserView.as_view(), name='create_user'),
    path('api/books/', BookListView.as_view(), name='book_list'),
    path('api/borrow-requests/', BorrowRequestListView.as_view(), name='borrow_requests'),
    path('api/approve-request/<int:pk>/', ApproveBorrowRequestView.as_view(), name='approve_request'),
    
    
]
