# Library Management System API

This project is a **Library Management System** backend API built using **Django** and **Django Rest Framework (DRF)**. It allows librarians to manage books, users, and borrow requests while supporting authentication and authorization using **JWT** tokens.
access **redoc** at https://library-management-task1.vercel.app/
access **swagger documentation** at https://library-management-task1.vercel.app/swagger/

---

## Features

1. **Librarian Registration**: Only librarians can register and perform privileged operations.
2. **Authentication**: Supports user login with JWT token generation.
3. **Book Management**:
   - Librarians can create books.
   - List all books available in the library.
4. **User Management**:
   - Librarians can create new library users.
5. **Borrow Requests**:
   - Users can request to borrow books.
   - Librarians can approve or deny borrow requests.

---

## Installation

### Prerequisites

- Python 3.8+
- Django 4+
- Django Rest Framework (DRF)
- Django Rest Framework Simple JWT
- DRF-YASG for Swagger API documentation

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/library-management-system.git
   cd library-management-system

2. Install dependencies:
  ```bash
    pip install -r requirements.txt

3.Run migrations:
  ```bash
  python manage.py makemigrations
  python manage.py migrate

4.Start the development server:

  ```bash  
  python manage.py runserver
  Access the Swagger API Documentation:

**Visit http://127.0.0.1:8000/swagger/ in your browser.**
