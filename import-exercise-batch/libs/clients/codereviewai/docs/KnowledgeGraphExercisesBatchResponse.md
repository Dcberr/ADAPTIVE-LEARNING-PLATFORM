# KnowledgeGraphExercisesBatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercises** | [**List[ExerciseRecord]**](ExerciseRecord.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.knowledge_graph_exercises_batch_response import KnowledgeGraphExercisesBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphExercisesBatchResponse from a JSON string
knowledge_graph_exercises_batch_response_instance = KnowledgeGraphExercisesBatchResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphExercisesBatchResponse.to_json())

# convert the object into a dict
knowledge_graph_exercises_batch_response_dict = knowledge_graph_exercises_batch_response_instance.to_dict()
# create an instance of KnowledgeGraphExercisesBatchResponse from a dict
knowledge_graph_exercises_batch_response_from_dict = KnowledgeGraphExercisesBatchResponse.from_dict(knowledge_graph_exercises_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


