from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User, Book, BorrowRequest
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Register Librarian
class RegisterLibrarianView(APIView):
    def post(self, request):
        try:
            data = request.data
            data['is_librarian'] = True
            data['password'] = make_password(data['password'])
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LoginView(APIView):
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
        
        
# Create a New Library User (Admin-only)
class CreateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            if not request.user.is_librarian:
                return Response({"error": "Only librarians can create users."}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data
            data['password'] = make_password(data['password'])
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
