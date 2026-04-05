import logging
from typing import Any, Dict, List

from openai import OpenAI

from app.models.review_state import LogicIssue, ReviewState
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ConceptMappingAgent:
    """Maps logic issues to CS1 concepts using chat-based messages."""

    def __init__(self, client: OpenAI, model_name: str, batch_size: int = 5):
        self.client = client
        self.model_name = model_name
        self.batch_size = batch_size

    def chunk_issues(self, issues: Dict[str, LogicIssue]):
        """Split logic issues dict into batches."""
        if not issues:
            return

        issue_items = list(issues.items())
        batch_size = max(1, self.batch_size)

        for i in range(0, len(issue_items), batch_size):
            yield issue_items[i : i + batch_size]

    def format_issue(self, issue: LogicIssue) -> str:
        """Format a LogicIssue into a concise string for the prompt."""
        location_str = ""
        if "location" in issue and issue["location"]:
            loc = issue["location"]
            location_str = f" (line {loc.get('line')}, col {loc.get('col')})"

        return (
            f"Issue {issue['evidence']} | "
            f"Summary: {issue['issue']} | "
            f"Evidence (test case ID): {issue['evidence']} | "
            f"Code snippet: {issue['code_snippet']}{location_str}"
        )

    def generate_messages(
        self,
        issues_batch: List[LogicIssue],
        expected_concepts: List[str],
        assignment_requirements: str,
    ) -> List[dict]:
        """Return system + user messages for chat models with formatted issues."""
        system_msg = {
            "role": "system",
            "content": (
                "You are a concept-mapping agent for CS1 (intro to programming). "
                "Your job is to map each logic issue to CS1 concepts accurately. "
                "Always respond in valid JSON format."
            ),
        }

        # Format all issues in this batch
        formatted_issues = [self.format_issue(issue) for issue in issues_batch]
        formatted_issues_str = "\n".join(formatted_issues)

        user_msg_content = f"""
        Assignment requirements: {assignment_requirements}
        Expected concepts: {expected_concepts}

        Logic issues in this batch:
        {formatted_issues_str}

        Task:
        1. If the issue relates to an expected concept, append it to "relevant_concept".
        2. If the issue relates to other valid CS1 concepts, append it to "other_concept".
        3. Include issue reference "issue_ref" as the index in this batch.
        4. Provide a short explanation citing the evidence (test case ID and/or code snippet).

        Output JSON format:
        {{
            "concept_issues": [
                {{
                    "issue_ref": <index>,
                    "relevant_concept": ["concept1", ...],
                    "other_concept": ["conceptX", ...],
                    "explanation": "brief explanation"
                }}
            ]
        }}

        Notes:
        - Do NOT invent new failing cases.
        - Keep JSON valid.
        """
        user_msg = {"role": "user", "content": user_msg_content}

        return [system_msg, user_msg]

    def analyze(self, state: ReviewState) -> ReviewState:
        """Run concept mapping analysis on a submission state with batching and update original issues."""
        logger.debug(
            "Starting ConceptMappingAgent with state summary: %s",
            summarize_state(state),
        )
        new_state: ReviewState = dict(state)

        logic_issues: Dict[str, LogicIssue] = new_state.get("logic_issues", {})
        expected_concepts: List[str] = new_state.get("expected_concepts", [])
        assignment_req: str = new_state.get("assignment_requirements", "")

        all_concept_issues: List[Dict[str, Any]] = []

        for batch_index, batch_items in enumerate(
            self.chunk_issues(logic_issues) or [], start=1
        ):
            batch = dict(batch_items)
            batch_issue_list = [issue for _, issue in batch_items]
            logger.debug(
                "ConceptMappingAgent processing batch %s for issue ids=%s",
                batch_index,
                list(batch.keys()),
            )
            messages = self.generate_messages(
                batch_issue_list, expected_concepts, assignment_req
            )

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2048,
                )
                model_text = response.choices[0].message.content
                logger.debug(
                    "ConceptMappingAgent batch %s raw response preview: %s",
                    batch_index,
                    truncate_text(model_text),
                )
                parsed = safe_parse_json_response(model_text)

                concept_issues = parsed.get("concept_issues", [])
                logger.debug(
                    "ConceptMappingAgent batch %s parsed %s concept mappings",
                    batch_index,
                    len(concept_issues),
                )
                for ci in concept_issues:
                    issue_ref = ci.get("issue_ref")
                    if not isinstance(issue_ref, int):
                        continue
                    if issue_ref < 0 or issue_ref >= len(batch_items):
                        continue

                    original_issue = batch_items[issue_ref][1]
                    original_issue["relevant_concept"].extend(
                        ci.get("relevant_concept", [])
                    )
                    original_issue["other_concept"].extend(ci.get("other_concept", []))

                    all_concept_issues.append(ci)

            except Exception as e:
                logger.exception("ConceptMappingAgent batch %s failed", batch_index)
                for issue_ref, issue in batch.items():
                    issue["relevant_concept"] = []
                    issue["other_concept"] = []
                    all_concept_issues.append(
                        {
                            "issue_ref": issue_ref,
                            "relevant_concept": [],
                            "other_concept": [],
                            "explanation": "Error processing batch",
                        }
                    )

        # Update the state with enriched issues
        new_state["logic_issues"] = logic_issues  # dict updated in-place
        new_state["concept_issues"] = all_concept_issues
        logger.debug(
            "ConceptMappingAgent completed with %s concept issue records",
            len(new_state["concept_issues"]),
        )
        return new_state
