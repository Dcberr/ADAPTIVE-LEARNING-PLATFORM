# KnowledgeGraphSnapshotResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**graph** | [**KnowledgeGraphDocument**](KnowledgeGraphDocument.md) |  | 

## Example

```python
from reviewagent_client.models.knowledge_graph_snapshot_response import KnowledgeGraphSnapshotResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KnowledgeGraphSnapshotResponse from a JSON string
knowledge_graph_snapshot_response_instance = KnowledgeGraphSnapshotResponse.from_json(json)
# print the JSON string representation of the object
print(KnowledgeGraphSnapshotResponse.to_json())

# convert the object into a dict
knowledge_graph_snapshot_response_dict = knowledge_graph_snapshot_response_instance.to_dict()
# create an instance of KnowledgeGraphSnapshotResponse from a dict
knowledge_graph_snapshot_response_from_dict = KnowledgeGraphSnapshotResponse.from_dict(knowledge_graph_snapshot_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


