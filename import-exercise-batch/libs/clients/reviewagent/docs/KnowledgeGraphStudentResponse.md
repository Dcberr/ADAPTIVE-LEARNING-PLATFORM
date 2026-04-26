# KnowledgeGraphStudentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **str** |  | 
**student_profile** | [**StudentProfileScoring**](StudentProfileScoring.md) |  | 

## Example

```python
from reviewagent_client.models.knowledge_graph_student_response import KnowledgeGraphStudentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphStudentResponse from a JSON string
knowledge_graph_student_response_instance = KnowledgeGraphStudentResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphStudentResponse.to_json())

# convert the object into a dict
knowledge_graph_student_response_dict = knowledge_graph_student_response_instance.to_dict()
# create an instance of KnowledgeGraphStudentResponse from a dict
knowledge_graph_student_response_from_dict = KnowledgeGraphStudentResponse.from_dict(knowledge_graph_student_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


