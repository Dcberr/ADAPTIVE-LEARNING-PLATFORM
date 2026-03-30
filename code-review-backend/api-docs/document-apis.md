# Document API

## 1. Upload Document

### Endpoint

POST /documents

### Content-Type

multipart/form-data

### Request

| Field       | Type   | Description                      |
| ----------- | ------ | -------------------------------- |
| file        | file   | Document file (pdf, video, etc.) |
| topicId     | UUID   | Topic ID                         |
| title       | string | Document title                   |
| description | string | Description                      |

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Lecture 1",
    "fileUrl": "http://localhost:9000/...",
    "type": "application/pdf"
  }
}
```

---

## 2. Get Documents by Topic

### Endpoint

GET /documents/topic/{topicId}

---

### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Lecture 1",
      "fileUrl": "...",
      "type": "application/pdf"
    }
  ]
}
```

---

## 3. Download Document

### Endpoint

GET /documents/download/{id}

### Description

Open document directly in browser (inline preview)

---

### Response

* File stream (PDF, image, etc.)
* Content-Disposition: inline

---

## 4. Stream Video

### Endpoint

GET /documents/stream/{id}

### Description

Stream video with support for Range header

---

### Headers

| Header | Description |
| ------ | ----------- |
| Range  | bytes=0-    |

---

### Response

* HTTP 206 Partial Content
* Video stream

---

## Authentication

* Required for all endpoints
* Uses JWT or Cookie

---

## Notes

* Upload uses multipart/form-data
* Download returns inline content
* Stream supports video playback in browser
