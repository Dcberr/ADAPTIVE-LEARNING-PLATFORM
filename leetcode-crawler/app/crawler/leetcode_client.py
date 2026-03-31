from leetscrape import GetQuestionsList, GetQuestion

class LeetCodeClient:

    def get_problems(self, limit=1):
        qs = GetQuestionsList(limit=limit)
        qs.scrape()
        return qs.questions

    def get_problem_detail(self, slug):
        q = GetQuestion(titleSlug=slug)
        return q.scrape()