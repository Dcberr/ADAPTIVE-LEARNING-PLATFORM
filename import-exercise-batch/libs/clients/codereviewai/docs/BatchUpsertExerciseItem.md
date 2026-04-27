# BatchUpsertExerciseItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slug** | **str** |  | [optional] [default to '']
**title** | **str** |  | 
**description** | **str** |  | 
**content** | **str** |  | 
**difficulty** | **str** |  | 
**tags** | **List[str]** |  | [optional] 
**exercise_id** | **str** |  | 

## Example

```python
from code_review_ai_client.models.batch_upsert_exercise_item import BatchUpsertExerciseItem

# TODO update the JSON string below
json = "{}"
# create an instance of BatchUpsertExerciseItem from a JSON string
batch_upsert_exercise_item_instance = BatchUpsertExerciseItem.from_json(json)
# print the JSON string representation of the object
print(BatchUpsertExerciseItem.to_json())

# convert the object into a dict
batch_upsert_exercise_item_dict = batch_upsert_exercise_item_instance.to_dict()
# create an instance of BatchUpsertExerciseItem from a dict
batch_upsert_exercise_item_from_dict = BatchUpsertExerciseItem.from_dict(batch_upsert_exercise_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


