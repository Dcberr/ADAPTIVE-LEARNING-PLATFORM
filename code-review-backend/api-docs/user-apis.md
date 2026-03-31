# User API

## 1. Get Current User

### Endpoint

GET /users/me

---

### Description

Get profile of the currently authenticated user

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Nguyen Van A",
    "email": "user@example.com",
    "role": "STUDENT",
    "picture": "https://..."
  }
}
```

---

## 2. Get User by ID

### Endpoint

GET /users/{id}

---

### Description

Get public user information by ID

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Nguyen Van A",
    "picture": "https://..."
  }
}
```

---

## 3. Update Profile

### Endpoint

PUT /users/me

---

### Description

Update current user profile

---

### Request Body

```json
{
  "name": "New Name",
  "picture": "https://new-avatar.com"
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "New Name"
  }
}
```

---

## Authentication

* Required for `/me` endpoints
* Uses JWT or Cookie

---

## Notes

* `/users/{id}` should return only public information
* Sensitive data (email, role) should be restricted if needed
