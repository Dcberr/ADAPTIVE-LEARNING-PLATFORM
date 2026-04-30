# PatchExerciseRelationsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concept_slugs** | **List[str]** |  | [optional] 
**related_exercise_slugs** | **List[str]** |  | [optional] 

## Example

```python
from code_review_ai_client.models.patch_exercise_relations_request import PatchExerciseRelationsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchExerciseRelationsRequest from a JSON string
patch_exercise_relations_request_instance = PatchExerciseRelationsRequest.from_json(json)
# print the JSON string representation of the object
print(PatchExerciseRelationsRequest.to_json())

# convert the object into a dict
patch_exercise_relations_request_dict = patch_exercise_relations_request_instance.to_dict()
# create an instance of PatchExerciseRelationsRequest from a dict
patch_exercise_relations_request_from_dict = PatchExerciseRelationsRequest.from_dict(patch_exercise_relations_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


