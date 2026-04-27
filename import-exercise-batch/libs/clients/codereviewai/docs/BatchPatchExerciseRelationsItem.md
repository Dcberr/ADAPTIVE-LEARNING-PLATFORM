# BatchPatchExerciseRelationsItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concept_slugs** | **List[str]** |  | [optional] 
**related_exercise_ids** | **List[str]** |  | [optional] 
**related_exercise_slugs** | **List[str]** |  | [optional] 
**exercise_id** | **str** |  | 

## Example

```python
from code_review_ai_client.models.batch_patch_exercise_relations_item import BatchPatchExerciseRelationsItem

# TODO update the JSON string below
json = "{}"
# create an instance of BatchPatchExerciseRelationsItem from a JSON string
batch_patch_exercise_relations_item_instance = BatchPatchExerciseRelationsItem.from_json(json)
# print the JSON string representation of the object
print(BatchPatchExerciseRelationsItem.to_json())

# convert the object into a dict
batch_patch_exercise_relations_item_dict = batch_patch_exercise_relations_item_instance.to_dict()
# create an instance of BatchPatchExerciseRelationsItem from a dict
batch_patch_exercise_relations_item_from_dict = BatchPatchExerciseRelationsItem.from_dict(batch_patch_exercise_relations_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


