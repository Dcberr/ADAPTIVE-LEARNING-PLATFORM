from leetscrape import GetQuestionsList
import requests


class LeetCodeClient:

    def get_problems(self, limit=1):
        qs = GetQuestionsList(limit=limit)
        qs.scrape()
        return qs.questions

    def get_problem_detail(self, slug, lang="cpp"):
        query = {
            "query": """
            query getQuestion($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionFrontendId
                title
                titleSlug
                difficulty
                content
                hints
                topicTags { name }
                codeSnippets {
                  lang
                  langSlug
                  code
                }
                similarQuestions
                isPaidOnly
              }
            }
            """,
            "variables": {"titleSlug": slug},
        }

        res = requests.post("https://leetcode.com/graphql", json=query)

        if res.status_code != 200:
            raise Exception(f"GraphQL error: {res.status_code}")

        data = res.json()["data"]["question"]

        # ===== Extract code theo ngôn ngữ =====
        code = None
        for s in data["codeSnippets"]:
            if s["langSlug"] == lang:
                code = s["code"]
                break

        # fallback nếu không có cpp
        if code is None and data["codeSnippets"]:
            code = data["codeSnippets"][0]["code"]

        return {
            "QID": int(data["questionFrontendId"]),
            "title": data["title"],
            "titleSlug": data["titleSlug"],
            "difficulty": data["difficulty"],
            "content": data["content"],
            "hints": data["hints"],
            "topics": [t["name"] for t in data["topicTags"]],
            "similar": data["similarQuestions"],
            "is_paid": data["isPaidOnly"],
            "code": code
        }