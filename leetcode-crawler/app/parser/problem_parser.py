from bs4 import BeautifulSoup


def parse_problem(html):
    soup = BeautifulSoup(html, "html.parser")

    # ===== FULL CONTENT =====
    content = soup.get_text("\n").strip()

    # ===== EXAMPLES =====
    examples = []
    for pre in soup.find_all("pre"):
        text = pre.get_text("\n").strip()

        if "Input" not in text or "Output" not in text:
            continue

        data = {}
        current_key = None

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                continue

            # 🔥 robust match (không dùng startswith)
            if "Input:" in line:
                data["input"] = line.split("Input:")[-1].strip()
                current_key = "input"

            elif "Output:" in line:
                data["output"] = line.split("Output:")[-1].strip()
                current_key = "output"

            elif "Explanation:" in line:
                data["explanation"] = line.split("Explanation:")[-1].strip()
                current_key = "explanation"

            else:
                # multi-line continuation
                if current_key and current_key in data:
                    data[current_key] += " " + line

        if data:
            examples.append(data)

    # ===== CONSTRAINTS =====
    constraints_list = []

    for strong in soup.find_all("strong"):
        if "Constraints" in strong.get_text():
            parent = strong.find_parent()

            # 🔥 robust hơn: tìm ul gần nhất phía sau
            ul = parent.find_next("ul")

            if ul:
                for li in ul.find_all("li"):
                    text = li.get_text().strip()
                    if text:
                        constraints_list.append(text)

    # 👉 convert sang TEXT (backend-friendly)
    constraints_text = "\n".join(constraints_list)

    return {
        "content": content,
        "examples": examples,          # list[dict] → JSONB
        "constraints": constraints_text  # TEXT
    }