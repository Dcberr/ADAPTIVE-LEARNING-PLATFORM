package com.example.demo.problem.dto;

import java.util.Map;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

/**
 * DTO for updating problem starter code templates
 * Used to upload/update template configurations for a problem
 */
@Data
@Builder
public class UpdateProblemTemplateRequest {

    /**
     * Problem ID to update
     */
    private UUID problemId;

    /**
     * Map of language to template
     * Template format:
     * {{FUNCTION_SIGNATURE}} {
     *     //STUDENT_CODE_HERE
     * }
     * 
     * int main() {
     *     {{INPUT_PARSING}}
     *     {{CALL_FUNCTION}}
     *     {{OUTPUT}}
     *     return 0;
     * }
     */
    private Map<String, String> starterCodes;
}
