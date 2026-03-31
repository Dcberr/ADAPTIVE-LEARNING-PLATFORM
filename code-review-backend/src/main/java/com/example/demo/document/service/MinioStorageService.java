package com.example.demo.document.service;

import java.io.InputStream;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.document.dto.UploadFilleResponse;
import com.example.demo.document.entity.Document;
import com.example.demo.document.repository.DocumentRepository;

import io.minio.BucketExistsArgs;
import io.minio.GetObjectArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.StatObjectArgs;
import io.minio.StatObjectResponse;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class MinioStorageService {

    private final MinioClient minioClient;
    private final DocumentRepository documentRepository;

    @Value("${minio.bucket}")
    private String bucket;

    public UploadFilleResponse upload(MultipartFile file) {
        try {
            String objectName = generateFileName(file.getOriginalFilename());

            ensureBucketExists();

            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .stream(file.getInputStream(), file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );

            return UploadFilleResponse.builder() 
                    .fileUrl(getFileUrl(objectName)) 
                    .type(file.getContentType())
                    .build();

        } catch (Exception e) {
            throw new RuntimeException("Upload to MinIO failed", e);
        }
    }

    private void ensureBucketExists() throws Exception {
        boolean exists = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucket).build()
        );

        if (!exists) {
            minioClient.makeBucket(
                    MakeBucketArgs.builder().bucket(bucket).build()
            );
        }
    }

    private String generateFileName(String originalName) {
        String ext = originalName.substring(originalName.lastIndexOf('.') + 1);
        return "uploads/" + UUID.randomUUID() + "." + ext;
    }

    private String getFileUrl(String objectName) {
        return String.format("%s/%s/%s",
                "http://localhost:9000",
                bucket,
                objectName);
    }


    public ResponseEntity<Resource> download(String fileUrl, String fileName, String fileType) {
        // Implement download logic if needed

        try {

            String objectName = extractObjectName(fileUrl);

            InputStream stream = minioClient.getObject(
                    io.minio.GetObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .build()
            );

            InputStreamResource resource = new InputStreamResource(stream); 

            // String fileName = objectName.substring(objectName.lastIndexOf("/") + 1);

            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, 
                        "inline; filename=\"" + fileName + "\"")
                .contentType(MediaType.parseMediaType(fileType))
                .body(resource);

        } catch (Exception e) {
            throw new RuntimeException("Download from MinIO failed", e);
        }
           
    }

    private String extractObjectName(String url) {
        // http://localhost:9000/bucket/uploads/abc.pdf
        return url.substring(url.indexOf(bucket) + bucket.length() + 1);
    }

    public ResponseEntity<Resource> stream(String documentId, String rangeHeader) {

        Document document = documentRepository.findById(UUID.fromString(documentId))
                .orElseThrow(() -> new RuntimeException("Document not found"));

        try {
            String objectName = extractObjectName(document.getFileUrl());

            StatObjectResponse stat = minioClient.statObject(
                    StatObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .build()
            );

            long fileSize = stat.size();

            long start = 0;
            long end = fileSize - 1;

            if (rangeHeader != null && rangeHeader.startsWith("bytes=")) {
                String[] ranges = rangeHeader.substring(6).split("-");
                start = Long.parseLong(ranges[0]);
                if (ranges.length > 1 && !ranges[1].isEmpty()) {
                    end = Long.parseLong(ranges[1]);
                }
            }

            long contentLength = end - start + 1;

            InputStream stream = minioClient.getObject(
                    GetObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .offset(start)
                            .length(contentLength)
                            .build()
            );

            return ResponseEntity.status(rangeHeader == null ? 200 : 206)
                    .header(HttpHeaders.CONTENT_TYPE, document.getType())
                    .header(HttpHeaders.ACCEPT_RANGES, "bytes")
                    .header(HttpHeaders.CONTENT_LENGTH, String.valueOf(contentLength))
                    .header(HttpHeaders.CONTENT_RANGE,
                            "bytes " + start + "-" + end + "/" + fileSize)
                    .body(new InputStreamResource(stream));

        } catch (Exception e) {
            throw new RuntimeException("Stream failed", e);
        }
    }
}
