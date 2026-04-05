# Class API

## 1. Create Class

### Endpoint

POST /classes

### Description

Create a new class (Instructor only)

### Content-Type

multipart/form-data

### Request

| Field       | Type   | Description |
| ----------- | ------ | ----------- |
| name        | string | Class name  |
| description | string | Description |

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Class A"
  }
}
```

---

## 2. Get My Classes

### Endpoint

GET /classes/me

### Description

Get all classes of current user

---

### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Class A"
    }
  ]
}
```

---

## 3. Add Student

### Endpoint

POST /classes/{classId}/students

### Request Body

```json
{
  "studentId": "uuid"
}
```

---

### Response

```json
{
  "success": true
}
```

---

## 4. Remove Student

### Endpoint

DELETE /classes/{classId}/students/{studentId}

---

### Response

```json
{
  "success": true
}
```

---

## 5. Get Class Detail

### Endpoint

GET /classes/{classId}

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Class A",
    "students": [],
    "topics": []
  }
}
```

---

## Authentication

* Required for all endpoints
* Uses JWT (Authorization header) or Cookie

---

## Notes

* Instructor can manage class
* Student can only view joined classes
