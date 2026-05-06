package com.example.demo.submission.repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.demo.submission.dto.SubmissionOverviewResponse;
import com.example.demo.submission.dto.SubmissionResponse;
import com.example.demo.submission.entity.Submission;

@Repository
public interface SubmissionRepository
        extends JpaRepository<Submission, UUID> {
    List<Submission> findByUserId(UUID userId);

    List<Submission> findByProblemId(UUID problemId);

    List<Submission> findByProblemIdAndIdNot(UUID problemId, UUID submissionId);

    @Query(value = """
        SELECT 
            s.id AS submissionId,
            a.title AS assignmentTitle,
            p.title AS problemTitle,
            s.score AS score,
            p.difficulty AS difficulty,
            a.deadline AS deadline,
            s.status AS status,
            s.submitted_at AS submittedAt,
            u.name as studentName
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        JOIN assignment_problems ap ON ap.problem_id = p.id
        JOIN assignments a ON ap.assignment_id = a.id
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.user_id = :userId
    """, nativeQuery = true)
    List<SubmissionOverviewResponse> getSubmissionOverview(UUID userId);

    Optional<Submission> findById(UUID id);

    @Query(value = """
        SELECT
            s.id AS submissionId,
            a.title AS assignmentTitle,
            p.title AS problemTitle,
            s.score AS score,
            p.difficulty AS difficulty,
            a.deadline AS deadline,
            s.status AS status,
            s.submitted_at AS submittedAt,
            u.name as studentName
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        LEFT JOIN assignment_problems ap ON ap.problem_id = p.id
        LEFT JOIN assignments a ON ap.assignment_id = a.id
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.problem_id = :problemId
        ORDER BY s.created_at DESC
    """, nativeQuery = true)
    List<SubmissionOverviewResponse> getSubmissionOverviewByProblem(UUID problemId);
    
    @Query(value = """
        SELECT new com.example.demo.submission.dto.SubmissionResponse(
            s.id,
            s.userId,
            s.status,
            a.createdAt,
            s.submittedAt,
            s.score,
            u.name
        )
        FROM Submission s
        JOIN Problem p ON s.problemId = p.id
        JOIN AssignmentProblem ap ON ap.problemId = p.id
        JOIN Assignment a ON ap.assignmentId = a.id
        LEFT JOIN User u ON s.userId = u.id
        WHERE s.userId = :userId AND a.id = :assignmentId
        ORDER BY s.submittedAt DESC
    """)
    List<SubmissionResponse> getUserSubmissionsByAssignmentId(UUID userId, UUID assignmentId);

        @Query(value = """
            SELECT new com.example.demo.submission.dto.SubmissionResponse(
                s.id,
                s.userId,
                s.status,
                a.createdAt,
                s.submittedAt,
                s.score,
                u.name
            )
            FROM Submission s
            JOIN Problem p ON s.problemId = p.id
            JOIN AssignmentProblem ap ON ap.problemId = p.id
            JOIN Assignment a ON ap.assignmentId = a.id
            LEFT JOIN User u ON s.userId = u.id
            WHERE a.id = :assignmentId
            ORDER BY s.submittedAt DESC
        """)
        List<SubmissionResponse> getAllSubmissionsByAssignmentId(UUID assignmentId);

    @Query(value = """
        SELECT s
        FROM Submission s
        JOIN Problem p ON s.problemId = p.id
        WHERE s.userId = :userId AND p.id = :problemId
    """)
    List<Submission> getAllSubmissionsByProblemIdAndUserId(UUID userId, UUID problemId);

    @Query(value = """
        SELECT COUNT(s)
        FROM Submission s
        JOIN AssignmentProblem ap ON ap.problemId = s.problemId
        WHERE s.userId = :userId AND ap.assignmentId = :assignmentId
    """)
    long countByUserIdAndAssignmentId(UUID userId, UUID assignmentId);

    @Query("""
        SELECT DISTINCT s.problemId
        FROM Submission s
        WHERE s.userId = :userId
        ORDER BY s.problemId
    """)
    List<UUID> findDistinctProblemIdsByUserId(UUID userId);

}
