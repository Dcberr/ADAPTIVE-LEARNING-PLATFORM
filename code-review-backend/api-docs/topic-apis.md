# Topic API

## 1. Create Topic

### Endpoint

POST /topics

---

### Description

Create a new topic inside a class

---

### Request Body

```json
{
  "classId": "uuid",
  "title": "Week 1",
  "description": "Introduction to algorithms"
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Week 1"
  }
}
```

---

## 2. Get Topics Overview by Class

### Endpoint

GET /topics/class/{classId}

---

### Description

Get list of topics in a class (lightweight overview)

---

### Response

```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "id": "uuid",
        "title": "Week 1",
        "assignmentCount": 3,
        "documentCount": 5
      }
    ]
  }
}
```

---

## 3. Get Topic Detail

### Endpoint

GET /topics/{topicId}

---

### Description

Get full topic detail including assignments and documents

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Week 1",
    "description": "Intro",
    "assignments": [
      {
        "id": "uuid",
        "title": "Assignment 1"
      }
    ],
    "documents": [
      {
        "id": "uuid",
        "title": "Lecture PDF"
      }
    ]
  }
}
```

---

## Authentication

* Required for all endpoints

---

## Notes

* Overview API is lightweight for listing
* Detail API returns full nested data
