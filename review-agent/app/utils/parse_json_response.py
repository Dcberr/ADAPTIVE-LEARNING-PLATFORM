import json
import re
from typing import Any, Dict


def safe_parse_json_response(response: str) -> Dict[str, Any]:
    """Try to parse response into dict if it contains JSON-like text."""
    try:
        return json.loads(response)
    except Exception:
        response_text = str(response).strip()

    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", response_text, re.DOTALL)
    if fenced_match:
        try:
            return json.loads(fenced_match.group(1))
        except Exception:
            pass

    json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass

    return {"raw": response_text}
