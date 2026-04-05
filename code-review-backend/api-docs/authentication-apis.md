# Auth API

## 1. Get Current User

### Endpoint

GET /auth/me

### Description

Get information of the currently authenticated user

---

### Headers

| Header        | Value                 |
| ------------- | --------------------- |
| Authorization | Bearer <access_token> |

*(Nếu bạn dùng cookie thì không cần header này)*

---

### Request

```http
GET /auth/me
```

---

### Response

```json
{
  "success": true,
  "message": "Success",
  "data": "user-uuid"
}
```

---

### Response (Recommended)

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "user-uuid"
  }
}
```

---

### Error Response

```json
{
  "success": false,
  "message": "Unauthorized"
}
```

---

### Notes

* API requires authentication
* User identity is extracted from JWT / session
