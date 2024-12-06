# serializers.py
from rest_framework import serializers
from .models import User, Book, BorrowRequest
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'mobile_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)
    
    def to_representation(self, instance):
        representation= super().to_representation(instance)
        representation['is_librarian']=instance.is_librarian
        
        return representation

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_id', 'title', 'author', 'status']

class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['borrow_id', 'book', 'start_date', 'end_date' ,'status']
        extra_kwargs={
            'status':{'read_only':True}
        }
    
    def to_representation(self, instance):
        representation= super().to_representation(instance)
        user=instance.user
        representation['email']=user.email
        representation['name']=f"{user.first_name} {user.last_name}"
        
        return representation
