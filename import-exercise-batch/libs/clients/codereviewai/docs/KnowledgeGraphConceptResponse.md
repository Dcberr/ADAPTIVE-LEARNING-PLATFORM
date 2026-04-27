# KnowledgeGraphConceptResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concept** | [**ConceptRecord**](ConceptRecord.md) |  | 

## Example

```python
from code_review_ai_client.models.knowledge_graph_concept_response import KnowledgeGraphConceptResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphConceptResponse from a JSON string
knowledge_graph_concept_response_instance = KnowledgeGraphConceptResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphConceptResponse.to_json())

# convert the object into a dict
knowledge_graph_concept_response_dict = knowledge_graph_concept_response_instance.to_dict()
# create an instance of KnowledgeGraphConceptResponse from a dict
knowledge_graph_concept_response_from_dict = KnowledgeGraphConceptResponse.from_dict(knowledge_graph_concept_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


