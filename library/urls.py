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
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Library Management System API",
        default_version='v1',
        description="API documentation for Library Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register-librarian/', RegisterLibrarianView.as_view(), name='register_librarian'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/create-user/', CreateUserView.as_view(), name='create_user'),
    path('api/books/', BookListView.as_view(), name='book_list'),
    path('api/borrow-requests/', BorrowRequestListView.as_view(), name='borrow_requests'),
    path('api/approve-request/<int:pk>/', ApproveBorrowRequestView.as_view(), name='approve_request'),
    
     # Swagger and ReDoc URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
