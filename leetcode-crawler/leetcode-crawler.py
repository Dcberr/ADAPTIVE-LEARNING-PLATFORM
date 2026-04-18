from leetscrape import GetQuestionsList, GetQuestion

qs = GetQuestionsList(limit=1)
qs.scrape()

for _, row in qs.questions.iterrows():
    try:
        slug = row["titleSlug"]

        q = GetQuestion(titleSlug=slug)
        detail = q.scrape()

        print({
            "title": detail.Body.title(),
            "difficulty": detail.difficulty
        })

    except Exception as e:
        print("Error:", slug, e)