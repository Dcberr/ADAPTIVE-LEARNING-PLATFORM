# KnowledgeGraphExerciseResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise** | [**ExerciseRecord**](ExerciseRecord.md) |  | 

## Example

```python
from reviewagent_client.models.knowledge_graph_exercise_response import KnowledgeGraphExerciseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphExerciseResponse from a JSON string
knowledge_graph_exercise_response_instance = KnowledgeGraphExerciseResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphExerciseResponse.to_json())

# convert the object into a dict
knowledge_graph_exercise_response_dict = knowledge_graph_exercise_response_instance.to_dict()
# create an instance of KnowledgeGraphExerciseResponse from a dict
knowledge_graph_exercise_response_from_dict = KnowledgeGraphExerciseResponse.from_dict(knowledge_graph_exercise_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


