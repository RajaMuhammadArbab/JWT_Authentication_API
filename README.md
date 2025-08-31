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
## PROJECT-DEMO ##
## 1 ##
<img width="1371" height="554" alt="1" src="https://github.com/user-attachments/assets/139aef8e-2bf1-4e6d-b4cb-128bf09ff1d9" />
## 2 ##
<img width="1363" height="688" alt="2" src="https://github.com/user-attachments/assets/d9397c29-7062-4cc9-aa68-ffb873134681" />
## 3 ##
<img width="1368" height="433" alt="3" src="https://github.com/user-attachments/assets/998ec483-f190-4f6d-8a7e-742bfbd1c964" />
## 4 ##
<img width="1383" height="686" alt="5" src="https://github.com/user-attachments/assets/3ec89142-2c62-4935-910e-c98b9a817f33" />
## 5 ##
<img width="1378" height="558" alt="4" src="https://github.com/user-attachments/assets/51b48ffe-625a-46df-97fd-9b982c3aeee6" />
