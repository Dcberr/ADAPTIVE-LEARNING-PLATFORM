# UpsertExerciseRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slug** | **str** |  | [optional] [default to '']
**title** | **str** |  | 
**description** | **str** |  | 
**content** | **str** |  | 
**difficulty** | **str** |  | 
**concept_slugs** | **List[str]** |  | [optional] 

## Example

```python
from code_review_ai_client.models.upsert_exercise_request import UpsertExerciseRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertExerciseRequest from a JSON string
upsert_exercise_request_instance = UpsertExerciseRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertExerciseRequest.to_json())

# convert the object into a dict
upsert_exercise_request_dict = upsert_exercise_request_instance.to_dict()
# create an instance of UpsertExerciseRequest from a dict
upsert_exercise_request_from_dict = UpsertExerciseRequest.from_dict(upsert_exercise_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


