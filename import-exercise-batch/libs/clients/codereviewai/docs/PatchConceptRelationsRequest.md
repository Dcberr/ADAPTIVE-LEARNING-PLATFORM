# PatchConceptRelationsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prerequisite_slugs** | **List[str]** |  | [optional] 

## Example

```python
from code_review_ai_client.models.patch_concept_relations_request import PatchConceptRelationsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchConceptRelationsRequest from a JSON string
patch_concept_relations_request_instance = PatchConceptRelationsRequest.from_json(json)
# print the JSON string representation of the object
print(PatchConceptRelationsRequest.to_json())

# convert the object into a dict
patch_concept_relations_request_dict = patch_concept_relations_request_instance.to_dict()
# create an instance of PatchConceptRelationsRequest from a dict
patch_concept_relations_request_from_dict = PatchConceptRelationsRequest.from_dict(patch_concept_relations_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


