from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User, Book, BorrowRequest
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterLibrarianView(APIView):
    @swagger_auto_schema(
        operation_id="Register the Librarian",
        operation_description="Register a librarian to manage library operations. Only librarians can register new users.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="Librarian registered successfully.",
                examples={"application/json": {"id": 1, "username": "admin", "first_name": "John", "last_name": "Doe", "mobile_number": "1234567890"}}
            ),
            400: openapi.Response(
                description="Validation error in input data.",
                examples={"application/json": {"username": ["This field must be unique."]}}
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}}
            ),
        },
    )
    def post(self, request):
        try:
            data = request.data
            data['is_librarian'] = True
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login
class LoginView(APIView):
    @swagger_auto_schema(
        operation_id="Login User",
        operation_description="Authenticate a user and generate JWT tokens (access and refresh).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
            required=["username", "password"],
        ),
        responses={
            200: openapi.Response(
                description="User authenticated successfully.",
                examples={"application/json": {"access": "jwt_token", "refresh": "refresh_token", "user_id": 1, "username": "admin"}}
            ),
            400: openapi.Response(
                description="Bad request, missing fields.",
                examples={"application/json": {"error": "Please provide both username and password."}}
            ),
            401: openapi.Response(
                description="Unauthorized, invalid credentials.",
                examples={"application/json": {"error": "Invalid credentials."}}
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}}
            ),
        },
    )
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({"error": "Please provide both username and password."}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create a New Library User
class CreateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id="Create a New Library User",
        operation_description="Create a new library user. Only librarians are allowed to perform this action.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully.",
                examples={"application/json": {"id": 2, "username": "user1", "first_name": "Alice", "last_name": "Smith", "mobile_number": "9876543210"}}
            ),
            403: openapi.Response(
                description="Forbidden. Only librarians can perform this action.",
                examples={"application/json": {"error": "Only librarians can create users."}}
            ),
            400: openapi.Response(
                description="Validation error in input data.",
                examples={"application/json": {"username": ["This field must be unique."]}}
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}}
            ),
        },
    )
    def post(self, request):
        try:
            if not request.user.is_librarian:
                return Response({"error": "Only librarians can create users."}, status=status.HTTP_403_FORBIDDEN)

            data = request.data
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# List All Books
class BookListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id="List All Books",
        operation_description="Retrieve a list of all books in the library.",
        responses={
            200: openapi.Response(
                description="List of books retrieved successfully.",
                examples={"application/json": [{"id": 1, "title": "Book A", "author": "Author A", "status": "available"}]}
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}}
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization", openapi.IN_HEADER, description="Bearer Token", type=openapi.TYPE_STRING, required=True
            )
        ],
    )
    def get(self, request):
        try:
            books = Book.objects.all()
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Borrow Request Handling
class BorrowRequestListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id="List Borrow Requests",
        operation_description=(
            "Retrieve a list of all borrow requests. Librarians see all requests, while regular users see only their own."
        ),
        responses={
            200: openapi.Response(
                description="List of borrow requests retrieved successfully.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user": 2,
                            "book": 1,
                            "start_date": "2024-12-01",
                            "end_date": "2024-12-15",
                            "status": "pending",
                        }
                    ]
                },
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}},
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization", openapi.IN_HEADER, description="Bearer Token", type=openapi.TYPE_STRING, required=True
            )
        ],
    )
    def get(self, request):
        try:
            if request.user.is_librarian:
                requests = BorrowRequest.objects.all()
            else:
                requests = BorrowRequest.objects.filter(user=request.user)
            serializer = BorrowRequestSerializer(requests, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_id="Create Borrow Request",
        operation_description="Create a new borrow request for a book.",
        request_body=BorrowRequestSerializer,
        responses={
            201: openapi.Response(
                description="Borrow request created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 2,
                        "book": 1,
                        "start_date": "2024-12-01",
                        "end_date": "2024-12-15",
                        "status": "pending",
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error or overlapping borrow dates.",
                examples={"application/json": {"error": "Book is already borrowed during this period."}},
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}},
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization", openapi.IN_HEADER, description="Bearer Token", type=openapi.TYPE_STRING, required=True
            )
        ],
    )
    def post(self, request):
        try:
            data = request.data
            data['user'] = request.user.id  # Associate the request with the logged-in user

            # Check for overlapping borrow dates
            book_id = data.get('book')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            overlapping_request = BorrowRequest.objects.filter(
                book_id=book_id,
                status='approved',
                start_date__lt=end_date,
                end_date__gt=start_date
            ).exists()

            if overlapping_request:
                return Response({"error": "Book is already borrowed during this period."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = BorrowRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Approve or Deny Borrow Request
class ApproveBorrowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id="Approve or Deny Borrow Request",
        operation_description="Approve or deny a borrow request. Only librarians are allowed to perform this action.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["approved", "denied"],
                    description="Set the status to either 'approved' or 'denied'.",
                )
            },
            required=["status"],
        ),
        responses={
            200: openapi.Response(
                description="Request status updated successfully.",
                examples={"application/json": {"message": "Request approved successfully."}},
            ),
            403: openapi.Response(
                description="Forbidden. Only librarians can approve or deny requests.",
                examples={"application/json": {"error": "Only librarians can approve or deny requests."}},
            ),
            404: openapi.Response(
                description="Borrow request not found.",
                examples={"application/json": {"error": "Borrow request not found."}},
            ),
            400: openapi.Response(
                description="Invalid status or book already borrowed.",
                examples={"application/json": {"error": "Invalid status."}},
            ),
            500: openapi.Response(
                description="Internal server error.",
                examples={"application/json": {"error": "Unexpected error occurred."}},
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization", openapi.IN_HEADER, description="Bearer Token", type=openapi.TYPE_STRING, required=True
            )
        ],
    )
    def put(self, request, pk):
        try:
            if not request.user.is_librarian:
                return Response({"error": "Only librarians can approve or deny requests."}, status=status.HTTP_403_FORBIDDEN)

            borrow_request = BorrowRequest.objects.get(pk=pk)
            status_update = request.data.get('status', 'denied')

            if status_update not in ['approved', 'denied']:
                return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

            borrow_request.status = status_update
            if status_update == 'approved':
                book = borrow_request.book
                if book.status == 'borrowed':
                    return Response({"error": "Book is already borrowed."}, status=status.HTTP_400_BAD_REQUEST)
                book.status = 'borrowed'
                book.save()

            borrow_request.save()
            return Response({"message": f"Request {status_update} successfully."})
        except BorrowRequest.DoesNotExist:
            return Response({"error": "Borrow request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
