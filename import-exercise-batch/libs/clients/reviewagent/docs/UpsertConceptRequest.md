# UpsertConceptRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**difficulty** | **int** |  | [optional] [default to 1]

## Example

```python
from reviewagent_client.models.upsert_concept_request import UpsertConceptRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertConceptRequest from a JSON string
upsert_concept_request_instance = UpsertConceptRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertConceptRequest.to_json())

# convert the object into a dict
upsert_concept_request_dict = upsert_concept_request_instance.to_dict()
# create an instance of UpsertConceptRequest from a dict
upsert_concept_request_from_dict = UpsertConceptRequest.from_dict(upsert_concept_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


