import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)  
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    mobile_number = models.CharField(
        max_length=15,
        unique=True,
        null=False,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    is_librarian = models.BooleanField(default=False)
    
    #we are not using username so make it blank , null, non unique
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    
    USERNAME_FIELD = 'email'  # Set email as the login field
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile_number']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({'Librarian' if self.is_librarian else 'User'})"

class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='available')  # available or borrowed

class BorrowRequest(models.Model):
    borrow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='pending')  # pending, approved, denied
