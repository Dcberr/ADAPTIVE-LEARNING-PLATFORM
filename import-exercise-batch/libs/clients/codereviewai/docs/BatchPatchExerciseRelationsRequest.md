# BatchPatchExerciseRelationsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercises** | [**List[BatchPatchExerciseRelationsItem]**](BatchPatchExerciseRelationsItem.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.batch_patch_exercise_relations_request import BatchPatchExerciseRelationsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BatchPatchExerciseRelationsRequest from a JSON string
batch_patch_exercise_relations_request_instance = BatchPatchExerciseRelationsRequest.from_json(json)
# print the JSON string representation of the object
print(BatchPatchExerciseRelationsRequest.to_json())

# convert the object into a dict
batch_patch_exercise_relations_request_dict = batch_patch_exercise_relations_request_instance.to_dict()
# create an instance of BatchPatchExerciseRelationsRequest from a dict
batch_patch_exercise_relations_request_from_dict = BatchPatchExerciseRelationsRequest.from_dict(batch_patch_exercise_relations_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


