# BatchUpsertExercisesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercises** | [**List[BatchUpsertExerciseItem]**](BatchUpsertExerciseItem.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.batch_upsert_exercises_request import BatchUpsertExercisesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BatchUpsertExercisesRequest from a JSON string
batch_upsert_exercises_request_instance = BatchUpsertExercisesRequest.from_json(json)
# print the JSON string representation of the object
print(BatchUpsertExercisesRequest.to_json())

# convert the object into a dict
batch_upsert_exercises_request_dict = batch_upsert_exercises_request_instance.to_dict()
# create an instance of BatchUpsertExercisesRequest from a dict
batch_upsert_exercises_request_from_dict = BatchUpsertExercisesRequest.from_dict(batch_upsert_exercises_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


