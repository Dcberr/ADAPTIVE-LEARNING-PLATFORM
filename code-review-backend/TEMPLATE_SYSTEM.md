# Starter Code Template System

## Overview

The template system allows problems to define a generic template with placeholders, hiding boilerplate code from students while maintaining full code structure for execution.

## Template Format

```cpp
#include <bits/stdc++.h>
using namespace std;

{{FUNCTION_SIGNATURE}} {
    //STUDENT_CODE_HERE
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    {{INPUT_PARSING}}

    {{CALL_FUNCTION}}

    {{OUTPUT}}

    return 0;
}
```

## Placeholders

- **`{{FUNCTION_SIGNATURE}}`** - Function signature to implement (e.g., `int solve(int n)`)
- **`//STUDENT_CODE_HERE`** - Student's code placeholder
- **`{{INPUT_PARSING}}`** - Code to parse input (executed in main)
- **`{{CALL_FUNCTION}}`** - Code to call the function
- **`{{OUTPUT}}`** - Code to output result

## API Usage

### 1. Create Problem with Template

```bash
POST /problems
Content-Type: application/json

{
  "description": "Find sum of array",
  "problemConstraint": "n <= 1000",
  "assignmentId": "uuid",
  "starterCodes": {
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\n{{FUNCTION_SIGNATURE}} {\n    //STUDENT_CODE_HERE\n}\n\nint main() {\n    {{INPUT_PARSING}}\n    {{CALL_FUNCTION}}\n    {{OUTPUT}}\n    return 0;\n}",
    "java": "public class Solution {\n    {{FUNCTION_SIGNATURE}} {\n        //STUDENT_CODE_HERE\n    }\n\n    public static void main(String[] args) {\n        {{INPUT_PARSING}}\n        {{CALL_FUNCTION}}\n        {{OUTPUT}}\n    }\n}"
  },
  "testcases": [
    {
      "input": "3",
      "expectedOutput": "6",
      "isHidden": false
    }
  ]
}
```

### 2. Get Problem (Returns Function Skeleton)

```bash
GET /problems/{problemId}
```

Response:
```json
{
  "id": "uuid",
  "description": "Find sum of array",
  "problemConstraint": "n <= 1000",
  "functionSkeletons": {
    "cpp": "int solve(int n) {\n    //STUDENT_CODE_HERE\n}",
    "java": "public static int solve(int n) {\n    //STUDENT_CODE_HERE\n}"
  }
}
```

### 3. Update Problem Templates

```bash
PUT /problems/templates
Content-Type: application/json

{
  "problemId": "uuid",
  "starterCodes": {
    "cpp": "... updated template ..."
  }
}
```

### 4. Run Code (ExecutionService)

When student submits code:

```bash
POST /execution/run-by-testcase
Content-Type: application/json

{
  "problemId": "uuid",
  "language": "cpp",
  "code": "return n * (n + 1) / 2;"
}
```

Internally:
1. Fetch problem template from starterCodes
2. Replace `//STUDENT_CODE_HERE` with student code
3. Compile full code (with main, I/O, etc.)
4. Run against testcases

## Backward Compatibility

- Field renamed from `starterCodeTemplates` to `starterCodes`
- No backward compatibility layer needed - single field supports everything

## Database Schema

### Table: `problems`
- `id` UUID (PK)
- `title` TEXT
- `description` TEXT
- `problem_constraint` TEXT
- `created_at` TIMESTAMP
- ...

### Table: `problem_starter_codes` (ElementCollection)
- `problem_id` UUID (FK)
- `language` VARCHAR (key)
- `starter_code` TEXT (deprecated)

### Table: `problem_starter_code_templates` (ElementCollection)
- `problem_id` UUID (FK)
- `language` VARCHAR (key)
- `starter_code_template` TEXT

## Example: C++ Problem

### 1. Create Problem
Templates define the full structure:

```cpp
#include <bits/stdc++.h>
using namespace std;

int solve(int n) {
    //STUDENT_CODE_HERE
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n;
    cin >> n;
    
    cout << solve(n);
    
    return 0;
}
```

### 2. Student Views
Student sees only the function:

```cpp
int solve(int n) {
    //STUDENT_CODE_HERE
}
```

### 3. Student Submits
Student code: `return n * (n + 1) / 2;`

### 4. System Executes
Full code (compiled & executed):

```cpp
#include <bits/stdc++.h>
using namespace std;

int solve(int n) {
    return n * (n + 1) / 2;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n;
    cin >> n;
    
    cout << solve(n);
    
    return 0;
}
```

## Implementation Notes

### CodeExtractor Utility

- **`extractFunctionSkeleton(template)`** - Extracts function part (starts at `{{FUNCTION_SIGNATURE}}`, ends before `main()`)
- **`combineWithStudentCode(template, studentCode)`** - Replaces `//STUDENT_CODE_HERE` placeholder
- **`extractFunctionSignature(template)`** - Extracts just the function signature

### Service Flow

1. **ProblemService** - Maps template to function skeleton for API responses
2. **ExecutionService** - Uses full template to combine + execute
3. **Frontend** - Displays function skeleton to student

## Future Enhancements

- Support multi-function problems
- Template validation before save
- Template versioning
- Language-specific template helpers
