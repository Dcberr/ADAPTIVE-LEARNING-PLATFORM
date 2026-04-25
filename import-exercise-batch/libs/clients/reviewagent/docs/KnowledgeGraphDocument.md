# KnowledgeGraphDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concepts** | [**List[ConceptRecord]**](ConceptRecord.md) |  | [optional] 
**concept_relations** | [**List[ConceptRelation]**](ConceptRelation.md) |  | [optional] 
**exercises** | [**List[ExerciseRecord]**](ExerciseRecord.md) |  | [optional] 
**exercise_concept_links** | [**List[ExerciseConceptLink]**](ExerciseConceptLink.md) |  | [optional] 
**exercise_path_links** | [**List[ExercisePathLink]**](ExercisePathLink.md) |  | [optional] 
**exercise_relations** | [**List[ExerciseRelation]**](ExerciseRelation.md) |  | [optional] 
**students** | [**List[StudentRecord]**](StudentRecord.md) |  | [optional] 
**submissions** | [**List[SubmissionRecord]**](SubmissionRecord.md) |  | [optional] 
**submission_relations** | [**List[SubmissionRelation]**](SubmissionRelation.md) |  | [optional] 
**reviews** | [**List[ReviewRecord]**](ReviewRecord.md) |  | [optional] 
**review_relations** | [**List[ReviewRelation]**](ReviewRelation.md) |  | [optional] 

## Example

```python
from reviewagent_client.models.knowledge_graph_document import KnowledgeGraphDocument

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphDocument from a JSON string
knowledge_graph_document_instance = KnowledgeGraphDocument.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphDocument.to_json())

# convert the object into a dict
knowledge_graph_document_dict = knowledge_graph_document_instance.to_dict()
# create an instance of KnowledgeGraphDocument from a dict
knowledge_graph_document_from_dict = KnowledgeGraphDocument.from_dict(knowledge_graph_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


