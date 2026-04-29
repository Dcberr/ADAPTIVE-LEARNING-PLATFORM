# ExerciseRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise_id** | **str** |  | 
**slug** | **str** |  | [optional] [default to '']
**title** | **str** |  | 
**description** | **str** |  | 
**content** | **str** |  | 
**difficulty** | **str** |  | 
**concept_slugs** | **List[str]** |  | [optional] 

## Example

```python
from code_review_ai_client.models.exercise_record import ExerciseRecord

# TODO update the JSON string below
json = "{}"
# create an instance of ExerciseRecord from a JSON string
exercise_record_instance = ExerciseRecord.from_json(json)
# print the JSON string representation of the object
print(ExerciseRecord.to_json())

# convert the object into a dict
exercise_record_dict = exercise_record_instance.to_dict()
# create an instance of ExerciseRecord from a dict
exercise_record_from_dict = ExerciseRecord.from_dict(exercise_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


