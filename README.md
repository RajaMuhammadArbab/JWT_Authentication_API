# Django JWT Authentication API

A simple Django REST API with custom JWT (JSON Web Token) authentication, refresh token rotation, and logout functionality.

---

## 🚀 Setup Instructions

1. **Clone project & install dependencies**
   ```bash
   pip install Django>=4.2 djangorestframework>=3.14 PyJWT>=2.8
   ```

2. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will run at:  
```
http://127.0.0.1:8000/api/
```

---

## 🔑 API Endpoints

| Method | Endpoint              | Description |
|--------|-----------------------|-------------|
| POST   | `/api/register/`      | Register a new user |
| POST   | `/api/login/`         | Login with username & password → returns Access & Refresh tokens |
| POST   | `/api/token/refresh/` | Refresh expired Access Token using Refresh Token |
| POST   | `/api/logout/`        | Revoke refresh token (logout) |
| GET    | `/api/protected/`     | Example protected route (requires valid Access Token) |

---

## 📌 Example Usage (Postman or cURL)

### 1️⃣ Register User
**POST** `http://127.0.0.1:8000/api/register/`  
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "test1234"
}
```

### 2️⃣ Login
**POST** `http://127.0.0.1:8000/api/login/`  
```json
{
  "username": "alice",
  "password": "test1234"
}
```

✅ Response:
```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

---

### 3️⃣ Access Protected Route
**GET** `http://127.0.0.1:8000/api/protected/`  
Headers:
```
Authorization: Bearer <ACCESS_TOKEN>
```

✅ Response:
```json
{
  "message": "Hello alice, you have accessed a protected route!"
}
```

---

### 4️⃣ Refresh Token
**POST** `http://127.0.0.1:8000/api/token/refresh/`  
```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

✅ Response:
```json
{
  "access": "<NEW_ACCESS_TOKEN>"
}
```

---

### 5️⃣ Logout (Revoke Token)
**POST** `http://127.0.0.1:8000/api/logout/`  
```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

✅ Response:
```json
{
  "message": "Logged out successfully"
}
```

---

## ⚙️ Notes
- Access token lifetime: **15 minutes**  
- Refresh token lifetime: **7 days**  
- On logout, refresh token is **revoked** and cannot be reused.  
- Always use the **latest Access Token** for protected endpoints.  

---
