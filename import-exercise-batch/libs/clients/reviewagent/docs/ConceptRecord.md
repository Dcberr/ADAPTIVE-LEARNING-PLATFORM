# ConceptRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concept_id** | **str** |  | 
**slug** | **str** |  | [optional] [default to '']
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**difficulty** | **int** |  | [optional] [default to 1]

## Example

```python
from reviewagent_client.models.concept_record import ConceptRecord

# TODO update the JSON string below
json = "{}"
# create an instance of ConceptRecord from a JSON string
concept_record_instance = ConceptRecord.from_json(json)
# print the JSON string representation of the object
print(ConceptRecord.to_json())

# convert the object into a dict
concept_record_dict = concept_record_instance.to_dict()
# create an instance of ConceptRecord from a dict
concept_record_from_dict = ConceptRecord.from_dict(concept_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


