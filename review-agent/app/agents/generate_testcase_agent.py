import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from openai import OpenAI

from app.models.generate_testcase import GenerateTestcase
from app.models.logic_issue import create_logic_issue
from app.models.review_state import ReviewState
from app.tools.execution_run_tool import ExecutionRunTool
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class GenerateTestcaseAgent:
    """Generate exploratory testcases and convert their findings into logic issues."""

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        execution_tool: ExecutionRunTool,
    ):
        self.client = client
        self.model_name = model_name
        self.execution_tool = execution_tool
        self.max_parallel_runs = 3

    def generate_messages(
        self,
        *,
        code: str,
        language: str,
        assignment_requirements: str,
        expected_concepts: list[str],
    ) -> list[dict[str, str]]:
        system_msg = {
            "role": "system",
            "content": (
                "You are a CS1 teaching assistant who designs short exploratory "
                "program inputs. Return valid JSON only."
            ),
        }
        user_msg = {
            "role": "user",
            "content": f"""
Student language: {language}
Assignment requirements: {assignment_requirements}
Expected concepts: {expected_concepts}

Student code:
{code}

Generate 3 exploratory stdin testcases for this student code.

Return JSON in this shape:
{{
  "testcases": [
    {{
      "input": "raw stdin",
      "reason": "short explanation"
    }}
  ]
}}

Rules:
- Keep inputs realistic for the assignment.
- Prefer representative cases and edge cases.
- Do not include expected output because the program will be executed separately.
- Return JSON only.
            """,
        }
        return [system_msg, user_msg]

    def generate_issue_messages(
        self,
        *,
        code: str,
        executed_testcases: list[GenerateTestcase],
    ) -> list[dict[str, str]]:
        system_msg = {
            "role": "system",
            "content": (
                "You are a CS1 debugging tutor. Review exploratory execution results "
                "and identify likely logic problems. Return valid JSON only."
            ),
        }
        user_msg = {
            "role": "user",
            "content": f"""
Student code:
{code}

Executed exploratory testcases:
{executed_testcases}

Task:
Review the executed testcases above. If any testcase suggests a likely logic problem,
return it in this shape:
{{
  "logic_issues": [
    {{
      "issue": "short explanation",
      "evidence": testcase id,
      "code_snippet": "relevant code snippet",
      "location": {{
        "start_line": line_number,
        "end_line": line_number,
        "start_col": column_number,
        "end_col": column_number
      }}
    }}
  ]
}}

Rules:
- Only include likely logic issues.
- If nothing looks wrong, return an empty list.
- Use the testcase id exactly from the provided testcase data.
- Return JSON only.
            """,
        }
        return [system_msg, user_msg]

    def _execute_generated_testcase(
        self,
        *,
        testcase_id: int,
        stdin: str,
        reason: str,
        language: str,
        code: str,
    ) -> GenerateTestcase:
        try:
            execution_result = self.execution_tool.run_code(
                language=language,
                code=code,
                stdin=stdin,
            )
            run_data = execution_result.get("data") or {}
            testcase_results = run_data.get("testcases") or []
            primary_result = testcase_results[0] if testcase_results else {}

            return {
                "id": testcase_id,
                "input": stdin,
                "expected_output": primary_result.get("output", ""),
                "status": run_data.get("status", "UNKNOWN"),
                "reason": reason or "Generated exploratory testcase.",
                "error": primary_result.get("error", ""),
            }
        except Exception as exc:
            logger.exception(
                "GenerateTestcaseAgent execution failed for generated testcase %s",
                testcase_id,
            )
            return {
                "id": testcase_id,
                "input": stdin,
                "expected_output": "",
                "status": "EXECUTION_ERROR",
                "reason": reason or "Generated exploratory testcase.",
                "error": str(exc),
            }

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        logger.debug(
            "Starting GenerateTestcaseAgent with state summary: %s",
            summarize_state(state),
        )

        new_state: ReviewState = dict(state)
        if new_state.get("logic_issues"):
            logger.debug("GenerateTestcaseAgent skipped because logic issues exist")
            new_state["generated_testcases"] = []
            return new_state

        try:
            messages = self.generate_messages(
                code=new_state.get("code", ""),
                language=new_state.get("assignment_language", ""),
                assignment_requirements=new_state.get("assignment_requirements", ""),
                expected_concepts=new_state.get("expected_concepts", []),
            )
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            model_text = response.choices[0].message.content
            logger.debug(
                "GenerateTestcaseAgent raw response preview: %s",
                truncate_text(model_text),
            )
            parsed = safe_parse_json_response(model_text)
            generated_testcases: list[GenerateTestcase] = []
            generated_logic_issues: Dict[int, Any] = {}
            execution_jobs: list[tuple[int, str, str]] = []

            for case_index, candidate in enumerate(parsed.get("testcases", [])[:3], start=1):
                stdin = candidate.get("input", "")
                reason = candidate.get("reason", "").strip()
                if not stdin:
                    continue

                testcase_id = 10_000 + case_index
                execution_jobs.append((testcase_id, stdin, reason))

            if execution_jobs:
                logger.debug(
                    "GenerateTestcaseAgent running %s generated testcases in parallel",
                    len(execution_jobs),
                )
                with ThreadPoolExecutor(
                    max_workers=min(self.max_parallel_runs, len(execution_jobs))
                ) as executor:
                    futures = {
                        executor.submit(
                            self._execute_generated_testcase,
                            testcase_id=testcase_id,
                            stdin=stdin,
                            reason=reason,
                            language=new_state.get("assignment_language", ""),
                            code=new_state.get("code", ""),
                        ): testcase_id
                        for testcase_id, stdin, reason in execution_jobs
                    }
                    completed_testcases: list[GenerateTestcase] = []
                    for future in as_completed(futures):
                        completed_testcases.append(future.result())

                generated_testcases = sorted(
                    completed_testcases,
                    key=lambda testcase: testcase["id"],
                )

            new_state["generated_testcases"] = generated_testcases
            if generated_testcases:
                issue_messages = self.generate_issue_messages(
                    code=new_state.get("code", ""),
                    executed_testcases=generated_testcases,
                )
                issue_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=issue_messages,
                    temperature=0.2,
                    max_tokens=1024,
                )
                issue_text = issue_response.choices[0].message.content
                logger.debug(
                    "GenerateTestcaseAgent issue analysis response preview: %s",
                    truncate_text(issue_text),
                )
                issue_parsed = safe_parse_json_response(issue_text)
                for issue_data in issue_parsed.get("logic_issues") or []:
                    issue = create_logic_issue(
                        issue=issue_data.get("issue", ""),
                        evidence=int(issue_data.get("evidence", -1)),
                        code_snippet=issue_data.get("code_snippet", ""),
                        location=issue_data.get("location"),
                    )
                    generated_logic_issues[issue["evidence"]] = issue

            new_state["logic_issues"] = generated_logic_issues
            logger.debug(
                "GenerateTestcaseAgent created %s generated testcases and %s logic issues",
                len(generated_testcases),
                len(generated_logic_issues),
            )
        except Exception:
            logger.exception("GenerateTestcaseAgent failed")
            new_state["generated_testcases"] = []
            new_state["logic_issues"] = {}

        logger.debug(
            "GenerateTestcaseAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
