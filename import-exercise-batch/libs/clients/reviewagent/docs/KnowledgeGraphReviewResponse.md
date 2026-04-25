# KnowledgeGraphReviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**review** | [**ReviewRecord**](ReviewRecord.md) |  | 

## Example

```python
from reviewagent_client.models.knowledge_graph_review_response import KnowledgeGraphReviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphReviewResponse from a JSON string
knowledge_graph_review_response_instance = KnowledgeGraphReviewResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphReviewResponse.to_json())

# convert the object into a dict
knowledge_graph_review_response_dict = knowledge_graph_review_response_instance.to_dict()
# create an instance of KnowledgeGraphReviewResponse from a dict
knowledge_graph_review_response_from_dict = KnowledgeGraphReviewResponse.from_dict(knowledge_graph_review_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


