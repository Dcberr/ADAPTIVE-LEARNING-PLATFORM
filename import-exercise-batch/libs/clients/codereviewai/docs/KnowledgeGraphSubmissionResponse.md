# KnowledgeGraphSubmissionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission** | [**SubmissionRecord**](SubmissionRecord.md) |  | 

## Example

```python
from code_review_ai_client.models.knowledge_graph_submission_response import KnowledgeGraphSubmissionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphSubmissionResponse from a JSON string
knowledge_graph_submission_response_instance = KnowledgeGraphSubmissionResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphSubmissionResponse.to_json())

# convert the object into a dict
knowledge_graph_submission_response_dict = knowledge_graph_submission_response_instance.to_dict()
# create an instance of KnowledgeGraphSubmissionResponse from a dict
knowledge_graph_submission_response_from_dict = KnowledgeGraphSubmissionResponse.from_dict(knowledge_graph_submission_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


