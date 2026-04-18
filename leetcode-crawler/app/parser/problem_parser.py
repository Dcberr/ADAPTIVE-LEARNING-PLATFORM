from bs4 import BeautifulSoup
import re
import json


def parse_problem(html):
    """
    Parse LeetCode problem HTML to extract content, examples, and constraints.
    Returns structured data optimized for database storage.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # ===== FULL CONTENT =====
    content = soup.get_text("\n").strip()

    # ===== EXAMPLES =====
    examples = _extract_examples(soup)

    # ===== CONSTRAINTS =====
    constraints = _extract_constraints_from_text(content)

    return {
        "content": content,
        "examples": examples,      # dict with example1, example2, etc.
        "constraints": constraints  # list of constraint strings
    }


def _extract_examples_from_text(text):
    """
    Extract examples from text using regex pattern matching.
    Looks for patterns like:
    Example 1:
    Input: ...
    Output: ...
    Explanation: ...
    """
    examples_dict = {}
    example_counter = 1
    
    # Split by "Example X:" to find all examples
    example_pattern = r"Example\s*\d+\s*:\s*(.*?)(?=Example\s*\d+\s*:|Constraints:|Follow-up:|$)"
    matches = re.finditer(example_pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        example_text = match.group(2).strip()
        example_data = _parse_single_example_from_text(example_text)
        
        if example_data:
            examples_dict[f"example{example_counter}"] = example_data
            example_counter += 1
    
    return examples_dict


def _parse_single_example_from_text(text):
    """Parse example text to extract Input, Output, and Explanation."""
    example = {}
    
    # Extract Input
    input_match = re.search(r"Input\s*:\s*(.*?)(?=\n\s*Output|$)", text, re.IGNORECASE | re.DOTALL)
    if input_match:
        example["input"] = input_match.group(1).strip()
    
    # Extract Output
    output_match = re.search(r"Output\s*:\s*(.*?)(?=\n\s*Explanation|$)", text, re.IGNORECASE | re.DOTALL)
    if output_match:
        example["output"] = output_match.group(1).strip()
    
    # Extract Explanation (optional)
    explanation_match = re.search(r"Explanation\s*:\s*(.*?)$", text, re.IGNORECASE | re.DOTALL)
    if explanation_match:
        expl_text = explanation_match.group(1).strip()
        if expl_text:
            example["explanation"] = expl_text
    
    return example if ("input" in example or "output" in example) else None


def _extract_constraints_from_text(text):
    """
    Extract constraints from text.
    Looks for text between "Constraints:" and next section.
    """
    constraints = []
    
    # Find Constraints section
    constraints_match = re.search(
        r"Constraints?\s*:\s*(.*?)(?=Follow-up|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    
    if constraints_match:
        constraints_text = constraints_match.group(1).strip()
        
        # Split by newlines and clean up
        for line in constraints_text.split("\n"):
            line = line.strip()
            # Remove empty lines and lines that are just numbers
            if line and len(line) > 3:
                # Clean up math notation (10^9 is harder to parse, keep as is)
                constraints.append(line)
    
    return constraints


def extract_description(content: str) -> str:
    # Tìm vị trí bắt đầu của các section không cần
    pattern = r"(Example\s*\d+:|Constraints:|Follow-up:)"
    
    match = re.search(pattern, content, re.IGNORECASE)
    
    if match:
        return content[:match.start()].strip()
    
    return content.strip()

def _extract_examples(soup):
    """Extract examples from HTML and return as dict with example1, example2, etc."""
    examples_dict = {}
    example_counter = 1
    
    # Try to find examples in <pre> tags (most reliable)
    for pre in soup.find_all("pre"):
        text = pre.get_text("\n").strip()
        
        # Check if this looks like an example (has Input/Output)
        if "Input" not in text and "Output" not in text:
            continue
        
        example_data = _parse_single_example(text)
        if example_data:
            examples_dict[f"example{example_counter}"] = example_data
            example_counter += 1
    
    return examples_dict


def _parse_single_example(text):
    """Parse a single example text block into structured format."""
    lines = text.split("\n")
    example = {}
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers
        if line.startswith("Input:"):
            current_section = "input"
            example["input"] = line.replace("Input:", "").strip()
        elif line.startswith("Output:"):
            current_section = "output"
            example["output"] = line.replace("Output:", "").strip()
        elif line.startswith("Explanation:"):
            current_section = "explanation"
            example["explanation"] = line.replace("Explanation:", "").strip()
        elif current_section and current_section in example:
            # Append to current section for multi-line values
            example[current_section] += " " + line
    
    return example if example else None


def _extract_constraints(soup):
    """Extract constraints and return as list of strings."""
    constraints = []
    
    # Strategy 1: Look for <strong>Constraints:</strong> or "Constraints:" text
    for strong in soup.find_all("strong"):
        if "Constraints" in strong.get_text():
            # Look for <ul> or <li> elements after this
            parent = strong.find_parent()
            
            # Find all <li> elements in the nearest <ul>
            ul = parent.find_next("ul") if parent else soup.find_next("ul")
            if ul:
                for li in ul.find_all("li"):
                    constraint_text = li.get_text().strip()
                    if constraint_text:
                        constraints.append(constraint_text)
                if constraints:
                    break
    
    # Strategy 2: If no constraints found, try to extract from text patterns
    if not constraints:
        text = soup.get_text("\n")
        # Find text between "Constraints:" and next section
        constraint_match = re.search(
            r"Constraints?\s*:?\s*(.*?)(?=Example|\n\n|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if constraint_match:
            constraint_text = constraint_match.group(1).strip()
            # Split by newline and filter empty lines
            for line in constraint_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("Example"):
                    constraints.append(line)
    
    return constraints if constraints else []